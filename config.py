"""
Configuration file for Telegram AI Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = "8321556963:AAEELXHRLSnCtBFLy9_4-B3p15wsnylxWR4"

# Admin Configuration
ADMIN_IDS = [5163199584]  # SARDOR ID
PAYMENT_ADMIN_ID = 5163199584 # SARDOR ID

# Database Configuration
DATABASE_URL = "sqlite+aiosqlite:///bot_database.db"

# Payment Configuration (Manual Transfer) - YANGILANGAN!
# Renderga yuklashda Environment Variable orqali o'qing (xavfsizlik uchun)
MANUAL_CARD_NUMBER = os.getenv(
    "MANUAL_CARD_NUMBER", 
    "Norboyev Sardor 4463 0900 3664 3065" 
)

# --- PREMIUM CONFIGURATION (Qolgan qismi o'zgarishsiz) ---
PREMIUM_PACKAGES = {
    "basic": {
        "name_uz": "Asosiy", "name_ru": "Базовый",
        "price": 0,
        "duration_days": 3650, 
        "features": ["Chat", "Translation"],
        "limits": {
            "chat": 5, "translation": 10, "text_generation": 0,
            "video_creation": 0, "image_generation": 0, "voice_music": 0
        },
        "is_free": True
    },
    "standard": {
        "name_uz": "Standart", "name_ru": "Стандарт",
        "price": 0, 
        "duration_days": 3650,
        "features": ["Chat", "Translation", "Text Generation"],
        "limits": {
            "chat": 10, "translation": 20, "text_generation": 5,
            "video_creation": 0, "image_generation": 0, "voice_music": 0
        },
        "is_free": True
    },
    "pro": {
        "name_uz": "Pro (Oylik)", "name_ru": "Pro (Месячный)",
        "price": 50000,
        "duration_days": 30,
        "features": ["Chat (Cheksiz)", "Translation (Cheksiz)", "Text Gen (Cheksiz)", "Image Gen (100)", "Video Gen (10)"],
        "limits": {
            "chat": -1, "translation": -1, "text_generation": -1,
            "video_creation": 10, "image_generation": 100, "voice_music": 20
        },
        "is_free": False
    },
    "vip": {
        "name_uz": "VIP (Yillik)", "name_ru": "VIP (Годовой)",
        "price": 450000,
        "duration_days": 365,
        "features": ["Barcha xizmatlar (Cheksiz)", "Yuqori sifatli natijalar", "Ustuvor qo'llab-quvvatlash"],
        "limits": {
            "chat": -1, "translation": -1, "text_generation": -1,
            "video_creation": -1, "image_generation": -1, "voice_music": -1
        },
        "is_free": False
    }
}


# Service Parameters (unchanged)
SERVICE_PARAMS = {
    "video_creation": {
        "length_options": ["5 seconds", "10 seconds", "15 seconds", "30 seconds"],
        "style_options": ["Realistic", "Animated", "Cinematic", "Abstract"],
        "aspect_ratios": ["16:9", "9:16", "1:1", "4:3"]
    },
    "image_generation": {
        "size_options": ["512x512", "1024x1024", "1024x1792", "1792x1024"],
        "style_options": ["Realistic", "Artistic", "Anime", "3D Render", "Oil Painting"],
        "quantity_options": [1, 2, 3, 4]
    },
    "voice_music": {
        "voice_styles": ["Professional", "Casual", "Dramatic", "Cheerful", "Calm"],
        "languages": ["Uzbek", "Russian", "English"],
        "music_styles": ["Classical", "Electronic", "Ambient", "Pop", "Jazz"]
    },
    "text_generation": {
        "content_types": ["Blog Post", "Email", "Scenario", "Article", "Social Media Post"],
        "lengths": ["Short (100-300 words)", "Medium (300-700 words)", "Long (700-1500 words)"],
        "tones": ["Professional", "Casual", "Formal", "Friendly", "Persuasive"]
    },
    "translation": {
        "languages": ["Uzbek", "Russian", "English", "Turkish", "Chinese", "Arabic"]
    }
}

# AI API Configuration (to be filled by user)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY", "")

# Premium Features
PREMIUM_FEATURES = {
    "unlimited_requests": True,
    "priority_processing": True,
    "higher_quality": True,
    "exclusive_models": True
}
