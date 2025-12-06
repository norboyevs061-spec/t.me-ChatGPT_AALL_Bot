"""
Chat Service - Text Q&A
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import db_manager
from locales import get_text
from utils.keyboards import get_main_menu_keyboard
from utils.decorators import rate_limit 
import config

# Conversation states
WAITING_QUESTION = 1

class ChatService:
    """Chat Q&A service"""
    
    @staticmethod
    @rate_limit("chat") # Premium limitlariga asoslangan cheklov qo'llaniladi
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start chat service"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        await update.message.reply_text(
            get_text(language, "chat_start")
        )
        
        return WAITING_QUESTION
    
    @staticmethod
    async def process_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process user question"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        question = update.message.text
        
        # Check for back button
        if question == get_text(language, "back"):
            await update.message.reply_text(
                get_text(language, "main_menu"),
                reply_markup=get_main_menu_keyboard(language)
            )
            return ConversationHandler.END
        
        # Show processing message
        await update.message.reply_text(get_text(language, "processing"))
        
        # Log request
        await db_manager.log_request(
            user.id, 
            "chat", 
            {"question": question},
            "success"
        )
        
        # AI API integration point
        response = await ChatService.integrate_ai_api(question, language)
        
        # Send response
        await update.message.reply_text(
            get_text(language, "chat_response", response=response),
            reply_markup=get_main_menu_keyboard(language)
        )
        
        return ConversationHandler.END
    
    @staticmethod
    async def integrate_ai_api(question: str, language: str) -> str:
        """
        AI API integration point for chat
        """
        # Placeholder response
        return f"[AI Response Placeholder]\n\nYour question: {question}\n\nTo integrate real AI, add your API key to config.py and implement the API call in the integrate_ai_api method."
    
    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel chat conversation"""
        user = update.effective_user
        language = await db_manager.get_user_language(user.id)
        
        await update.message.reply_text(
            get_text(language, "main_menu"),
            reply_markup=get_main_menu_keyboard(language)
        )
        
        return ConversationHandler.END
