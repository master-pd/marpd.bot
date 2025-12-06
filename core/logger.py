import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logger(name="MARPD_Bot"):
    """Setup comprehensive logging system"""
    
    # Create logs directory if not exists
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Log format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # File handler (rotating, max 10MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(
        f'logs/marpd_bot_{datetime.now().strftime("%Y%m")}.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        f'logs/errors_{datetime.now().strftime("%Y%m")}.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger

class BotLogger:
    """Custom logger for bot operations"""
    
    def __init__(self, bot_name="MARPD_Bot"):
        self.logger = setup_logger(bot_name)
        self.bot_name = bot_name
        
    def log_command(self, user_id, username, command, args=""):
        """Log command usage"""
        self.logger.info(f"CMD | User:{user_id} (@{username}) | Command:{command} | Args:{args}")
    
    def log_message(self, user_id, username, message_type, length):
        """Log message activity"""
        self.logger.info(f"MSG | User:{user_id} (@{username}) | Type:{message_type} | Length:{length}")
    
    def log_payment(self, user_id, amount, method, status):
        """Log payment activity"""
        self.logger.info(f"PAY | User:{user_id} | Amount:{amount} | Method:{method} | Status:{status}")
    
    def log_game(self, user_id, game_type, result, points):
        """Log game activity"""
        self.logger.info(f"GAME | User:{user_id} | Game:{game_type} | Result:{result} | Points:{points}")
    
    def log_error(self, error_type, details, user_id=None):
        """Log errors"""
        if user_id:
            self.logger.error(f"ERROR | Type:{error_type} | User:{user_id} | Details:{details}")
        else:
            self.logger.error(f"ERROR | Type:{error_type} | Details:{details}")
    
    def log_admin_action(self, admin_id, action, target=None):
        """Log admin actions"""
        if target:
            self.logger.info(f"ADMIN | Admin:{admin_id} | Action:{action} | Target:{target}")
        else:
            self.logger.info(f"ADMIN | Admin:{admin_id} | Action:{action}")
    
    def log_system(self, component, action, details=""):
        """Log system operations"""
        self.logger.info(f"SYSTEM | Component:{component} | Action:{action} | Details:{details}")
    
    def get_log_file(self, log_type="main"):
        """Get latest log file path"""
        month = datetime.now().strftime("%Y%m")
        
        if log_type == "main":
            return f'logs/marpd_bot_{month}.log'
        elif log_type == "error":
            return f'logs/errors_{month}.log'
        else:
            return f'logs/{log_type}_{month}.log'