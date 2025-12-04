"""
Translation Service
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db_manager
from locales import get_text
from utils.keyboards import get_main_menu_keyboard, get_translation_language_keyboard
from utils.decorators import rate_limit
import config

# Conversation states
WAITING_TEXT, SELECTING_SOURCE, SELECTING_TARGET = range(3)

class TranslationService:
    """Translation service"""
    
    @staticmethod
    @rate_limit("translation")
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start translation service"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        await update.message.reply_text(
            get_text(language, "translation_start")
        )
        
        return WAITING_TEXT
    
    @staticmethod
    async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive text to translate"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        text = update.message.text
        
        # Check for back button
        if text == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "main_menu"),
                reply_markup=get_main_menu_keyboard(language)
            )
            return ConversationHandler.END
        
        # Store text in context
        context.user_data['translation_text'] = text
        
        # Ask for source language
        await update.message.reply_text(
            get_text(language, "translation_select_source"),
            reply_markup=get_translation_language_keyboard(language)
        )
        
        return SELECTING_SOURCE
    
    @staticmethod
    async def select_source_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select source language"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        source_lang = update.message.text
        
        # Check for back button
        if source_lang == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "translation_start")
            )
            return WAITING_TEXT
        
        # Store source language
        context.user_data['source_language'] = source_lang
        
        # Ask for target language
        await update.message.reply_text(
            get_text(language, "translation_select_target"),
            reply_markup=get_translation_language_keyboard(language)
        )
        
        return SELECTING_TARGET
    
    @staticmethod
    async def select_target_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select target language and process translation"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        target_lang = update.message.text
        
        # Check for back button
        if target_lang == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "translation_select_source"),
                reply_markup=get_translation_language_keyboard(language)
            )
            return SELECTING_SOURCE
        
        # Get stored data
        text = context.user_data.get('translation_text', '')
        source_lang = context.user_data.get('source_language', '')
        
        # Show processing message
        await update.message.reply_text(get_text(language, "processing"))
        
        # Log request
        await db_manager.log_request(
            user.id,
            "translation",
            {
                "text": text,
                "source": source_lang,
                "target": target_lang
            },
            "success"
        )
        
        # AI API integration point
        translation = await TranslationService.integrate_ai_api(
            text, source_lang, target_lang, language
        )
        
        # Send translation
        await update.message.reply_text(
            get_text(language, "translation_result", translation=translation),
            reply_markup=get_main_menu_keyboard(language)
        )
        
        # Clear context data
        context.user_data.clear()
        
        return ConversationHandler.END
    
    @staticmethod
    async def integrate_ai_api(text: str, source_lang: str, target_lang: str, ui_language: str) -> str:
        """
        AI API integration point for translation
        
        TODO: Integrate with OpenAI, DeepL, or Google Translate API
        
        Example integration with OpenAI:
        ```
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": f"Translate the following text from {source_lang} to {target_lang}. Only provide the translation, no explanations."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
        ```
        """
        # Placeholder translation
        return f"[Translation Placeholder]\n\nOriginal ({source_lang}): {text}\n\nTranslated to {target_lang}: [Add API integration here]"
    
    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel translation conversation"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        context.user_data.clear()
        
        await update.message.reply_text(
            get_text(language, "main_menu"),
            reply_markup=get_main_menu_keyboard(language)
        )
        
        return ConversationHandler.END
