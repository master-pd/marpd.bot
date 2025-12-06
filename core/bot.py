import asyncio
import logging
from datetime import datetime
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

from core.config import Config
from core.database import Database
from core.logger import setup_logger
from features.ai_trainer import AITrainer
from features.gaming import GamingSystem
from features.admin import AdminSystem
from features.media import MediaProcessor
from features.payment import PaymentSystem
from features.shop import ShopSystem
from features.economy import EconomySystem
from features.notifications import NotificationSystem
from features.analytics import AnalyticsSystem
from handlers.command_handler import CommandHandler
from handlers.message_handler import MessageHandler
from handlers.callback_handler import CallbackHandler
from handlers.error_handler import ErrorHandler

class MARPD_Bot:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger("MARPD_Bot")
        
        # Initialize core systems
        self.db = Database()
        self.ai = AITrainer(self.db)
        self.gaming = GamingSystem(self.db)
        self.admin = AdminSystem(self.db)
        self.media = MediaProcessor(self.db)
        self.payment = PaymentSystem(self.db)
        self.shop = ShopSystem(self.db)
        self.economy = EconomySystem(self.db)
        self.notifications = NotificationSystem(self.db)
        self.analytics = AnalyticsSystem(self.db)
        
        # Initialize handlers
        self.command_handler = CommandHandler(self)
        self.message_handler = MessageHandler(self)
        self.callback_handler = CallbackHandler(self)
        self.error_handler = ErrorHandler(self)
        
        # Bot state
        self.application = None
        self.is_running = False
        self.start_time = datetime.now()
        self.stats = {
            'total_messages': 0,
            'total_users': 0,
            'total_games': 0,
            'total_payments': 0
        }
    
    async def initialize(self):
        """Initialize bot systems"""
        self.logger.info("Initializing MAR PD Bot...")
        
        # Initialize database
        await self.db.initialize()
        
        # Load AI training data
        await self.ai.load_training_data()
        
        # Load game data
        await self.gaming.load_games()
        
        # Load shop items
        await self.shop.load_items()
        
        # Start notification system
        await self.notifications.start()
        
        self.logger.info("Bot systems initialized successfully")
    
    async def setup_commands(self):
        """Setup bot commands menu"""
        commands = [
            BotCommand("start", "🎭 বট শুরু করুন"),
            BotCommand("menu", "📱 মেইন মেনু"),
            BotCommand("help", "❓ সাহায্য"),
            BotCommand("game", "🎮 গেম খেলুন"),
            BotCommand("points", "💰 পয়েন্ট চেক"),
            BotCommand("shop", "🛒 শপ"),
            BotCommand("recharge", "💸 রিচার্জ"),
            BotCommand("withdraw", "🏧 উইথড্র"),
            BotCommand("send", "📤 পয়েন্ট পাঠান"),
            BotCommand("profile", "👤 প্রোফাইল"),
            BotCommand("leaderboard", "🏆 লিডারবোর্ড"),
            BotCommand("daily", "🎁 ডেইলি বোনাস"),
            BotCommand("refer", "👥 রেফার"),
            BotCommand("admin", "👮 অ্যাডমিন"),
            BotCommand("settings", "⚙️ সেটিংস"),
            BotCommand("feedback", "💬 ফিডব্যাক"),
            BotCommand("report", "📊 রিপোর্ট"),
            BotCommand("support", "🆘 সাপোর্ট")
        ]
        
        await self.application.bot.set_my_commands(commands)
        self.logger.info("Bot commands setup completed")
    
    def register_handlers(self):
        """Register all handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.command_handler.start))
        self.application.add_handler(CommandHandler("menu", self.command_handler.menu))
        self.application.add_handler(CommandHandler("help", self.command_handler.help))
        self.application.add_handler(CommandHandler("game", self.command_handler.game))
        self.application.add_handler(CommandHandler("points", self.command_handler.points))
        self.application.add_handler(CommandHandler("shop", self.command_handler.shop))
        self.application.add_handler(CommandHandler("recharge", self.command_handler.recharge))
        self.application.add_handler(CommandHandler("withdraw", self.command_handler.withdraw))
        self.application.add_handler(CommandHandler("send", self.command_handler.send_points))
        self.application.add_handler(CommandHandler("profile", self.command_handler.profile))
        self.application.add_handler(CommandHandler("leaderboard", self.command_handler.leaderboard))
        self.application.add_handler(CommandHandler("daily", self.command_handler.daily_bonus))
        self.application.add_handler(CommandHandler("refer", self.command_handler.refer))
        self.application.add_handler(CommandHandler("admin", self.command_handler.admin))
        self.application.add_handler(CommandHandler("settings", self.command_handler.settings))
        self.application.add_handler(CommandHandler("feedback", self.command_handler.feedback))
        self.application.add_handler(CommandHandler("report", self.command_handler.report))
        self.application.add_handler(CommandHandler("support", self.command_handler.support))
        
        # Message handlers
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.message_handler.handle_text
        ))
        self.application.add_handler(MessageHandler(
            filters.PHOTO, 
            self.message_handler.handle_photo
        ))
        self.application.add_handler(MessageHandler(
            filters.VIDEO, 
            self.message_handler.handle_video
        ))
        self.application.add_handler(MessageHandler(
            filters.Document.ALL, 
            self.message_handler.handle_document
        ))
        self.application.add_handler(MessageHandler(
            filters.VOICE, 
            self.message_handler.handle_voice
        ))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(
            self.callback_handler.handle
        ))
        
        # Error handler
        self.application.add_error_handler(
            self.error_handler.handle_error
        )
        
        self.logger.info("All handlers registered")
    
    async def start(self):
        """Start the bot"""
        try:
            # Create application
            self.application = Application.builder() \
                .token(self.config.BOT_TOKEN) \
                .build()
            
            # Initialize systems
            await self.initialize()
            
            # Setup commands
            await self.setup_commands()
            
            # Register handlers
            self.register_handlers()
            
            # Start polling
            self.logger.info("Starting bot polling...")
            await self.application.initialize()
            await self.application.start()
            
            # Send startup notification
            if self.config.NOTIFY_ON_START:
                await self.notifications.send_startup_message()
            
            self.is_running = True
            self.logger.info("✅ MAR PD Bot is now running!")
            
            # Keep running
            await self.application.updater.start_polling()
            
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            self.is_running = False
            raise
    
    async def stop(self):
        """Stop the bot"""
        self.logger.info("Stopping bot...")
        
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
        
        # Stop all systems
        await self.notifications.stop()
        await self.db.close()
        
        self.is_running = False
        self.logger.info("Bot stopped successfully")
    
    async def get_stats(self):
        """Get bot statistics"""
        return {
            'uptime': str(datetime.now() - self.start_time),
            'total_messages': self.stats['total_messages'],
            'total_users': await self.db.get_total_users(),
            'active_users': await self.db.get_active_users(),
            'total_games': self.stats['total_games'],
            'total_payments': self.stats['total_payments'],
            'total_points': await self.db.get_total_points(),
            'ai_responses': await self.ai.get_response_count()
        }