#!/usr/bin/env python3
"""
🎭 MAR PD Bot - Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# 🔐 TELEGRAM SETTINGS
# ============================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0"))

# ============================================
# 🔥 FIREBASE SETTINGS
# ============================================
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
PROJECT_ID = os.getenv("PROJECT_ID", "")

# ============================================
# ⚙️ BOT INFORMATION
# ============================================
BOT_NAME = os.getenv("BOT_NAME", "MAR PD Bot")
BOT_VERSION = os.getenv("BOT_VERSION", "3.0.0")

# ============================================
# 🤖 AI LEARNING SETTINGS
# ============================================
AI_LEARN_ENABLED = os.getenv("AI_LEARN_ENABLED", "True") == "True"
LEARN_FROM_GROUPS = os.getenv("LEARN_FROM_GROUPS", "True") == "True"
MIN_LEARN_LENGTH = int(os.getenv("MIN_LEARN_LENGTH", "3"))
MAX_LEARN_LENGTH = int(os.getenv("MAX_LEARN_LENGTH", "200"))

# ============================================
# 🎮 GAMING SYSTEM
# ============================================
GAME_POINTS = {
    "message": int(os.getenv("POINTS_MESSAGE", "1")),
    "media": int(os.getenv("POINTS_MEDIA", "3")),
    "voice": int(os.getenv("POINTS_VOICE", "5")),
    "game_win": int(os.getenv("POINTS_GAME_WIN", "10")),
    "daily_login": int(os.getenv("POINTS_DAILY_LOGIN", "5"))
}

# ============================================
# 🎨 PROFILE SETTINGS
# ============================================
PROFILE_BACKGROUNDS = [
    "🎭", "🃏", "👑", "⚡", "🔥", "💎", "🌟", "✨", "💫", "🦅",
    "🐉", "🦁", "🐯", "🐺", "🦊", "🦇", "☠️", "👻", "💀", "🎮"
]

# ============================================
# 💬 AUTO REPLY DATABASE
# ============================================
AUTO_REPLY_DB = {
    "সালাম": "ওয়ালাইকুম আসসালাম! 🎭 MAR PD এ স্বাগতম!",
    "হ্যালো": "হ্যালো! 🃏 MAR PD কীভাবে সাহায্য করতে পারি?",
    "ধন্যবাদ": "আপনাকেও ধন্যবাদ! 👑",
    "মারপিড": "🎭 MAR PD সবসময় আপনার সাথে!",
    "বট": "হ্যাঁ, আমি এখানে আছি! 🎮",
    "খেলা": "গেম খেলতে: /game",
    "পয়েন্ট": "পয়েন্ট দেখতে: /points",
    "কেমন আছ": "ভালো আছি! আপনিই বা কেমন আছেন? 😊",
    "আল্লাহ": "আল্লাহ সর্বশক্তিমান! ✨",
    "নামাজ": "নামাজের সময়: /prayer",
    "কুরআন": "কুরআনের আয়াত: /quran"
}

# ============================================
# ⚡ EXTRA FEATURES
# ============================================
EXTRA_FEATURES = {
    "auto_backup": os.getenv("DB_AUTO_BACKUP", "True") == "True",
    "anti_spam": True,
    "auto_restart": True,
    "notification": os.getenv("NOTIFY_OWNER", "True") == "True",
    "multi_language": True,
    "file_sharing": True,
    "group_analytics": True
}

# ============================================
# 🔒 SECURITY SETTINGS
# ============================================
MAX_MESSAGES_PER_MINUTE = int(os.getenv("MAX_MESSAGES_PER_MINUTE", "30"))
ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "jpg,jpeg,png,gif,mp4,mp3,pdf").split(",")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024

# ============================================
# 📊 LOGGING & CACHE
# ============================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/marpd_bot.log")
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True") == "True"
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))

# ============================================
# 🚀 PERFORMANCE
# ============================================
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "10"))

# ============================================
# VALIDATE CONFIGURATION
# ============================================
def validate_config():
    """Validate required configuration"""
    errors = []
    
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN is not set in .env file")
    
    if BOT_OWNER_ID == 0:
        errors.append("BOT_OWNER_ID is not set in .env file")
    
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        print("\n💡 Please check your .env file")
        return False
    
    return True

if __name__ == "__main__":
    # Test configuration
    print(f"✅ {BOT_NAME} Configuration loaded")
    print(f"🤖 Token: {'✓' if BOT_TOKEN else '✗'}")
    print(f"👑 Owner: {BOT_OWNER_ID if BOT_OWNER_ID else 'Not set'}")