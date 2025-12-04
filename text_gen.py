"""
Text Generation Service - Blogs, emails, scenarios
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db_manager
from locales import get_text
from utils.keyboards import (get_main_menu_keyboard, get_text_type_keyboard,
                             get_text_length_keyboard, get_text_tone_keyboard)
from utils.decorators import rate_limit
import config

# Conversation states
SELECTING_TYPE, ENTERING_TOPIC, SELECTING_LENGTH, SELECTING_TONE = range(4)

class TextGenerationService:
    """Text generation service"""
    
    @staticmethod
    @rate_limit("text_generation")
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start text generation service"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        await update.message.reply_text(
            get_text(language, "textgen_start")
        )
        
        await update.message.reply_text(
            get_text(language, "textgen_select_type"),
            reply_markup=get_text_type_keyboard(language)
        )
        
        return SELECTING_TYPE
    
    @staticmethod
    async def select_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select content type"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        content_type = update.message.text
        
        # Check for back button
        if content_type == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "main_menu"),
                reply_markup=get_main_menu_keyboard(language)
            )
            return ConversationHandler.END
        
        # Store content type
        context.user_data['content_type'] = content_type
        
        # Ask for topic
        await update.message.reply_text(
            get_text(language, "textgen_enter_topic")
        )
        
        return ENTERING_TOPIC
    
    @staticmethod
    async def enter_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enter topic"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        topic = update.message.text
        
        # Check for back button
        if topic == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "textgen_select_type"),
                reply_markup=get_text_type_keyboard(language)
            )
            return SELECTING_TYPE
        
        # Store topic
        context.user_data['topic'] = topic
        
        # Ask for length
        await update.message.reply_text(
            get_text(language, "textgen_select_length"),
            reply_markup=get_text_length_keyboard(language)
        )
        
        return SELECTING_LENGTH
    
    @staticmethod
    async def select_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select text length"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        length = update.message.text
        
        # Check for back button
        if length == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "textgen_enter_topic")
            )
            return ENTERING_TOPIC
        
        # Store length
        context.user_data['length'] = length
        
        # Ask for tone
        await update.message.reply_text(
            get_text(language, "textgen_select_tone"),
            reply_markup=get_text_tone_keyboard(language)
        )
        
        return SELECTING_TONE
    
    @staticmethod
    async def select_tone(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select tone and generate text"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        tone = update.message.text
        
        # Check for back button
        if tone == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "textgen_select_length"),
                reply_markup=get_text_length_keyboard(language)
            )
            return SELECTING_LENGTH
        
        # Get stored data
        content_type = context.user_data.get('content_type', '')
        topic = context.user_data.get('topic', '')
        length = context.user_data.get('length', '')
        
        # Show processing message
        await update.message.reply_text(get_text(language, "processing"))
        
        # Log request
        await db_manager.log_request(
            user.id,
            "text_generation",
            {
                "type": content_type,
                "topic": topic,
                "length": length,
                "tone": tone
            },
            "success"
        )
        
        # AI API integration point
        generated_text = await TextGenerationService.integrate_ai_api(
            content_type, topic, length, tone, language
        )
        
        # Send generated text
        await update.message.reply_text(
            get_text(language, "textgen_result", text=generated_text),
            reply_markup=get_main_menu_keyboard(language)
        )
        
        # Clear context data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    @staticmethod
    async def integrate_ai_api(content_type: str, topic: str, length: str, tone: str, language: str) -> str:
        """
        AI API integration point for text generation
        
        TODO: Integrate with OpenAI GPT, Claude, or other LLM API
        
        Example integration with OpenAI:
        ```
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        prompt = f"Write a {content_type} about {topic}. Length: {length}. Tone: {tone}. Language: {language}"
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a professional content writer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
        ```
        """
        # Placeholder text
        return f"[Generated Text Placeholder]\n\nType: {content_type}\nTopic: {topic}\nLength: {length}\nTone: {tone}\n\n[Add API integration here to generate actual content]"
    
    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel text generation conversation"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        context.user_data.clear()
        
        await update.message.reply_text(
            get_text(language, "main_menu"),
            reply_markup=get_main_menu_keyboard(language)
        )
        
        return ConversationHandler.END
