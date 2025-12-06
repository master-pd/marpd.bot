#!/usr/bin/env python3
"""
🎭 MAR PD Bot - Media Handler System
"""

import random
from config import PROFILE_BACKGROUNDS, GAME_POINTS, BOT_NAME
from database import db

class MediaHandler:
    """Media and file handling system"""
    
    def __init__(self):
        self.bot_name = BOT_NAME
        print(f"📸 Media handler initialized for {BOT_NAME}")
    
    async def update_media_stats(self, user_id, media_type):
        """Update media statistics for user"""
        user = db.get_user(user_id) or {}
        
        # Define points for each media type
        points_map = {
            "photo": GAME_POINTS["media"],
            "video": GAME_POINTS["media"],
            "voice": GAME_POINTS["voice"],
            "document": 2,
            "sticker": 1,
            "animation": 3
        }
        
        points = points_map.get(media_type, 1)
        
        # Update specific counters
        if media_type == "photo":
            count = int(user.get('photo_count', 0)) + 1
            user['photo_count'] = str(count)
        elif media_type == "video":
            count = int(user.get('video_count', 0)) + 1
            user['video_count'] = str(count)
        elif media_type == "voice":
            count = int(user.get('voice_count', 0)) + 1
            user['voice_count'] = str(count)
        elif media_type == "document":
            count = int(user.get('document_count', 0)) + 1
            user['document_count'] = str(count)
        elif media_type == "sticker":
            count = int(user.get('sticker_count', 0)) + 1
            user['sticker_count'] = str(count)
        elif media_type == "animation":
            count = int(user.get('animation_count', 0)) + 1
            user['animation_count'] = str(count)
        
        # Add points
        current_points = int(user.get('points', 0))
        user['points'] = str(current_points + points)
        
        # Save to database
        db.save_user(user)
        
        return points
    
    def generate_media_report(self, user_id):
        """Generate media usage report"""
        user = db.get_user(user_id) or {}
        
        # Calculate totals
        photo_count = int(user.get('photo_count', 0))
        video_count = int(user.get('video_count', 0))
        voice_count = int(user.get('voice_count', 0))
        document_count = int(user.get('document_count', 0))
        sticker_count = int(user.get('sticker_count', 0))
        animation_count = int(user.get('animation_count', 0))
        
        total_media = (photo_count + video_count + voice_count + 
                      document_count + sticker_count + animation_count)
        
        # Calculate points earned from media
        photo_points = photo_count * GAME_POINTS["media"]
        video_points = video_count * GAME_POINTS["media"]
        voice_points = voice_count * GAME_POINTS["voice"]
        document_points = document_count * 2
        sticker_points = sticker_count * 1
        animation_points = animation_count * 3
        
        total_points = (photo_points + video_points + voice_points + 
                       document_points + sticker_points + animation_points)
        
        # Generate report
        report = f"""
📊 **{self.bot_name} মিডিয়া রিপোর্ট**

📈 *মিডিয়া স্ট্যাটস:*
• 🖼️ ফটো: {photo_count}
• 🎥 ভিডিও: {video_count}
• 🎙️ ভয়েস: {voice_count}
• 📁 ডকুমেন্ট: {document_count}
• 😜 স্টিকার: {sticker_count}
• 🎬 অ্যানিমেশন: {animation_count}

📊 *সারাংশ:*
• মোট মিডিয়া: {total_media}
• মোট পয়েন্ট: {total_points}
• পয়েন্ট/মিডিয়া: {total_points/total_media if total_media > 0 else 0:.1f}

⚡ *পয়েন্ট সিস্টেম:*
• ফটো/ভিডিও: {GAME_POINTS['media']} পয়েন্ট
• ভয়েস মেসেজ: {GAME_POINTS['voice']} পয়েন্ট
• ডকুমেন্ট: ২ পয়েন্ট
• অ্যানিমেশন: ৩ পয়েন্ট
• স্টিকার: ১ পয়েন্ট

🎯 *টিপস:*
• বেশি মিডিয়া শেয়ার করুন
• ভয়েস মেসেজে বেশি পয়েন্ট পাবেন
• নিয়মিত শেয়ার করুন
"""
        
        return report
    
    async def handle_profile_picture(self, update, context):
        """Handle user profile picture"""
        try:
            user = update.effective_user
            
            # Try to get profile photos
            photos = await user.get_profile_photos(limit=1)
            
            if photos.total_count > 0:
                # User has profile picture
                photo_file = await photos.photos[0][-1].get_file()
                
                # In a real implementation, you might download or process the photo
                # For now, just return that they have a profile picture
                return True, "Profile picture available"
            
            return False, "No profile picture"
            
        except Exception as e:
            print(f"Profile picture error: {e}")
            return False, "Error checking profile"
    
    def generate_profile_with_media(self, user_data, has_profile_pic=False):
        """Generate enhanced profile with media info"""
        bg = random.choice(PROFILE_BACKGROUNDS)
        
        if has_profile_pic:
            profile_art = """
            ┌──────────────────┐
            │     📸✨         │
            │   প্রোফাইল      │
            │     ছবি         │
            └──────────────────┘
            """
        else:
            profile_art = f"""
            ┌──────────────────┐
            │     {bg}{bg}        │
            │   {user_data.get('first_name', 'User')[:10]:^10}  │
            │     {bg}{bg}        │
            └──────────────────┘
            """
        
        # Media stats
        media_stats = f"""
📱 *মিডিয়া স্ট্যাটস:*
• ফটো: {user_data.get('photo_count', 0)}
• ভিডিও: {user_data.get('video_count', 0)}
• ভয়েস: {user_data.get('voice_count', 0)}
• স্টিকার: {user_data.get('sticker_count', 0)}
"""
        
        profile = f"""
{profile_art}

🎭 **{self.bot_name} প্রোফাইল**

👤 নাম: {user_data.get('first_name', 'User')}
🏆 পয়েন্ট: {user_data.get('points', 0)}
📈 লেভেল: {user_data.get('level', 1)}
💬 মেসেজ: {user_data.get('message_count', 0)}

{media_stats}

{'✅ প্রোফাইল ছবি আছে' if has_profile_pic else '⚠️ ডিফল্ট প্রোফাইল'}
"""
        
        return profile
    
    def get_media_tips(self):
        """Get media sharing tips"""
        tips = [
            "📸 **ফটো শেয়ার করুন:** প্রতিটি ফটোতে {} পয়েন্ট!".format(GAME_POINTS['media']),
            "🎙️ **ভয়েস মেসেজ:** {} পয়েন্ট পান ভয়েসে!".format(GAME_POINTS['voice']),
            "🎬 **ভিডিও শেয়ার:** {} পয়েন্ট প্রতি ভিডিও!".format(GAME_POINTS['media']),
            "📁 **ডকুমেন্ট:** ২ পয়েন্ট প্রতি ফাইলে!",
            "😜 **স্টিকার:** ১ পয়েন্ট প্রতি স্টিকারে!"
        ]
        
        return random.choice(tips)

# Create global media handler instance
media = MediaHandler()