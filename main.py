#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 MAR PD Bot - Complete Ultra Advanced Version
Simple, Manual, No External APIs
All Features Included
"""

import asyncio
import logging
import sys
import signal
from datetime import datetime

# Add paths
sys.path.append('core')
sys.path.append('features')
sys.path.append('utils')
sys.path.append('handlers')
sys.path.append('data')

from core.bot import MARPD_Bot
from core.logger import setup_logger
from features.scheduler import TaskScheduler
from features.backup import BackupManager
from web.dashboard import start_dashboard

class Application:
    def __init__(self):
        self.logger = setup_logger()
        self.bot = None
        self.scheduler = TaskScheduler()
        self.backup = BackupManager()
        self.running = False
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.shutdown()
    
    async def startup(self):
        """Startup the application"""
        self.logger.info("🚀 Starting MAR PD Bot...")
        
        # Initialize bot
        self.bot = MARPD_Bot()
        
        # Start background tasks
        await self.scheduler.start()
        await self.backup.start()
        
        # Start web dashboard if enabled
        if self.bot.config.WEB_DASHBOARD:
            asyncio.create_task(start_dashboard())
        
        self.running = True
        self.logger.info("✅ Application started successfully!")
    
    async def run(self):
        """Main run loop"""
        await self.startup()
        
        try:
            while self.running:
                # Keep the application running
                await asyncio.sleep(1)
                
                # Check bot status
                if not self.bot.is_running:
                    self.logger.warning("Bot stopped, restarting...")
                    await self.bot.start()
                
        except Exception as e:
            self.logger.error(f"Application error: {e}")
        
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the application"""
        self.logger.info("🛑 Shutting down application...")
        
        # Stop bot
        if self.bot:
            await self.bot.stop()
        
        # Stop background tasks
        await self.scheduler.stop()
        await self.backup.stop()
        
        self.logger.info("👋 Application shutdown complete")
        sys.exit(0)

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════╗
    ║         🎭 MAR PD BOT v7.0.0 🎭          ║
    ║        Complete All Features Edition     ║
    ║                                          ║
    ║  🔥 Features:                           ║
    ║  • AI Learning from Users               ║
    ║  • 20+ Games with Economy               ║
    ║  • Bkash/Nagad Manual Payments          ║
    ║  • Firestore Database                   ║
    ║  • Web Dashboard                        ║
    ║  • Auto Backup & Reports                ║
    ║  • Complete Admin Controls              ║
    ║                                          ║
    ║  📞 Support: @mar_pd_support            ║
    ╚══════════════════════════════════════════╝
    """
    print(banner)

if __name__ == "__main__":
    print_banner()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/marpd_bot.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create and run application
    app = Application()
    app.setup_signal_handlers()
    
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)