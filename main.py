"""
Main bot file - Entry point for Telegram AI Bot
"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)

import config
from database import db_manager
from locales import get_text
from utils.keyboards import get_language_keyboard, get_main_menu_keyboard
from services import (
    ChatService,
    TranslationService,
    TextGenerationService,
    VideoCreationService,
    ImageGenerationService,
    VoiceMusicService,
    PremiumService
)
from admin import AdminPanel

# Import conversation states
from services.chat import WAITING_QUESTION
from services.translation import WAITING_TEXT, SELECTING_SOURCE, SELECTING_TARGET
from services.text_gen import SELECTING_TYPE, ENTERING_TOPIC, SELECTING_LENGTH, SELECTING_TONE
from services.video_gen import (
    ENTERING_DESCRIPTION as VIDEO_DESCRIPTION,
    SELECTING_LENGTH as VIDEO_LENGTH,
    SELECTING_STYLE as VIDEO_STYLE,
    SELECTING_RATIO
)
from services.image_gen import (
    ENTERING_PROMPT,
    SELECTING_SIZE,
    SELECTING_STYLE as IMAGE_STYLE,
    SELECTING_QUANTITY
)
from services.voice_music import (
    SELECTING_MODE,
    ENTERING_TEXT as VOICE_TEXT,
    SELECTING_VOICE_STYLE,
    SELECTING_VOICE_LANG,
    ENTERING_MUSIC_PROMPT,
    SELECTING_MUSIC_STYLE
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Command handlers
async def start_command(update: Update, context):
    """Handle /start command"""
    user = update.effective_user
    
    # Create or get user
    await db_manager.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Check if user has language preference
    language = await db_manager.get_user_language(user.id)
    
    if not language or language == 'ru':
        # Show language selection
        await update.message.reply_text(
            "👋 Salom! / Здравствуйте!\n\nTilni tanlang / Выберите язык:",
            reply_markup=get_language_keyboard()
        )
    else:
        # Show main menu
        await update.message.reply_text(
            get_text(language, "main_menu"),
            reply_markup=get_main_menu_keyboard(language)
        )


async def help_command(update: Update, context):
    """Handle /help command"""
    user = update.effective_user
    language = await db_manager.get_user_language(user.id)
    
    help_text = """
🤖 Telegram AI Bot Help

Available Services:
💬 Chat - Ask questions and get AI responses
🌐 Translation - Translate text between languages
📝 Text Generation - Generate blogs, emails, scenarios
🎬 Video Creation - Create AI-generated videos
🎨 Image Generation - Generate AI images
🎵 Voice & Music - Text-to-speech and music generation
⭐ Premium - Unlimited requests and bonuses

Commands:
/start - Start the bot
/help - Show this help message
/stats - Show your usage statistics
/language - Change language

Admin Commands (admin only):
/admin_stats - Show bot statistics
/grant_premium <user_id> <days> - Grant premium
/revoke_premium <user_id> - Revoke premium
/list_users [limit] - List recent users
/broadcast <message> - Send message to all users
"""
    
    await update.message.reply_text(help_text)


async def stats_command(update: Update, context):
    """Handle /stats command - show user statistics"""
    user = update.effective_user
    language = await db_manager.get_user_language(user.id)
    
    # Get user's service usage
    async with db_manager.async_session() as session:
        from sqlalchemy import select, func
        from database.models import User, ServiceUsage
        
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        user_obj = result.scalar_one_or_none()
        
        if not user_obj:
            await update.message.reply_text(get_text(language, "error"))
            return
        
        # Get service usage
        result = await session.execute(
            select(ServiceUsage).where(ServiceUsage.user_id == user_obj.id)
        )
        usage_records = result.scalars().all()
    
    # Format statistics
    stats_text = f"📊 Your Statistics\n\n"
    stats_text += f"Premium Status: {'✅ Active' if user_obj.is_premium else '❌ Inactive'}\n"
    stats_text += f"Member Since: {user_obj.created_at.strftime('%Y-%m-%d')}\n\n"
    stats_text += f"Service Usage:\n"
    
    if usage_records:
        for usage in usage_records:
            stats_text += f"  • {usage.service_name}: {usage.request_count} requests\n"
    else:
        stats_text += "  No usage yet\n"
    
    await update.message.reply_text(stats_text)


async def language_command(update: Update, context):
    """Handle /language command - change language"""
    await update.message.reply_text(
        "Tilni tanlang / Выберите язык:",
        reply_markup=get_language_keyboard()
    )


# Callback query handler for language selection
async def language_callback(update: Update, context):
    """Handle language selection callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    language_code = query.data.split('_')[1]  # Extract 'uz' or 'ru' from 'lang_uz'
    
    # Set user language
    await db_manager.set_user_language(user.id, language_code)
    
    # Show confirmation and main menu
    await query.message.reply_text(
        get_text(language_code, "language_selected")
    )
    await query.message.reply_text(
        get_text(language_code, "main_menu"),
        reply_markup=get_main_menu_keyboard(language_code)
    )


