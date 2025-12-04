"""
Configuration file for Telegram AI Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = "8321556963:AAEELXHRLSnCtBFLy9_4-B3p15wsnylxWR4"

# Admin Configuration
ADMIN_IDS = [123456789]  # Add your Telegram user ID here

# Database Configuration
DATABASE_URL = "sqlite+aiosqlite:///bot_database.db"

# Rate Limits (requests per day for free users)
RATE_LIMITS = {
    "chat": 10,
    "translation": 20,
    "text_generation": 5,
    "video_creation": 2,
    "image_generation": 5,
    "voice_music": 5
}

# Service Parameters
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

# Premium Configuration
PREMIUM_FEATURES = {
    "unlimited_requests": True,
    "priority_processing": True,
    "higher_quality": True,
    "exclusive_models": True
}
