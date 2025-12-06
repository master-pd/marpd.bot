#!/usr/bin/env python3
"""
🎭 MAR PD Bot - Final Version
🔧 Fixed: Single instance running only
"""

import logging
import random
import asyncio
import sys
import os
import socket
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, CallbackQueryHandler, ContextTypes
)

# Import modules
from config import *
from database import db
from ai_trainer import ai_trainer
from gaming import gaming
from admin_control import AdminControl
from media_handler import media

# ============================================
# 🛡️ SINGLE INSTANCE CHECK
# ============================================

def check_single_instance():
    """Check if another instance is already running"""
    lock_file = "/data/data/com.termux/files/usr/tmp/marpd_bot.lock"
    
    try:
        # Try to create lock file
        fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        # Write current PID
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return False  # No other instance running
    except OSError:
        # File exists, check if process is still running
        try:
            with open(lock_file, 'r') as f:
                old_pid = int(f.read().strip())
            
            # Check if process exists
            try:
                os.kill(old_pid, 0)  # Check if process exists
                return True  # Another instance is running
            except OSError:
                # Process doesn't exist, remove stale lock
                os.remove(lock_file)
                return False
        except:
            os.remove(lock_file)
            return False

def cleanup_lock_file():
    """Cleanup lock file on exit"""
    lock_file = "/data/data/com.termux/files/usr/tmp/marpd_bot.lock"
    try:
        if os.path.exists(lock_file):
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())
                if pid == os.getpid():
                    os.remove(lock_file)
    except:
        pass

# ============================================
# 📊 LOGGING SETUP
# ============================================

# Create logs directory if not exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL),
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# 🔧 CONFIGURATION VALIDATION
# ============================================

def validate_configuration():
    """Validate bot configuration"""
    errors = []
    
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        errors.append("❌ BOT_TOKEN is not set in .env file")
    
    if BOT_OWNER_ID == 0:
        errors.append("⚠️ BOT_OWNER_ID is not set in .env file")
    
    if errors:
        print("\n".join(errors))
        print("\n💡 Please edit .env file with your credentials")
        return False
    
    return True

