#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎭 MAR PD Bot - Runner Script
Alternative entry point with better error handling
"""

import sys
import os
import signal
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def setup_environment():
    """Setup environment and paths"""
    # Check for .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and configure it.")
        sys.exit(1)
    
    # Check for required directories
    required_dirs = ['data', 'logs', 'backups']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"📁 Created directory: {dir_name}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/bot_runner.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def check_dependencies():
    """Check required dependencies"""
    required_packages = [
        'python-telegram-bot',
        'firebase-admin',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing dependencies:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main function"""
    print("\n" + "="*50)
    print("🎭 MAR PD Bot - Runner")
    print("="*50 + "\n")
    
    # Setup environment
    setup_environment()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting MAR PD Bot Runner...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Import and run bot
        from main import Application
        
        logger.info("Initializing application...")
        app = Application()
        
        # Run application
        import asyncio
        asyncio.run(app.run())
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Check logs/bot_runner.log for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()