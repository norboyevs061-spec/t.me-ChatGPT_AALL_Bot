"""
Voice & Music Service - Text-to-speech and music generation
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db_manager
from locales import get_text
from utils.keyboards import (get_main_menu_keyboard, get_voice_mode_keyboard,
                             get_voice_style_keyboard, get_voice_language_keyboard,
                             get_music_style_keyboard)
from utils.decorators import rate_limit
import config

# Conversation states
SELECTING_MODE, ENTERING_TEXT, SELECTING_VOICE_STYLE, SELECTING_VOICE_LANG = range(4, 8)
ENTERING_MUSIC_PROMPT, SELECTING_MUSIC_STYLE = range(8, 10)

class VoiceMusicService:
    """Voice and music service"""
    
    @staticmethod
    @rate_limit("voice_music")
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start voice & music service"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        await update.message.reply_text(
            get_text(language, "voice_start")
        )
        
        await update.message.reply_text(
            get_text(language, "voice_select_mode"),
            reply_markup=get_voice_mode_keyboard(language)
        )
        
        return SELECTING_MODE
    
    @staticmethod
    async def select_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select mode (TTS or Music)"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        mode = update.message.text
        
        # Check for back button
        if mode == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "main_menu"),
                reply_markup=get_main_menu_keyboard(language)
            )
            return ConversationHandler.END
        
        # Store mode
        context.user_data['voice_mode'] = mode
        
        # Route based on mode
        if mode == get_text(language, "voice_mode_tts"):
            await update.message.reply_text(
                get_text(language, "voice_enter_text")
            )
            return ENTERING_TEXT
        else:  # Music generation
            await update.message.reply_text(
                get_text(language, "music_enter_prompt")
            )
            return ENTERING_MUSIC_PROMPT
    
    # Text-to-Speech flow
    @staticmethod
    async def enter_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enter text for TTS"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        text = update.message.text
        
        # Check for back button
        if text == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "voice_select_mode"),
                reply_markup=get_voice_mode_keyboard(language)
            )
            return SELECTING_MODE
        
        # Store text
        context.user_data['voice_text'] = text
        
        # Ask for voice style
        await update.message.reply_text(
            get_text(language, "voice_select_style"),
            reply_markup=get_voice_style_keyboard(language)
        )
        
        return SELECTING_VOICE_STYLE
    
    @staticmethod
    async def select_voice_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select voice style"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        style = update.message.text
        
        # Check for back button
        if style == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "voice_enter_text")
            )
            return ENTERING_TEXT
        
        # Store style
        context.user_data['voice_style'] = style
        
        # Ask for language
        await update.message.reply_text(
            get_text(language, "voice_select_language"),
            reply_markup=get_voice_language_keyboard(language)
        )
        
        return SELECTING_VOICE_LANG
    
    @staticmethod
    async def select_voice_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select voice language and generate TTS"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        voice_lang = update.message.text
        
        # Check for back button
        if voice_lang == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "voice_select_style"),
                reply_markup=get_voice_style_keyboard(language)
            )
            return SELECTING_VOICE_STYLE
        
        # Get stored data
        text = context.user_data.get('voice_text', '')
        style = context.user_data.get('voice_style', '')
        
        # Show processing message
        await update.message.reply_text(get_text(language, "voice_processing"))
        
        # Log request
        await db_manager.log_request(
            user.id,
            "voice_music",
            {
                "mode": "tts",
                "text": text,
                "style": style,
                "language": voice_lang
            },
            "success"
        )
        
        # AI API integration point
        audio_result = await VoiceMusicService.integrate_tts_api(
            text, style, voice_lang, language
        )
        
        # Send result
        await update.message.reply_text(
            get_text(language, "voice_result") + f"\n\n{audio_result}",
            reply_markup=get_main_menu_keyboard(language)
        )
        
        # Clear context data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    # Music Generation flow
    @staticmethod
    async def enter_music_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enter music prompt"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        prompt = update.message.text
        
        # Check for back button
        if prompt == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "voice_select_mode"),
                reply_markup=get_voice_mode_keyboard(language)
            )
            return SELECTING_MODE
        
        # Store prompt
        context.user_data['music_prompt'] = prompt
        
        # Ask for music style
        await update.message.reply_text(
            get_text(language, "music_select_style"),
            reply_markup=get_music_style_keyboard(language)
        )
        
        return SELECTING_MUSIC_STYLE
    
    @staticmethod
    async def select_music_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select music style and generate music"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        style = update.message.text
        
        # Check for back button
        if style == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "music_enter_prompt")
            )
            return ENTERING_MUSIC_PROMPT
        
        # Get stored data
        prompt = context.user_data.get('music_prompt', '')
        
        # Show processing message
        await update.message.reply_text(get_text(language, "voice_processing"))
        
        # Log request
        await db_manager.log_request(
            user.id,
            "voice_music",
            {
                "mode": "music",
                "prompt": prompt,
                "style": style
            },
            "success"
        )
        
        # AI API integration point
        music_result = await VoiceMusicService.integrate_music_api(
            prompt, style, language
        )
        
        # Send result
        await update.message.reply_text(
            get_text(language, "voice_result") + f"\n\n{music_result}",
            reply_markup=get_main_menu_keyboard(language)
        )
        
        # Clear context data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    @staticmethod
    async def integrate_tts_api(text: str, style: str, voice_lang: str, ui_language: str) -> str:
        """
        AI API integration point for text-to-speech
        
        TODO: Integrate with ElevenLabs, OpenAI TTS, or other TTS API
        
        Example integration with OpenAI TTS:
        ```
        from openai import OpenAI
        from pathlib import Path
        
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Map style to voice
            input=text
        )
        
        # Save audio file
        speech_file = Path("speech.mp3")
        response.stream_to_file(speech_file)
        
        return str(speech_file)
        ```
        """
        # Placeholder result
        return f"[TTS Placeholder]\n\nText: {text}\nStyle: {style}\nLanguage: {voice_lang}\n\n[Add API integration here to generate actual audio]"
    
    @staticmethod
    async def integrate_music_api(prompt: str, style: str, language: str) -> str:
        """
        AI API integration point for music generation
        
        TODO: Integrate with Suno, MusicGen, or other music generation API
        
        Example integration with Suno (hypothetical):
        ```
        import requests
        
        url = "https://api.suno.ai/v1/generate"
        headers = {
            "Authorization": f"Bearer {config.SUNO_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "style": style,
            "duration": 30
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        return result.get("audio_url", "Music generation in progress")
        ```
        """
        # Placeholder result
        return f"[Music Generation Placeholder]\n\nPrompt: {prompt}\nStyle: {style}\n\n[Add API integration here to generate actual music]"
    
    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel voice & music conversation"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        context.user_data.clear()
        
        await update.message.reply_text(
            get_text(language, "main_menu"),
            reply_markup=get_main_menu_keyboard(language)
        )
        
        return ConversationHandler.END