# ============================================
# 🎭 COMMAND HANDLERS
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    chat = update.effective_chat
    
    logger.info(f"Start command from {user.id} ({user.first_name})")
    
    # Save user data
    user_data = {
        "user_id": str(user.id),
        "username": user.username or "",
        "first_name": user.first_name,
        "join_date": datetime.now().isoformat(),
        "message_count": "0",
        "points": "100",  # Starting bonus
        "level": "1",
        "last_active": datetime.now().isoformat(),
        "is_bot_owner": "true" if user.id == BOT_OWNER_ID else "false",
        "bot_name": BOT_NAME
    }
    
    db.save_user(user_data)
    
    # Welcome message
    welcome = f"""
🎭 **{BOT_NAME} v{BOT_VERSION}** 🎭

*স্বাগতম {user.first_name}!* 

⚡ *বটের বিশেষ বৈশিষ্ট্য:*
• 🤖 AI লার্নিং সিস্টেম
• 🎮 গেমিং ও পয়েন্ট
• 👑 অ্যাডমিন কন্ট্রোল
• 📸 মিডিয়া সাপোর্ট
• 📊 গ্রুপ এনালিটিক্স

📋 *প্রধান কমান্ড:*
/start - বট শুরু করুন
/profile - প্রোফাইল দেখুন  
/game - গেম খেলুন
/leaderboard - লিডারবোর্ড
/daily - ডেইলি রিওয়ার্ড
/ai [প্রশ্ন] - AI কে প্রশ্ন করুন
/media - মিডিয়া রিপোর্ট
/stats - বট পরিসংখ্যান
/admin - অ্যাডমিন প্যানেল
/help - সাহায্য

🎉 *শুরুতে ১০০ পয়েন্ট বোনাস!*
"""
    
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /profile command"""
    user = update.effective_user
    user_data = db.get_user(user.id) or {}
    
    profile_text = gaming.generate_profile_card(user_data)
    
    # Create interactive buttons
    keyboard = [
        [InlineKeyboardButton("🎮 গেম খেলুন", callback_data="play_game")],
        [InlineKeyboardButton("🏆 লিডারবোর্ড", callback_data="show_leaderboard")],
        [InlineKeyboardButton("🎁 ডেইলি রিওয়ার্ড", callback_data="daily_reward")],
        [InlineKeyboardButton("📊 মিডিয়া রিপোর্ট", callback_data="media_report")],
        [InlineKeyboardButton("🔄 রিফ্রেশ", callback_data="refresh_profile")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        profile_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def game_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /game command"""
    games_list = f"""
🎮 **{BOT_NAME} গেমস**

*নিজের জ্ঞান পরীক্ষা করুন:*

1. 🧠 *কুইজ গেম* - সাধারণ জ্ঞান
2. ➗ *গণিত গেম* - গণিত সমাধান  
3. 📖 *ইসলামিক কুইজ* - ইসলামিক জ্ঞান
4. 🎲 *র‍্যান্ডম গেম* - স্পেশাল চ্যালেঞ্জ

🏆 *পুরস্কার:* ৫-২০ পয়েন্ট
⏱️ *সময়:* ৩০ সেকেন্ড
"""
    
    keyboard = [
        [InlineKeyboardButton("🧠 কুইজ গেম", callback_data="game_quiz")],
        [InlineKeyboardButton("➗ গণিত গেম", callback_data="game_math")],
        [InlineKeyboardButton("📖 ইসলামিক কুইজ", callback_data="game_islamic")],
        [InlineKeyboardButton("🎲 র‍্যান্ডম গেম", callback_data="game_random")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        games_list, 
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leaderboard command"""
    leaderboard_text = gaming.get_leaderboard()
    await update.message.reply_text(leaderboard_text, parse_mode="Markdown")

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /daily command"""
    user_id = update.effective_user.id
    success, message = gaming.daily_reward(user_id)
    
    emoji = "🎉" if success else "⚠️"
    await update.message.reply_text(f"{emoji} {message}")

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ai command"""
    if not context.args:
        await update.message.reply_text("ব্যবহার: `/ai [আপনার প্রশ্ন]`", parse_mode="Markdown")
        return
    
    user_message = " ".join(context.args)
    logger.info(f"AI query from {update.effective_user.id}: {user_message}")
    
    # Get AI response
    response = ai_trainer.generate_response(user_message)
    
    # Learn from message
    db.learn_from_message(
        update.effective_chat.id,
        update.effective_user.id,
        user_message
    )
    
    await update.message.reply_text(f"🤖 {response}")

async def media_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /media command"""
    user_id = update.effective_user.id
    report = media.generate_media_report(user_id)
    await update.message.reply_text(report, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    admin = AdminControl(db, context.bot)
    stats_text = await admin.get_bot_stats()
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    admin = AdminControl(db, context.bot)
    await admin.admin_panel(update, context)

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command (owner only)"""
    admin = AdminControl(db, context.bot)
    await admin.broadcast_to_groups(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = f"""
🆘 **{BOT_NAME} সাহায্য**

*মূল কমান্ডসমূহ:*
/start - বট শুরু করুন
/profile - আপনার প্রোফাইল দেখুন
/game - গেম খেলুন
/leaderboard - শীর্ষ খেলোয়াড় দেখুন
/daily - দৈনিক পুরস্কার নিন
/ai [প্রশ্ন] - AI এর সাথে কথা বলুন
/media - মিডিয়া রিপোর্ট দেখুন
/stats - বট পরিসংখ্যান দেখুন
/admin - অ্যাডমিন প্যানেল
/help - সাহায্য দেখুন

*গেমিং সিস্টেম:*
• প্রতি মেসেজ: {GAME_POINTS['message']} পয়েন্ট
• মিডিয়া শেয়ার: {GAME_POINTS['media']} পয়েন্ট
• ভয়েস মেসেজ: {GAME_POINTS['voice']} পয়েন্ট
• গেম জয়: {GAME_POINTS['game_win']} পয়েন্ট

*যোগাযোগ:* বট ওনার
"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ============================================
# 📨 MESSAGE HANDLERS
# ============================================

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    user = update.effective_user
    chat = update.effective_chat
    message = update.message
    
    logger.info(f"Message from {user.id} in {chat.id}: {message.text}")
    
    # Update user stats
    db.update_user_stats(user.id, "message")
    
    # AI Learning
    if message.text and AI_LEARN_ENABLED:
        db.learn_from_message(chat.id, user.id, message.text)
    
    # Media handling
    if message.photo:
        points = await media.update_media_stats(user.id, "photo")
        if random.random() < 0.2:  # 20% chance
            await message.reply_text(f"📸 +{points} পয়েন্ট!")
    elif message.video:
        await media.update_media_stats(user.id, "video")
    elif message.voice:
        points = await media.update_media_stats(user.id, "voice")
        await message.reply_text(f"🎙️ +{points} পয়েন্ট!")
    
    # Auto-reply for certain messages
    if message.text and not message.text.startswith('/'):
        text_lower = message.text.lower()
        
        # Check for greetings
        if any(word in text_lower for word in ["সালাম", "assalam", "salam"]):
            await message.reply_text("ওয়ালাইকুম আসসালাম! 😊")
        elif any(word in text_lower for word in ["ধন্যবাদ", "thank", "thanks"]):
            await message.reply_text("আপনাকেও ধন্যবাদ! 🙏")
        elif any(word in text_lower for word in ["মারপিড", "mar pd"]):
            await message.reply_text("🎭 MAR PD এখানে আছি!")
        
        # AI auto-response (30% chance)
        elif random.random() < 0.3:
            ai_response = ai_trainer.generate_response(message.text)
            if ai_response:
                await message.reply_text(f"🤖 {ai_response}")

async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new chat members"""
    for member in update.message.new_chat_members:
        # If bot was added to group
        if member.id == context.bot.id:
            welcome = f"""
🎭 **{BOT_NAME} গ্রুপে যোগদান!**

*ধন্যবাদ আমাকে অ্যাড করার জন্য!*

🤖 *আমার সুবিধাসমূহ:*
• AI লার্নিং সিস্টেম
• গেমিং ও পয়েন্ট
• গ্রুপ মডারেশন
• মিডিয়া সাপোর্ট

*শুরু করতে:* /start
*সাহায্য:* /help

⚡ *গ্রুপে সক্রিয় থাকুন, পয়েন্ট সংগ্রহ করুন!*
"""
            await update.message.reply_text(welcome, parse_mode="Markdown")
            return
        
        # Welcome new users
        welcome_user = f"""
🎉 **স্বাগতম {member.first_name}!**

{BOT_NAME} গ্রুপে আপনাকে স্বাগতম!

🤖 *বট ব্যবহার করুন:*
/start - শুরু করুন
/profile - প্রোফাইল দেখুন  
/game - গেম খেলুন
/leaderboard - লিডারবোর্ড দেখুন

🎮 *গেম খেলুন, পয়েন্ট সংগ্রহ করুন!*
"""
        await update.message.reply_text(welcome_user, parse_mode="Markdown")

# ============================================
# 🔘 CALLBACK QUERY HANDLER
# ============================================

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user
    
    logger.info(f"Callback from {user.id}: {data}")
    
    # Handle game answers
    if data.startswith("game_answer_"):
        parts = data.split("_")
        game_type = parts[2]
        answer_idx = int(parts[3])
        
        game_info = gaming.mini_game(user.id, game_type)
        correct_answer = game_info["game_data"]["answer"]
        
        if answer_idx == correct_answer:
            points = game_info["game_data"]["points"]
            db.update_user_stats(user.id, "game_win")
            await query.edit_message_text(f"✅ **সঠিক উত্তর!**\n\n🏆 +{points} পয়েন্ট পেলেন! 🎉")
        else:
            await query.edit_message_text(f"❌ **ভুল উত্তর!**\n\nসঠিক উত্তরটি ছিল: {game_info['game_data']['options'][correct_answer]}")
    
    # Handle game hints
    elif data.startswith("game_hint_"):
        game_type = data.split("_")[2]
        hint = gaming.get_game_hint(game_type)
        await query.answer(f"💡 হিন্ট: {hint}", show_alert=True)
    
    # Handle other buttons
    elif data == "play_game":
        await game_command(update, context)
    elif data == "show_leaderboard":
        await leaderboard_command(update, context)
    elif data == "daily_reward":
        await daily_command(update, context)
    elif data == "media_report":
        await media_command(update, context)
    elif data == "refresh_profile":
        await profile_command(update, context)
    elif data == "admin_close":
        await query.edit_message_text("✅ অ্যাডমিন প্যানেল বন্ধ করা হয়েছে")
    
    # Handle game selection
    elif data.startswith("game_"):
        game_type = data.split("_")[1]
        if game_type == "random":
            game_type = random.choice(["quiz", "math", "islamic"])
        
        game_info = gaming.mini_game(user.id, game_type)
        await query.edit_message_text(
            game_info["text"],
            reply_markup=game_info["reply_markup"]
        )
    
    # Handle cancel game
    elif data == "game_cancel":
        await query.edit_message_text("❌ গেম বাতিল করা হয়েছে\n\nনতুন গেম: /game")

# ============================================
# 🚨 ERROR HANDLER
# ============================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Notify owner about critical errors
    if BOT_OWNER_ID:
        try:
            error_msg = f"""
⚠️ **{BOT_NAME} এরর রিপোর্ট**

🔄 আপডেট: {update}
❌ এরর: {context.error}
🕒 সময়: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🤖 স্বয়ংক্রিয় এরর রিপোর্ট
"""
            await context.bot.send_message(
                chat_id=BOT_OWNER_ID,
                text=error_msg[:4000],
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")

# ============================================
# 🚀 BOT INITIALIZATION
# ============================================

def initialize_bot():
    """Initialize and setup bot"""
    print(f"\n{'='*60}")
    print(f"🎭 {BOT_NAME} v{BOT_VERSION}")
    print(f"{'='*60}")
    
    # Validate configuration
    if not validate_configuration():
        sys.exit(1)
    
    print(f"🤖 বট: {BOT_NAME}")
    print(f"👑 ওনার: {BOT_OWNER_ID}")
    print(f"🔐 টোকেন: {'✅' if BOT_TOKEN else '❌'}")
    print(f"🔥 ফায়ারবেস: {'✅' if FIREBASE_API_KEY else '❌'}")
    print(f"🤖 AI লার্নিং: {'✅' if AI_LEARN_ENABLED else '❌'}")
    print(f"🎮 গেমিং: ✅")
    print(f"{'='*60}")
    
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add command handlers
        commands = [
            ("start", start_command),
            ("profile", profile_command),
            ("game", game_command),
            ("leaderboard", leaderboard_command),
            ("daily", daily_command),
            ("ai", ai_command),
            ("media", media_command),
            ("stats", stats_command),
            ("admin", admin_command),
            ("broadcast", broadcast_command),
            ("help", help_command),
            ("marpd", start_command),
            ("points", profile_command),
        ]
        
        for cmd, handler in commands:
            application.add_handler(CommandHandler(cmd, handler))
        
        # Add message handlers
        application.add_handler(MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            handle_new_members
        ))
        
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text_message
        ))
        
        # Add callback handler
        application.add_handler(CallbackQueryHandler(callback_query_handler))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        return application
        
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        raise

# ============================================
# 🎯 MAIN FUNCTION
# ============================================

def main():
    """Main function to run the bot"""
    
    # Check for single instance
    if check_single_instance():
        print("❌ Another instance of MAR PD Bot is already running!")
        print("💡 Please stop other instances first:")
        print("   pm2 stop marpd-bot")
        print("   pkill -f 'python bot.py'")
        print("   rm -f /data/data/com.termux/files/usr/tmp/marpd_bot.lock")
        sys.exit(1)
    
    try:
        # Initialize bot
        print("🚀 Starting MAR PD Bot...")
        app = initialize_bot()
        
        print("✅ Bot initialized successfully!")
        print("📱 Send /start to your bot on Telegram")
        print(f"⚡ Running with {MAX_WORKERS} workers")
        print(f"📊 Logging to: {LOG_FILE}")
        print(f"{'='*60}\n")
        
        # Register cleanup on exit
        import atexit
        atexit.register(cleanup_lock_file)
        
        # Start polling
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            poll_interval=0.5,
            timeout=30
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user (Ctrl+C)")
        cleanup_lock_file()
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.exception("Bot crashed")
        cleanup_lock_file()
        sys.exit(1)

# ============================================
# 🎮 ENTRY POINT
# ============================================

if __name__ == '__main__':
    main()
