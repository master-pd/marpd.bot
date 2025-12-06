#!/usr/bin/env python3
"""
🎭 MAR PD Bot - AI Trainer System
"""

import random
import re
from datetime import datetime
from config import AI_LEARN_ENABLED, MIN_LEARN_LENGTH, AUTO_REPLY_DB
from database import db

class AITrainer:
    """AI learning and response system"""
    
    def __init__(self):
        self.learned_patterns = {}
        self.response_templates = {
            "greeting": [
                "হ্যালো! 🎭 MAR PD এ স্বাগতম!",
                "আসসালামু আলাইকুম! 👑 কেমন আছেন?",
                "হাই! 🃏 কীভাবে সাহায্য করতে পারি?",
                "স্বাগতম! ⚡ আমি MAR PD বট!"
            ],
            "question": [
                "জানি না, তবে শিখব! 🤖",
                "দেখি উত্তর খুঁজে পাই কিনা... 🔍",
                "একটু ভাবতে দিন... 💭",
                "আমি এখনও শিখছি, কিন্তু শীঘ্রই উত্তর দিতে পারব! 📚"
            ],
            "thanks": [
                "আপনাকেও ধন্যবাদ! 😊",
                "জাযাকাল্লাহু খাইরান! 🙏",
                "কিছুই না! 😇",
                "আপনার জন্য সবসময়! 💖"
            ],
            "marpd": [
                "🎭 MAR PD প্রস্তুত আপনার সেবায়!",
                "🃏 আমাকে ডাকছেন? কী করতে পারি?",
                "👑 MAR PD সবসময় এখানে!",
                "⚡ MAR PD লার্নিং মোডে আছে!"
            ],
            "funny": [
                "হাহাহা! 😂",
                "মজার কথা! 🤣",
                "আপনি খুব মজার! 😄",
                "হাসিখুশি থাকুন! 😁"
            ]
        }
        
        print("🤖 AI Trainer initialized")
    
    def generate_response(self, user_message):
        """Generate intelligent response"""
        user_message_lower = user_message.lower()
        
        # 1. Check exact matches in auto-reply DB
        for keyword, response in AUTO_REPLY_DB.items():
            if keyword.lower() in user_message_lower:
                return response
        
        # 2. Check database for learned responses
        db_response = db.get_ai_response(user_message)
        if db_response:
            return db_response
        
        # 3. Check for greeting patterns
        greeting_patterns = ["সালাম", "হ্যালো", "হাই", "hello", "hi", "assalam"]
        if any(pattern in user_message_lower for pattern in greeting_patterns):
            return random.choice(self.response_templates["greeting"])
        
        # 4. Check for thanks
        thanks_patterns = ["ধন্যবাদ", "থ্যাংক", "শুকরিয়া", "thank", "thanks"]
        if any(pattern in user_message_lower for pattern in thanks_patterns):
            return random.choice(self.response_templates["thanks"])
        
        # 5. Check for MAR PD mentions
        marpd_patterns = ["মারপিড", "mar pd", "marpd", "বট", "bot"]
        if any(pattern in user_message_lower for pattern in marpd_patterns):
            return random.choice(self.response_templates["marpd"])
        
        # 6. Check for questions
        question_indicators = ["কি", "কেন", "কিভাবে", "কোথায়", "কখন", "?", "what", "how", "why"]
        if any(indicator in user_message_lower for indicator in question_indicators):
            return random.choice(self.response_templates["question"])
        
        # 7. Check for funny/emotional content
        funny_words = ["হাসি", "কমেডি", "মজা", "funny", "lol", "haha", "😂", "😄"]
        if any(word in user_message_lower for word in funny_words):
            return random.choice(self.response_templates["funny"])
        
        # 8. Generate context-aware response
        return self._generate_context_response(user_message)
    
    def _generate_context_response(self, message):
        """Generate context-aware response"""
        words = message.split()
        
        if len(words) <= 3:
            # Short message responses
            short_responses = [
                "বুঝলাম! 👍",
                "ঠিক আছে! 👌",
                "জানি! 🤔",
                "মজার! 😄",
                "চমৎকার! ✨"
            ]
            return random.choice(short_responses)
        
        elif len(words) <= 10:
            # Medium message responses
            medium_responses = [
                "আপনার কথার অর্থ বুঝতে পারছি! 🤖",
                "এটা খুবই ইন্টারেস্টিং! 😮",
                "এটা নিয়ে ভাবছি... 💭",
                "গ্রুপ থেকে শিখব এই বিষয়টা! 📚",
                "MAR PD এই বিষয়ে শিখবে! 🎓"
            ]
            return random.choice(medium_responses)
        
        else:
            # Long message responses
            long_responses = [
                "আপনি বিস্তারিত বলেছেন! আমি এটা শিখে রাখলাম! 📝",
                "বেশি লম্বা মেসেজ! আমি মূল অংশটি শিখব! 🧠",
                "ধন্যবাদ শেয়ার করার জন্য! MAR PD লার্ন করেছে! ✅",
                "আপনার কথাবার্তা থেকে শিখছি! 🤖",
                "গ্রুপের জ্ঞান ভাণ্ডার বাড়ছে! 📚"
            ]
            return random.choice(long_responses)
    
    def extract_keywords(self, text):
        """Extract important keywords from text"""
        # Remove common words
        stop_words = {"এবং", "বা", "কিন্তু", "যদি", "তবে", "এই", "যে", "আমি", "তুমি", "সে"}
        
        words = re.findall(r'[\u0980-\u09FFa-zA-Z]+', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:5]  # Return top 5 keywords
    
    def should_learn(self, message):
        """Determine if message should be learned"""
        if not AI_LEARN_ENABLED:
            return False
        
        if len(message) < MIN_LEARN_LENGTH:
            return False
        
        # Check for important content
        important_indicators = [
            "জানেন", "জানি", "শিখুন", "শিখবেন", "প্রশ্ন", "উত্তর",
            "know", "learn", "question", "answer", "explain", "tell"
        ]
        
        has_important = any(indicator in message.lower() for indicator in important_indicators)
        has_question = "?" in message
        
        return has_important or has_question
    
    def get_learning_stats(self):
        """Get AI learning statistics"""
        return {
            "templates": len(self.response_templates),
            "auto_replies": len(AUTO_REPLY_DB),
            "patterns": len(self.learned_patterns),
            "enabled": AI_LEARN_ENABLED
        }

# Global AI instance
ai_trainer = AITrainer()