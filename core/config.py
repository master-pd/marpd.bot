import os
import json
from typing import Any, Dict
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    """Configuration manager for MAR PD Bot"""
    
    # Telegram Bot
    BOT_TOKEN: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    BOT_OWNER_ID: int = field(default_factory=lambda: int(os.getenv("BOT_OWNER_ID", 0)))
    BOT_NAME: str = field(default_factory=lambda: os.getenv("BOT_NAME", "MAR PD Bot"))
    BOT_USERNAME: str = field(default_factory=lambda: os.getenv("BOT_USERNAME", "@mar_pd_bot"))
    BOT_VERSION: str = field(default_factory=lambda: os.getenv("BOT_VERSION", "7.0.0"))
    
    # Firebase (Firestore)
    FIREBASE_API_KEY: str = field(default_factory=lambda: os.getenv("FIREBASE_API_KEY", ""))
    FIREBASE_PROJECT_ID: str = field(default_factory=lambda: os.getenv("FIREBASE_PROJECT_ID", ""))
    FIREBASE_DB_URL: str = field(default_factory=lambda: os.getenv("FIREBASE_DB_URL", ""))
    FIREBASE_STORAGE_BUCKET: str = field(default_factory=lambda: os.getenv("FIREBASE_STORAGE_BUCKET", ""))
    
    # Payment (Manual Bkash/Nagad Only)
    BKASH_NUMBER: str = field(default_factory=lambda: os.getenv("BKASH_NUMBER", "017XXXXXXXX"))
    NAGAD_NUMBER: str = field(default_factory=lambda: os.getenv("NAGAD_NUMBER", "017XXXXXXXX"))
    PAYMENT_ADMIN_ID: str = field(default_factory=lambda: os.getenv("PAYMENT_ADMIN_ID", ""))
    
    # Points System
    POINTS_PER_MESSAGE: int = field(default_factory=lambda: int(os.getenv("POINTS_PER_MESSAGE", 1)))
    POINTS_PER_MEDIA: int = field(default_factory=lambda: int(os.getenv("POINTS_PER_MEDIA", 3)))
    POINTS_PER_VOICE: int = field(default_factory=lambda: int(os.getenv("POINTS_PER_VOICE", 5)))
    DAILY_BONUS: int = field(default_factory=lambda: int(os.getenv("DAILY_BONUS", 10)))
    REFERRAL_BONUS: int = field(default_factory=lambda: int(os.getenv("REFERRAL_BONUS", 50)))
    
    # AI Learning
    AI_LEARNING_ENABLED: bool = field(default_factory=lambda: os.getenv("AI_LEARNING_ENABLED", "True") == "True")
    MIN_LEARN_LENGTH: int = field(default_factory=lambda: int(os.getenv("MIN_LEARN_LENGTH", 3)))
    MAX_LEARN_LENGTH: int = field(default_factory=lambda: int(os.getenv("MAX_LEARN_LENGTH", 100)))
    AI_RESPONSE_LIMIT: int = field(default_factory=lambda: int(os.getenv("AI_RESPONSE_LIMIT", 1000)))
    
    # Gaming
    GAMES_ENABLED: bool = field(default_factory=lambda: os.getenv("GAMES_ENABLED", "True") == "True")
    GAME_COOLDOWN: int = field(default_factory=lambda: int(os.getenv("GAME_COOLDOWN", 30)))
    MAX_GAMES_PER_DAY: int = field(default_factory=lambda: int(os.getenv("MAX_GAMES_PER_DAY", 20)))
    
    # Economy
    MIN_WITHDRAW: int = field(default_factory=lambda: int(os.getenv("MIN_WITHDRAW", 100)))
    MAX_WITHDRAW: int = field(default_factory=lambda: int(os.getenv("MAX_WITHDRAW", 5000)))
    WITHDRAW_FEE: float = field(default_factory=lambda: float(os.getenv("WITHDRAW_FEE", 0.2)))  # 20%
    RECHARGE_RATE: int = field(default_factory=lambda: int(os.getenv("RECHARGE_RATE", 10)))  # 1 Taka = 10 points
    
    # Security
    RATE_LIMIT: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT", 50)))
    MAX_FILE_SIZE: int = field(default_factory=lambda: int(os.getenv("MAX_FILE_SIZE", 50)))  # MB
    ALLOWED_FILE_TYPES: list = field(default_factory=lambda: os.getenv("ALLOWED_FILE_TYPES", "jpg,png,gif,mp4,pdf").split(","))
    ENABLE_CAPTCHA: bool = field(default_factory=lambda: os.getenv("ENABLE_CAPTCHA", "True") == "True")
    
    # Notifications
    NOTIFY_ON_START: bool = field(default_factory=lambda: os.getenv("NOTIFY_ON_START", "True") == "True")
    NOTIFY_ON_ERROR: bool = field(default_factory=lambda: os.getenv("NOTIFY_ON_ERROR", "True") == "True")
    NOTIFY_OWNER: bool = field(default_factory=lambda: os.getenv("NOTIFY_OWNER", "True") == "True")
    
    # Web Dashboard
    WEB_DASHBOARD: bool = field(default_factory=lambda: os.getenv("WEB_DASHBOARD", "False") == "True")
    DASHBOARD_PORT: int = field(default_factory=lambda: int(os.getenv("DASHBOARD_PORT", 8080)))
    DASHBOARD_PASSWORD: str = field(default_factory=lambda: os.getenv("DASHBOARD_PASSWORD", "admin123"))
    
    # Backup
    AUTO_BACKUP: bool = field(default_factory=lambda: os.getenv("AUTO_BACKUP", "True") == "True")
    BACKUP_INTERVAL: int = field(default_factory=lambda: int(os.getenv("BACKUP_INTERVAL", 3600)))  # seconds
    MAX_BACKUPS: int = field(default_factory=lambda: int(os.getenv("MAX_BACKUPS", 30)))
    
    # System
    DEBUG_MODE: bool = field(default_factory=lambda: os.getenv("DEBUG_MODE", "False") == "True")
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    DATA_DIR: str = field(default_factory=lambda: os.getenv("DATA_DIR", "data"))
    LOG_DIR: str = field(default_factory=lambda: os.getenv("LOG_DIR", "logs"))
    BACKUP_DIR: str = field(default_factory=lambda: os.getenv("BACKUP_DIR", "backups"))
    
    # Localization
    DEFAULT_LANGUAGE: str = field(default_factory=lambda: os.getenv("DEFAULT_LANGUAGE", "bn"))
    TIMEZONE: str = field(default_factory=lambda: os.getenv("TIMEZONE", "Asia/Dhaka"))
    
    def __post_init__(self):
        """Validate configuration"""
        self.validate()
        self.create_directories()
    
    def validate(self):
        """Validate required configuration"""
        errors = []
        
        if not self.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        if not self.BOT_OWNER_ID:
            errors.append("BOT_OWNER_ID is required")
        if not self.FIREBASE_API_KEY:
            errors.append("FIREBASE_API_KEY is required")
        if not self.BKASH_NUMBER or self.BKASH_NUMBER == "017XXXXXXXX":
            errors.append("BKASH_NUMBER is required")
        if not self.NAGAD_NUMBER or self.NAGAD_NUMBER == "017XXXXXXXX":
            errors.append("NAGAD_NUMBER is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    def create_directories(self):
        """Create required directories"""
        directories = [self.DATA_DIR, self.LOG_DIR, self.BACKUP_DIR]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def save(self, filepath: str = "config.json"):
        """Save config to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
    
    @classmethod
    def load(cls, filepath: str = "config.json") -> 'Config':
        """Load config from file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(**data)