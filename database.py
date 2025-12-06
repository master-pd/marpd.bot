#!/usr/bin/env python3
"""
🎭 MAR PD Bot - Database Handler
"""

import requests
import json
import time
from datetime import datetime
import random
from config import *

class MARPDDatabase:
    """Firestore database handler for MAR PD Bot"""
    
    def __init__(self):
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
        self.api_key = FIREBASE_API_KEY
        self.bot_name = BOT_NAME
        self.cache = {}
        
        if not FIREBASE_API_KEY or not PROJECT_ID:
            print("⚠️ Firebase not configured - using simulated database")
            self.firebase_enabled = False
        else:
            self.firebase_enabled = True
            print(f"🔥 Firebase connected: {PROJECT_ID}")
    
    # ================== USER MANAGEMENT ==================
    
    def save_user(self, user_data):
        """Save user to database"""
        if not self.firebase_enabled:
            # Simulate save for testing
            print(f"📝 Simulated save: {user_data.get('user_id', 'unknown')}")
            return True
        
        try:
            user_id = user_data['user_id']
            url = f"{self.base_url}/marpd_users/{user_id}"
            
            # Convert data to Firestore format
            fields = {}
            for key, value in user_data.items():
                if isinstance(value, str):
                    fields[key] = {"stringValue": value}
                elif isinstance(value, int):
                    fields[key] = {"integerValue": str(value)}
                elif isinstance(value, bool):
                    fields[key] = {"booleanValue": value}
                else:
                    fields[key] = {"stringValue": str(value)}
            
            data = {"fields": fields}
            params = {"key": self.api_key}
            
            response = requests.patch(url, params=params, json=data, timeout=10)
            
            if response.status_code == 200:
                # Update cache
                cache_key = f"user_{user_id}"
                self.cache[cache_key] = {
                    'data': user_data,
                    'timestamp': time.time()
                }
                return True
            else:
                print(f"❌ Firestore error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️ Database error: {e}")
            return False
    
    def get_user(self, user_id):
        """Get user from database"""
        # Check cache first
        cache_key = f"user_{user_id}"
        if CACHE_ENABLED and cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached['timestamp'] < CACHE_TTL:
                return cached['data']
        
        if not self.firebase_enabled:
            # Return simulated user for testing
            return {
                'user_id': str(user_id),
                'first_name': 'User',
                'points': random.randint(0, 100),
                'level': random.randint(1, 5),
                'message_count': random.randint(0, 50)
            }
        
        try:
            url = f"{self.base_url}/marpd_users/{user_id}"
            params = {"key": self.api_key}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'fields' in data:
                    user_data = {}
                    for key, value in data['fields'].items():
                        if 'stringValue' in value:
                            user_data[key] = value['stringValue']
                        elif 'integerValue' in value:
                            user_data[key] = int(value['integerValue'])
                        elif 'booleanValue' in value:
                            user_data[key] = value['booleanValue']
                    
                    user_data['user_id'] = str(user_id)
                    
                    # Update cache
                    if CACHE_ENABLED:
                        self.cache[cache_key] = {
                            'data': user_data,
                            'timestamp': time.time()
                        }
                    
                    return user_data
                    
        except Exception as e:
            print(f"⚠️ Get user error: {e}")
        
        return None
    
    def update_user_stats(self, user_id, stat_type="message"):
        """Update user statistics"""
        user = self.get_user(user_id) or {}
        
        # Initialize if new user
        if 'user_id' not in user:
            user = {
                'user_id': str(user_id),
                'first_name': 'User',
                'username': '',
                'points': 0,
                'level': 1,
                'message_count': 0,
                'games_won': 0,
                'daily_login': 0,
                'created_at': datetime.now().isoformat()
            }
        
        # Add points based on activity
        points = GAME_POINTS.get(stat_type, 1)
        current_points = int(user.get('points', 0))
        user['points'] = current_points + points
        
        # Update specific counters
        if stat_type == "message":
            user['message_count'] = int(user.get('message_count', 0)) + 1
        elif stat_type == "game_win":
            user['games_won'] = int(user.get('games_won', 0)) + 1
        elif stat_type == "daily_login":
            user['daily_login'] = int(user.get('daily_login', 0)) + 1
        
        # Level up system
        level = int(user.get('level', 1))
        required_points = level * 100
        if user['points'] >= required_points:
            user['level'] = level + 1
            user['level_up_date'] = datetime.now().isoformat()
            print(f"🎉 Level up! User {user_id} reached level {user['level']}")
        
        # Update timestamp
        user['last_active'] = datetime.now().isoformat()
        user['bot_name'] = self.bot_name
        
        # Save to database
        success = self.save_user(user)
        
        if success and stat_type == "game_win":
            print(f"🏆 Game win! User {user_id} earned {points} points")
        
        return success
    
    # ================== AI LEARNING SYSTEM ==================
    
    def learn_from_message(self, chat_id, user_id, message_text):
        """Save message for AI learning"""
        if not AI_LEARN_ENABLED:
            return False
        
        if len(message_text) < MIN_LEARN_LENGTH or len(message_text) > MAX_LEARN_LENGTH:
            return False
        
        # Filter unimportant messages
        important_keywords = ["কি", "কেন", "কিভাবে", "কোথায়", "কখন", "জানেন", "?",
                             "what", "how", "why", "when", "where", "explain"]
        
        if not any(keyword in message_text.lower() for keyword in important_keywords):
            return False
        
        if not self.firebase_enabled:
            # Simulate learning for testing
            return True
        
        try:
            # Create unique document ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            random_num = random.randint(1000, 9999)
            doc_id = f"learn_{timestamp}_{random_num}"
            
            url = f"{self.base_url}/marpd_learning/{doc_id}"
            
            # Prepare learning data
            learn_data = {
                "text": message_text,
                "chat_id": str(chat_id),
                "user_id": str(user_id),
                "timestamp": datetime.now().isoformat(),
                "bot": self.bot_name,
                "language": "bangla" if any(ord(c) > 127 for c in message_text) else "english"
            }
            
            # Convert to Firestore format
            fields = {}
            for key, value in learn_data.items():
                fields[key] = {"stringValue": str(value)}
            
            data = {"fields": fields}
            params = {"key": self.api_key}
            
            response = requests.patch(url, params=params, json=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"⚠️ AI learning error: {e}")
            return False
    
    def get_ai_response(self, user_message):
        """Get AI response from learned data"""
        if not self.firebase_enabled:
            return None
        
        try:
            url = f"{self.base_url}/marpd_learning"
            params = {
                "key": self.api_key,
                "pageSize": 20,
                "orderBy": "timestamp desc"
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if "documents" in data:
                    # Search for similar messages
                    user_words = set(user_message.lower().split())
                    
                    for doc in data["documents"]:
                        if "fields" in doc:
                            learned_text = doc["fields"].get("text", {}).get("stringValue", "")
                            learned_words = set(learned_text.lower().split())
                            
                            # Check for word overlap
                            common_words = user_words.intersection(learned_words)
                            if len(common_words) >= 2:  # At least 2 common words
                                responses = [
                                    f"🎭 আমি এই বিষয়ে কিছু জানি!",
                                    f"🃏 গ্রুপ থেকে শিখেছি এই কথাটা!",
                                    f"👑 হ্যাঁ, এটা তো জানা কথা!",
                                    f"⚡ এটা সম্পর্কে আমার জানা আছে!"
                                ]
                                return random.choice(responses)
            
            return None
            
        except Exception as e:
            print(f"⚠️ AI response error: {e}")
            return None
    
    # ================== GROUP ANALYTICS ==================
    
    def save_group_activity(self, group_id, group_title, activity_type, details=""):
        """Save group activity for analytics"""
        if not self.firebase_enabled:
            return True
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            doc_id = f"group_{group_id}_{timestamp}"
            
            url = f"{self.base_url}/marpd_groups/{doc_id}"
            
            activity_data = {
                "group_id": str(group_id),
                "group_title": group_title,
                "activity_type": activity_type,
                "details": details,
                "timestamp": datetime.now().isoformat(),
                "bot": self.bot_name
            }
            
            fields = {}
            for key, value in activity_data.items():
                fields[key] = {"stringValue": str(value)}
            
            data = {"fields": fields}
            params = {"key": self.api_key}
            
            response = requests.patch(url, params=params, json=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"⚠️ Group analytics error: {e}")
            return False

# Create global database instance
db = MARPDDatabase()