# Message router for main menu
async def handle_main_menu(update: Update, context):
    """Route messages from main menu to appropriate service"""
    user = update.effective_user
    language = await db_manager.get_user_language(user.id)
    message_text = update.message.text
    
    # Route to services
    if message_text == get_text(language, "service_chat"):
        return await ChatService.start(update, context)
    elif message_text == get_text(language, "service_translation"):
        return await TranslationService.start(update, context)
    elif message_text == get_text(language, "service_text_gen"):
        return await TextGenerationService.start(update, context)
    elif message_text == get_text(language, "service_video"):
        return await VideoCreationService.start(update, context)
    elif message_text == get_text(language, "service_image"):
        return await ImageGenerationService.start(update, context)
    elif message_text == get_text(language, "service_voice"):
        return await VoiceMusicService.start(update, context)
    elif message_text == get_text(language, "service_premium"):
        return await PremiumService.show_info(update, context)
    else:
        # Unknown command
        await update.message.reply_text(
            get_text(language, "main_menu"),
            reply_markup=get_main_menu_keyboard(language)
        )


def main():
    """Start the bot"""
    # Initialize database
    import asyncio
    asyncio.run(db_manager.init_db())
    
    # Create application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("language", language_command))
    
    # Admin command handlers
    application.add_handler(CommandHandler("admin_stats", AdminPanel.show_stats))
    application.add_handler(CommandHandler("grant_premium", AdminPanel.grant_premium))
    application.add_handler(CommandHandler("revoke_premium", AdminPanel.revoke_premium))
    application.add_handler(CommandHandler("list_users", AdminPanel.list_users))
    application.add_handler(CommandHandler("broadcast", AdminPanel.broadcast))
    
    # Language selection callback
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    
    # Chat service conversation handler
    chat_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
        states={
            WAITING_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ChatService.process_question)]
        },
        fallbacks=[CommandHandler("start", start_command)],
        name="chat_conversation",
        persistent=False,
        allow_reentry=True
    )
    
    # Translation service conversation handler
    translation_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
        states={
            WAITING_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, TranslationService.receive_text)],
            SELECTING_SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, TranslationService.select_source_language)],
            SELECTING_TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, TranslationService.select_target_language)]
        },
        fallbacks=[CommandHandler("start", start_command)],
        name="translation_conversation",
        persistent=False,
        allow_reentry=True
    )
    
    # Text generation conversation handler
    textgen_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
        states={
            SELECTING_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, TextGenerationService.select_type)],
            ENTERING_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, TextGenerationService.enter_topic)],
            SELECTING_LENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, TextGenerationService.select_length)],
            SELECTING_TONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, TextGenerationService.select_tone)]
        },
        fallbacks=[CommandHandler("start", start_command)],
        name="textgen_conversation",
        persistent=False,
        allow_reentry=True
    )
    
    # Video creation conversation handler
    video_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
        states={
            VIDEO_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, VideoCreationService.enter_description)],
            VIDEO_LENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, VideoCreationService.select_length)],
            VIDEO_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, VideoCreationService.select_style)],
            SELECTING_RATIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, VideoCreationService.select_ratio)]
        },
        fallbacks=[CommandHandler("start", start_command)],
        name="video_conversation",
        persistent=False,
        allow_reentry=True
    )
    
    # Image generation conversation handler
    image_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
        states={
            ENTERING_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ImageGenerationService.enter_prompt)],
            SELECTING_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ImageGenerationService.select_size)],
            IMAGE_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ImageGenerationService.select_style)],
            SELECTING_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ImageGenerationService.select_quantity)]
        },
        fallbacks=[CommandHandler("start", start_command)],
        name="image_conversation",
        persistent=False,
        allow_reentry=True
    )
    
    # Voice & Music conversation handler
    voice_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
        states={
            SELECTING_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, VoiceMusicService.select_mode)],
            VOICE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, VoiceMusicService.enter_text)],
            SELECTING_VOICE_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, VoiceMusicService.select_voice_style)],
            SELECTING_VOICE_LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, VoiceMusicService.select_voice_language)],
            ENTERING_MUSIC_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, VoiceMusicService.enter_music_prompt)],
            SELECTING_MUSIC_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, VoiceMusicService.select_music_style)]
        },
        fallbacks=[CommandHandler("start", start_command)],
        name="voice_conversation",
        persistent=False,
        allow_reentry=True
    )
    
    # Note: Due to ConversationHandler limitations, we use a single handler approach
    # In production, consider using a state machine or separate entry points
    
    # Main message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu))
    
    # Error handler
    async def error_handler(update: Update, context):
        """Log errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            try:
                user = update.effective_user
                language = await db_manager.get_user_language(user.id)
                await update.effective_message.reply_text(
                    get_text(language, "error")
                )
            except Exception:
                pass
    
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
