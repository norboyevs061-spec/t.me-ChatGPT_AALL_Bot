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
from services.premium import SELECTING_PACKAGE, ENTERING_PROMO, WAITING_FOR_PAYMENT # NEW

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
    
    # Create or get user and ensure basic package is set
    user_obj = await db_manager.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Check if user has language preference
    language = user_obj.language
    
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
    """Handle /help command (Updated help text)"""
    user = update.effective_user
    language = await db_manager.get_user_language(user.id)
    
    help_text = f"""
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
/premium - Show premium packages

Admin Commands (admin only):
/admin_stats - Show bot, revenue and usage statistics
/list_payments - List pending payments for manual confirmation
/confirm_payment <id> - Confirm payment and activate premium
/create_promo <code> <discount%> [max] [days] - Create a promo code
/list_promos - List existing promo codes
/grant_premium <user_id> <days> [package] - Grant premium
/revoke_premium <user_id> - Revoke premium
/list_users [limit] - List recent users
/broadcast <message> - Send message to all users
"""
    
    await update.message.reply_text(help_text)


async def stats_command(update: Update, context):
    """Handle /stats command - show user statistics (Now shows package and limits)"""
    user = update.effective_user
    language = await db_manager.get_user_language(user.id)
    
    # Get user object
    user_obj = await db_manager.get_user(user.id)
    if not user_obj:
        await update.message.reply_text(get_text(language, "error"))
        return

    # Get package and limits
    package_key = await db_manager.get_user_package_key(user.id)
    package_config = config.PREMIUM_PACKAGES.get(package_key, config.PREMIUM_PACKAGES['basic'])
    
    stats_text = f"📊 Your Statistics\n\n"
    stats_text += f"**Package**: {package_config[f'name_{language}']}\n"
    stats_text += f"**Premium Status**: {'✅ Active' if user_obj.is_premium else '❌ Inactive'}\n"
    stats_text += f"**Expiry Date**: {user_obj.premium_expiry.strftime('%Y-%m-%d %H:%M:%S') if user_obj.premium_expiry else 'N/A'}\n"
    stats_text += f"Member Since: {user_obj.created_at.strftime('%Y-%m-%d')}\n\n"
    
    stats_text += f"**Daily Usage Limits (Remaining/Total)**:\n"
    
    for service_name, limit in package_config['limits'].items():
        if limit == -1:
            usage_text = "∞ / ∞"
        else:
            is_allowed, used, total_limit = await db_manager.check_rate_limit(user.id, service_name)
            remaining = total_limit - used
            usage_text = f"{remaining}/{total_limit}"

        stats_text += f"  • {service_name.replace('_', ' ').title()}: {usage_text}\n"
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')


async def language_command(update: Update, context):
    """Handle /language command - change language (Unchanged)"""
    await update.message.reply_text(
        "Tilni tanlang / Выберите язык:",
        reply_markup=get_language_keyboard()
    )


# Callback query handler for language selection (Unchanged)
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
    """Route messages from main menu to appropriate service or Premium/Admin flows"""
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
        # Redirect to the entry point of the Premium Conversation Handler
        return await PremiumService.show_info(update, context)
    else:
        # Unknown command - Show main menu (Fallback)
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
    application.add_handler(CommandHandler("premium", PremiumService.show_info)) # Added command
    
    # Admin command handlers (Updated/New)
    application.add_handler(CommandHandler("admin_stats", AdminPanel.show_stats))
    application.add_handler(CommandHandler("list_payments", AdminPanel.list_pending_payments))
    application.add_handler(CommandHandler("confirm_payment", AdminPanel.confirm_payment))
    application.add_handler(CommandHandler("create_promo", AdminPanel.create_promo_code_command))
    application.add_handler(CommandHandler("list_promos", AdminPanel.list_promo_codes_command))
    application.add_handler(CommandHandler("grant_premium", AdminPanel.grant_premium))
    application.add_handler(CommandHandler("revoke_premium", AdminPanel.revoke_premium))
    application.add_handler(CommandHandler("list_users", AdminPanel.list_users))
    application.add_handler(CommandHandler("broadcast", AdminPanel.broadcast))
    
    # Language selection callback
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    
    # Premium purchase conversation handler (NEW)
    premium_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(get_text('uz', "service_premium")) | filters.Regex(get_text('ru', "service_premium")), PremiumService.show_info)],
        states={
            SELECTING_PACKAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, PremiumService.select_package)],
            ENTERING_PROMO: [MessageHandler(filters.TEXT & ~filters.COMMAND, PremiumService.enter_promo)],
            WAITING_FOR_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, PremiumService.payment_confirmation_request)]
        },
        fallbacks=[CommandHandler("start", start_command), MessageHandler(filters.Regex(get_text('uz', "back")) | filters.Regex(get_text('ru', "back")), PremiumService.show_info)],
        name="premium_conversation",
        persistent=False,
        allow_reentry=True
    )
    application.add_handler(premium_handler)
    
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
