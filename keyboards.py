"""
Telegram keyboard utilities
"""
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from locales import get_text
import config
# from database.models import PremiumPackage # Import for type hinting

def get_language_keyboard():
    """Get language selection keyboard"""
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard(language: str):
    """Get main menu keyboard"""
    # 1. Asosiy Menyuni 1-banddagi kabi tuzish
    keyboard = [
        [get_text(language, "service_chat"), get_text(language, "service_translation")],
        [get_text(language, "service_text_gen"), get_text(language, "service_video")],
        [get_text(language, "service_image"), get_text(language, "service_voice")],
        [get_text(language, "service_premium")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard(language: str):
    """Get back button keyboard"""
    keyboard = [[get_text(language, "back")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_cancel_keyboard(language: str):
    """Get cancel button keyboard"""
    keyboard = [[get_text(language, "cancel")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_options_keyboard(options: list, language: str, columns: int = 2):
    """Get generic options keyboard"""
    keyboard = []
    row = []
    for i, option in enumerate(options):
        row.append(option)
        if (i + 1) % columns == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([get_text(language, "back")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- PREMIUM KEYBOARDS ---

async def get_premium_packages_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Get keyboard for selecting premium packages"""
    from database import db_manager # Import here to avoid circular dependency
    
    packages = await db_manager.get_all_packages()
    keyboard_options = []
    
    for pkg in packages:
        # Format: Name | Price
        price_text = get_text(language, "free") if pkg.is_free else f"{pkg.price:,.0f} UZS"
        name = getattr(pkg, f"name_{language}")
        keyboard_options.append(f"{name} | {price_text}")

    # Display in 2 columns
    return get_options_keyboard(keyboard_options, language, columns=2)

def get_payment_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Get keyboard for payment confirmation"""
    keyboard = [
        [get_text(language, "payment_confirm_btn")],
        [get_text(language, "back")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- ADMIN KEYBOARDS ---

def get_admin_panel_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Get admin panel main menu keyboard"""
    keyboard = [
        [get_text(language, "admin_stats_btn"), get_text(language, "admin_payments_btn")],
        [get_text(language, "admin_promo_btn"), get_text(language, "admin_broadcast_btn")],
        [get_text(language, "back")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- EXISTING SERVICE KEYBOARDS (UNMODIFIED) ---

def get_translation_language_keyboard(language: str):
    """Get translation language selection keyboard"""
    languages = config.SERVICE_PARAMS["translation"]["languages"]
    return get_options_keyboard(languages, language, columns=2)

def get_video_length_keyboard(language: str):
    """Get video length selection keyboard"""
    lengths = config.SERVICE_PARAMS["video_creation"]["length_options"]
    return get_options_keyboard(lengths, language, columns=2)

def get_video_style_keyboard(language: str):
    styles = config.SERVICE_PARAMS["video_creation"]["style_options"]
    return get_options_keyboard(styles, language, columns=2)

def get_video_ratio_keyboard(language: str):
    ratios = config.SERVICE_PARAMS["video_creation"]["aspect_ratios"]
    return get_options_keyboard(ratios, language, columns=2)

def get_image_size_keyboard(language: str):
    sizes = config.SERVICE_PARAMS["image_generation"]["size_options"]
    return get_options_keyboard(sizes, language, columns=2)

def get_image_style_keyboard(language: str):
    styles = config.SERVICE_PARAMS["image_generation"]["style_options"]
    return get_options_keyboard(styles, language, columns=2)

def get_image_quantity_keyboard(language: str):
    quantities = [str(q) for q in config.SERVICE_PARAMS["image_generation"]["quantity_options"]]
    return get_options_keyboard(quantities, language, columns=4)

def get_voice_mode_keyboard(language: str):
    keyboard = [
        [get_text(language, "voice_mode_tts")],
        [get_text(language, "voice_mode_music")],
        [get_text(language, "back")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_voice_style_keyboard(language: str):
    styles = config.SERVICE_PARAMS["voice_music"]["voice_styles"]
    return get_options_keyboard(styles, language, columns=2)

def get_voice_language_keyboard(language: str):
    languages = config.SERVICE_PARAMS["voice_music"]["languages"]
    return get_options_keyboard(languages, language, columns=2)

def get_music_style_keyboard(language: str):
    styles = config.SERVICE_PARAMS["voice_music"]["music_styles"]
    return get_options_keyboard(styles, language, columns=2)

def get_text_type_keyboard(language: str):
    types = config.SERVICE_PARAMS["text_generation"]["content_types"]
    return get_options_keyboard(types, language, columns=2)

def get_text_length_keyboard(language: str):
    lengths = config.SERVICE_PARAMS["text_generation"]["lengths"]
    return get_options_keyboard(lengths, language, columns=1)

def get_text_tone_keyboard(language: str):
    tones = config.SERVICE_PARAMS["text_generation"]["tones"]
    return get_options_keyboard(tones, language, columns=2)
