#!/usr/bin/env python3
"""
🎭 MAR PD Bot - Main File
"""

import logging
import random
import asyncio
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

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================== COMMAND HANDLERS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - Welcome message"""
    user = update.effective_user
    chat = update.effective_chat
    
    logger.info(f"New user: {user.id} - {user.first_name}")
    
    # User data
    user_data = {
        "user_id": str(user.id),
        "username": user.username or "",
        "first_name": user.first_name,
        "join_date": datetime.now().isoformat(),
        "message_count": "0",
        "points": "100",
        "level": "1",
        "last_active": datetime.now().isoformat(),
        "is_bot_owner": "true" if user.id == BOT_OWNER_ID else "false",
        "bot_name": BOT_NAME
    }
    
    # Save to database
    db.save_user(user_data)
    
    # Welcome message
    welcome = f"""
🎭 **{BOT_NAME} v{BOT_VERSION}** 🎭

*স্বাগতম {user.first_name}!* 

🤖 *বটের ফিচারসমূহ:*
• 🧠 AI লার্নিং সিস্টেম
• 🎮 গেমিং ও পয়েন্ট
• 👑 অ্যাডমিন কন্ট্রোল
• 📸 মিডিয়া সাপোর্ট
• 📊 গ্রুপ এনালিটিক্স

📋 *কমান্ড লিস্ট:*
/start - বট শুরু করুন
/profile - প্রোফাইল দেখুন  
/game - গেম খেলুন
/leaderboard - লিডারবোর্ড
/daily - ডেইলি রিওয়ার্ড
/ai [text] - AI কে প্রশ্ন করুন
/media - মিডিয়া রিপোর্ট
/stats - স্ট্যাটিসটিক্স
/admin - অ্যাডমিন প্যানেল

⚡ *শুরুতে ১০০ পয়েন্ট বোনাস পেলেন!*
"""
    
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User profile command"""
    user = update.effective_user
    user_data = db.get_user(user.id) or {}
    
    # Generate profile
    profile_text = gaming.generate_profile_card(user_data)
    
    # Create buttons
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

async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Game command"""
    games_list = f"""
🎮 **{BOT_NAME} গেমস**

*গেম নির্বাচন করুন:*

1. 🧠 *কুইজ গেম* - সাধারণ জ্ঞান
2. ➗ *গণিত গেম* - গণিত সমাধান  
3. 📖 *ইসলামিক কুইজ* - ইসলামিক প্রশ্ন
4. 🎲 *র‍্যান্ডম গেম* - স্ট্রাইক গেম

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

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Leaderboard command"""
    leaderboard_text = gaming.get_leaderboard()
    await update.message.reply_text(leaderboard_text, parse_mode="Markdown")

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Daily reward command"""
    user_id = update.effective_user.id
    success, message = gaming.daily_reward(user_id)
    
    emoji = "🎉" if success else "⚠️"
    await update.message.reply_text(f"{emoji} {message}")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """AI chat command"""
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

async def media_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Media report command"""
    user_id = update.effective_user.id
    report = media.generate_media_report(user_id)
    await update.message.reply_text(report, parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot statistics"""
    admin = AdminControl(db, context.bot)
    stats_text = await admin.get_bot_stats()
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel"""
    admin = AdminControl(db, context.bot)
    await admin.admin_panel(update, context)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast to groups (owner only)"""
    admin = AdminControl(db, context.bot)
    await admin.broadcast_to_groups(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = f"""
🆘 **{BOT_NAME} সাহায্য**

*মূল কমান্ডসমূহ:*
/start - বট শুরু করুন
/profile - আপনার প্রোফাইল দেখুন
/game - গেম খেলুন
/leaderboard - শীর্ষ খেলোয়াড়
/daily - দৈনিক পুরস্কার
/ai [প্রশ্ন] - AI এর সাথে কথা বলুন
/media - মিডিয়া রিপোর্ট
/stats - বট পরিসংখ্যান
/admin - অ্যাডমিন প্যানেল
/help - সাহায্য

*গেমিং সিস্টেম:*
• প্রতি মেসেজ: {GAME_POINTS['message']} পয়েন্ট
• মিডিয়া শেয়ার: {GAME_POINTS['media']} পয়েন্ট
• ভয়েস মেসেজ: {GAME_POINTS['voice']} পয়েন্ট
• গেম জয়: {GAME_POINTS['game_win']} পয়েন্ট

*যোগাযোগ:* বট ওনার
"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ================== MESSAGE HANDLER ==================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    """Handle new members in group"""
    for member in update.message.new_chat_members:
        # If bot was added
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

# ================== CALLBACK HANDLER ==================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    # Handle other buttons
    elif data == "play_game":
        await game(update, context)
    elif data == "show_leaderboard":
        await leaderboard(update, context)
    elif data == "daily_reward":
        await daily(update, context)
    elif data == "media_report":
        await media_report(update, context)
    elif data == "refresh_profile":
        await profile(update, context)
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

# ================== ERROR HANDLER ==================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Notify owner about critical errors
    if BOT_OWNER_ID:
        try:
            error_msg = f"⚠️ **বট এরর:**\n\n{context.error}"
            await context.bot.send_message(
                chat_id=BOT_OWNER_ID,
                text=error_msg[:4000]  # Telegram limit
            )
        except:
            pass

# ================== MAIN FUNCTION ==================

def main():
    """Start the bot"""
    print(f"\n{'='*60}")
    print(f"🎭 {BOT_NAME} v{BOT_VERSION}")
    print(f"{'='*60}")
    print(f"🤖 Owner: {BOT_OWNER_ID}")
    print(f"📱 Starting bot...")
    print(f"🔥 Firebase: {PROJECT_ID[:10]}..." if PROJECT_ID else "🔥 Firebase: Disabled")
    print(f"🤖 AI Learning: {'Enabled' if AI_LEARN_ENABLED else 'Disabled'}")
    print(f"{'='*60}")
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    commands = [
        ("start", start),
        ("profile", profile),
        ("game", game),
        ("leaderboard", leaderboard),
        ("daily", daily),
        ("ai", ai_chat),
        ("media", media_report),
        ("stats", stats),
        ("admin", admin),
        ("broadcast", broadcast),
        ("help", help_command),
        ("marpd", start),
        ("points", profile),
    ]
    
    for cmd, handler in commands:
        app.add_handler(CommandHandler(cmd, handler))
    
    # Add message handlers
    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        handle_new_members
    ))
    
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))
    
    # Add callback handler
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Start the bot
    print(f"✅ Bot started successfully!")
    print(f"📱 Send /start to begin")
    print(f"⚡ Running with {MAX_WORKERS} workers")
    print(f"{'='*60}\n")
    
    # Start polling
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.exception("Bot crashed")