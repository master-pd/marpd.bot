#!/usr/bin/env python3
"""
🎭 MAR PD Bot - Gaming System
"""

import random
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import PROFILE_BACKGROUNDS, GAME_POINTS, BOT_NAME
from database import db

class GamingSystem:
    """Gaming and points system"""
    
    def __init__(self):
        self.bot_name = BOT_NAME
        print(f"🎮 Gaming system initialized for {BOT_NAME}")
    
    def generate_profile_card(self, user_data):
        """Generate user profile card"""
        # Get user data
        user_id = user_data.get('user_id', 'Unknown')
        first_name = user_data.get('first_name', 'User')
        points = int(user_data.get('points', 0))
        level = int(user_data.get('level', 1))
        message_count = int(user_data.get('message_count', 0))
        games_won = int(user_data.get('games_won', 0))
        daily_login = int(user_data.get('daily_login', 0))
        
        # Select random theme
        theme = random.choice(PROFILE_BACKGROUNDS)
        
        # Calculate progress
        level_points = level * 100
        current_progress = points % 100
        next_level_points = level_points - points
        
        # Determine rank
        if points >= 5000:
            rank = "🎭 MAR PD কিং"
            rank_emoji = "👑"
        elif points >= 2000:
            rank = "⚡ MAR PD লিজেন্ড"
            rank_emoji = "⚡"
        elif points >= 1000:
            rank = "🔥 MAR PD হিরো"
            rank_emoji = "🔥"
        elif points >= 500:
            rank = "⭐ MAR PD প্রো"
            rank_emoji = "⭐"
        elif points >= 100:
            rank = "🌱 MAR প্লেয়ার"
            rank_emoji = "🌱"
        else:
            rank = "🌿 MAR PD নিউবি"
            rank_emoji = "🌿"
        
        # Create progress bar
        progress_percent = min(100, current_progress)
        filled = int(progress_percent / 10)
        progress_bar = "█" * filled + "░" * (10 - filled)
        
        # Generate profile
        profile = f"""
{theme*3} **{self.bot_name} প্রোফাইল** {theme*3}

{rank_emoji} **{first_name}**
├─ **র‍্যাঙ্ক:** {rank}
├─ **লেভেল:** {level}
├─ **পয়েন্ট:** {points}
├─ **মেসেজ:** {message_count}
└─ **প্রোগ্রেস:** {progress_bar} {progress_percent}%

📊 **স্ট্যাটিসটিক্স:**
• 🎮 গেম জয়: {games_won}
• 📅 ডেইলি স্ট্রিক: {daily_login} দিন
• 🔊 ভয়েস মেসেজ: {user_data.get('voice_count', 0)}
• 🖼️ মিডিয়া: {user_data.get('media_count', 0)}

🏆 **পরবর্তী লেভেল:** {next_level_points if next_level_points > 0 else 0} পয়েন্ট বাকি
"""
        
        return profile
    
    def get_leaderboard(self, limit=10):
        """Generate leaderboard"""
        leaderboard = f"""
🏆 **{self.bot_name} লিডারবোর্ড** 🏆

**শীর্ষ {limit} জন খেলোয়াড়:**

"""
        
        # Simulated leaderboard (in real app, fetch from DB)
        rankings = [
            ("🎭 MAR PD কিং", 5000),
            ("⚡ MAR PD লিজেন্ড", 4500),
            ("🔥 MAR PD হিরো", 4000),
            ("⭐ MAR PD প্রো", 3500),
            ("🌱 MAR প্লেয়ার", 3000),
            ("🏅 Gold Player", 2500),
            ("🥈 Silver Player", 2000),
            ("🥉 Bronze Player", 1500),
            ("🎯 Active User", 1000),
            ("🚀 New Star", 500)
        ]
        
        for i, (name, points) in enumerate(rankings[:limit], 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            leaderboard += f"{medal} {name} - {points} পয়েন্ট\n"
        
        leaderboard += f"""
{'='*30}

⚡ **পয়েন্ট পেতে:**
• মেসেজ: {GAME_POINTS['message']} পয়েন্ট
• মিডিয়া: {GAME_POINTS['media']} পয়েন্ট  
• ভয়েস: {GAME_POINTS['voice']} পয়েন্ট
• গেম জয়: {GAME_POINTS['game_win']} পয়েন্ট
• ডেইলি লগিন: {GAME_POINTS['daily_login']} পয়েন্ট

🎮 **টিপস:** নিয়মিত একটিভ থাকুন!
"""
        
        return leaderboard
    
    def daily_reward(self, user_id):
        """Give daily reward to user"""
        user = db.get_user(user_id) or {}
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if already claimed today
        last_reward = user.get('last_daily_reward', '')
        if last_reward == today:
            return False, "⚠️ আজকের রিওয়ার্ড ইতিমধ্যে নিয়েছেন!"
        
        # Calculate reward
        daily_streak = int(user.get('daily_login', 0))
        base_points = GAME_POINTS['daily_login']
        
        # Streak bonuses
        if daily_streak >= 30:
            bonus_multiplier = 5
            streak_message = "🔥 ৩০ দিন স্ট্রিক! অসাধারণ!"
        elif daily_streak >= 14:
            bonus_multiplier = 3
            streak_message = "🌟 ২ সপ্তাহ স্ট্রিক! দারুণ!"
        elif daily_streak >= 7:
            bonus_multiplier = 2
            streak_message = "⭐ ৭ দিন স্ট্রিক! ভালো করছেন!"
        else:
            bonus_multiplier = 1
            streak_message = "👍 ধারাবাহিকতা রাখুন!"
        
        total_points = base_points * bonus_multiplier
        
        # Update user
        user['last_daily_reward'] = today
        user['daily_login'] = str(daily_streak + 1)
        user['points'] = str(int(user.get('points', 0)) + total_points)
        
        # Save to database
        db.save_user(user)
        
        # Prepare message
        message = f"""
🎉 **ডেইলি রিওয়ার্ড!**

🏆 পয়েন্ট পেলেন: {total_points}
📅 স্ট্রিক: {daily_streak + 1} দিন
{streak_message}

✨ আগামীকাল আবার আসবেন!
"""
        
        return True, message
    
    def mini_game(self, user_id, game_type="quiz"):
        """Create mini game"""
        games = {
            "quiz": {
                "question": "বাংলাদেশের রাজধানীর নাম কী?",
                "options": ["ঢাকা", "চট্টগ্রাম", "খুলনা", "রাজশাহী"],
                "answer": 0,
                "points": 10,
                "hint": "এটা একটি মহানগরী"
            },
            "math": {
                "question": "১৫ + ২৫ × ২ = ?",
                "options": ["৬৫", "৭০", "৮০", "৫৫"],
                "answer": 0,  # 15 + (25×2) = 15 + 50 = 65
                "points": 15,
                "hint": "BODMAS নিয়ম অনুসরণ করুন"
            },
            "islamic": {
                "question": "ইসলামের কয়টি রুকন বা স্তম্ভ আছে?",
                "options": ["৪", "৫", "৬", "৭"],
                "answer": 1,
                "points": 20,
                "hint": "শাহাদাহ, নামাজ, রোজা, জাকাত, হজ্জ"
            },
            "general": {
                "question": "সূর্য কি গ্রহ নাকি নক্ষত্র?",
                "options": ["গ্রহ", "নক্ষত্র", "উপগ্রহ", "ধূমকেতু"],
                "answer": 1,
                "points": 12,
                "hint": "এটা আলো ও তাপ উৎপন্ন করে"
            }
        }
        
        # If random game type, pick one
        if game_type == "random":
            game_type = random.choice(list(games.keys()))
        
        game = games.get(game_type, games["quiz"])
        
        # Create keyboard with options
        keyboard = []
        emojis = ["🅰", "🅱", "🅲", "🅳"]
        
        for i, option in enumerate(game["options"]):
            keyboard.append([
                InlineKeyboardButton(
                    f"{emojis[i]} {option}",
                    callback_data=f"game_answer_{game_type}_{i}"
                )
            ])
        
        # Add hint and cancel buttons
        keyboard.append([
            InlineKeyboardButton("💡 হিন্ট দেখুন", callback_data=f"game_hint_{game_type}"),
            InlineKeyboardButton("❌ বাতিল", callback_data="game_cancel")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Game text
        game_text = f"""
🎮 **{self.bot_name} গেম**

📝 প্রশ্ন: {game['question']}

🏆 পুরস্কার: {game['points']} পয়েন্ট
⏱️ সময়: ৩০ সেকেন্ড
🎯 ধরন: {game_type.title()}
"""
        
        return {
            "text": game_text,
            "reply_markup": reply_markup,
            "game_data": game
        }
    
    def get_game_hint(self, game_type):
        """Get hint for game"""
        games = {
            "quiz": "বাংলাদেশের সবচেয়ে বড় শহর",
            "math": "গুণ আগে, যোগ পরে",
            "islamic": "মৌলিক পাঁচটি বিষয়",
            "general": "আমাদের সৌরজগতের কেন্দ্র"
        }
        return games.get(game_type, "চিন্তা করুন...")

# Create global gaming instance
gaming = GamingSystem()