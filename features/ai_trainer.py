import random
import re
from datetime import datetime
from collections import defaultdict

class AITrainer:
    """AI that learns from user messages"""
    
    def __init__(self, db):
        self.db = db
        self.config = Config()
        
        # Knowledge base
        self.responses = []
        self.patterns = defaultdict(list)
        self.context_memory = {}
        
        # Statistics
        self.trained_messages = 0
        self.response_count = 0
        
        # Load initial knowledge
        self._load_base_knowledge()
    
    def _load_base_knowledge(self):
        """Load base Bangla knowledge"""
        # Common greetings
        self.patterns['হ্যালো'].extend([
            "হ্যালো! আমি MAR PD Bot",
            "আসসালামু আলাইকুম",
            "নমস্কার",
            "হাই! কেমন আছেন?"
        ])
        
        self.patterns['কেমন আছ'].extend([
            "আলহামদুলিল্লাহ ভালো! আপনি কেমন আছেন?",
            "ভালো আছি, আপনাকে দেখে ভালো লাগছে",
            "ধন্যবাদ জিজ্ঞাসার জন্য! আমি ঠিক আছি"
        ])
        
        # Bot info
        self.patterns['তোমার নাম'].extend([
            "আমার নাম MAR PD Bot",
            "আমাকে MAR PD Bot বলা হয়",
            "আমি MAR PD Bot, আপনার সহায়ক AI"
        ])
        
        self.patterns['তুমি কে'].extend([
            "আমি একটি AI bot, আমি মানুষের সাথে কথা বলতে শিখছি",
            "আমি MAR PD Bot, আমি চ্যাট করতে পারি এবং গেম খেলতে পারি",
            "আমি একটি বট, আপনার সাথে কথা বলতে পছন্দ করি"
        ])
        
        # Help
        self.patterns['সাহায্য'].extend([
            "আমি কিভাবে আপনাকে সাহায্য করতে পারি?",
            "সাহায্যের জন্য /help লিখুন",
            "আপনি কি গেম খেলতে চান নাকি পয়েন্ট চেক করতে চান?"
        ])
        
        # Common phrases
        self.responses.extend([
            "বুঝতে পারছি",
            "জানি না",
            "আবার বলুন",
            "মজার কথা",
            "ধন্যবাদ",
            "দুঃখিত",
            "ভালো লাগলো",
            "অনেক সুন্দর",
            "আমিও তাই মনে করি",
            "হ্যাঁ ঠিক",
            "না ঠিক না",
            "হতে পারে",
            "কিছু মনে করবেন না",
            "আমি শিখছি",
            "আপনার সাথে কথা বলে ভালো লাগছে",
            "আরও বলুন",
            "বুঝলাম",
            "জানি",
            "জানিনা",
            "আসুন গেম খেলি"
        ])
    
    async def learn_from_message(self, user_id: int, message: str):
        """Learn from user message"""
        if not self.config.AI_LEARNING_ENABLED:
            return
        
        # Basic validation
        if len(message) < self.config.MIN_LEARN_LENGTH:
            return
        if len(message) > self.config.MAX_LEARN_LENGTH:
            return
        
        # Clean message
        message = message.strip()
        
        # Check if Bangla
        if not self._is_bangla(message):
            return  # Only learn Bangla for now
        
        # Store in database for later training
        await self.db.log_message(user_id, message)
        
        # Immediate learning (simple)
        self._learn_immediate(message)
        
        self.trained_messages += 1
    
    def _learn_immediate(self, message: str):
        """Immediate learning from message"""
        # Add to responses if unique
        if message not in self.responses:
            self.responses.append(message)
            
            # Limit responses
            if len(self.responses) > self.config.AI_RESPONSE_LIMIT:
                self.responses = self.responses[-self.config.AI_RESPONSE_LIMIT:]
        
        # Extract patterns
        words = message.split()
        if len(words) >= 2:
            # Use first word as pattern
            first_word = words[0]
            if len(first_word) > 2:
                if message not in self.patterns[first_word]:
                    self.patterns[first_word].append(message)
    
    async def train_from_database(self):
        """Train AI from database messages"""
        messages = await self.db.get_training_messages(limit=500)
        
        for message in messages:
            self._learn_immediate(message)
        
        print(f"🤖 AI trained with {len(messages)} new messages")
        print(f"📊 Total responses: {len(self.responses)}")
        print(f"📊 Total patterns: {len(self.patterns)}")
    
    async def get_response(self, user_message: str, user_id: int = None) -> str:
        """Get AI response"""
        self.response_count += 1
        
        # Clean message
        user_message = user_message.strip().lower()
        
        # 1. Check for exact pattern match
        for pattern, responses in self.patterns.items():
            if pattern in user_message:
                return random.choice(responses)
        
        # 2. Check for keyword matches
        keywords = ['নাম', 'কেমন', 'কি', 'কেন', 'কোথায়', 'কখন', 'কিভাবে']
        for keyword in keywords:
            if keyword in user_message:
                # Find responses containing this keyword
                matching_responses = [r for r in self.responses if keyword in r]
                if matching_responses:
                    return random.choice(matching_responses)
        
        # 3. Check for question patterns
        if user_message.endswith('?'):
            question_responses = [
                "জানি না",
                "ভালো প্রশ্ন",
                "আমি নিশ্চিত নই",
                "আপনি কী মনে করেন?",
                "আরও তথ্য দিতে হবে",
                "এটা কঠিন প্রশ্ন"
            ]
            return random.choice(question_responses)
        
        # 4. Get random response from learned data
        if self.responses:
            # Weight recent responses higher
            recent_responses = self.responses[-100:] if len(self.responses) > 100 else self.responses
            return random.choice(recent_responses)
        
        # 5. Fallback responses
        fallbacks = [
            "আমি এখনো শিখছি, আবার চেষ্টা করুন",
            "বুঝতে পারলাম না, সহজ করে বলুন",
            "আপনি কি গেম খেলতে চান? /game লিখুন",
            "আমার সাথে আরও কথা বলুন, আমি শিখব",
            "আপনার বার্তা পেয়েছি, আমি একটি AI বট"
        ]
        
        return random.choice(fallbacks)
    
    async def get_conversation_response(self, user_id: int, message: str) -> str:
        """Get response with conversation context"""
        # Get previous context
        context = self.context_memory.get(user_id, [])
        
        # Add current message to context
        context.append(message)
        if len(context) > 5:  # Keep last 5 messages
            context = context[-5:]
        
        self.context_memory[user_id] = context
        
        # Try to respond based on context
        if len(context) >= 2:
            last_message = context[-2]
            if "নাম" in last_message and "নাম" in message:
                return "আপনি আগেই নাম জিজ্ঞাসা করেছেন, আমি MAR PD Bot"
        
        # Get regular response
        response = await self.get_response(message, user_id)
        
        # Add response to context
        context.append(response)
        self.context_memory[user_id] = context
        
        return response
    
    def _is_bangla(self, text: str) -> bool:
        """Check if text is Bangla"""
        bangla_range = r'[\u0980-\u09FF]'
        return bool(re.search(bangla_range, text))
    
    async def get_statistics(self):
        """Get AI statistics"""
        return {
            'trained_messages': self.trained_messages,
            'response_count': self.response_count,
            'total_responses': len(self.responses),
            'total_patterns': len(self.patterns),
            'active_contexts': len(self.context_memory)
        }
    
    async def reset_memory(self):
        """Reset AI memory (keep base knowledge)"""
        self.responses = []
        self.patterns = defaultdict(list)
        self.context_memory = {}
        self._load_base_knowledge()
        print("🤖 AI memory reset")
    
    async def save_knowledge(self, filepath: str):
        """Save AI knowledge to file"""
        import json
        
        knowledge = {
            'responses': self.responses,
            'patterns': dict(self.patterns),
            'stats': {
                'trained_messages': self.trained_messages,
                'response_count': self.response_count,
                'saved_at': datetime.now().isoformat()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)
        
        return True
    
    async def load_knowledge(self, filepath: str):
        """Load AI knowledge from file"""
        import json
        import os
        
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            knowledge = json.load(f)
        
        self.responses = knowledge.get('responses', [])
        self.patterns = defaultdict(list, knowledge.get('patterns', {}))
        
        print(f"🤖 AI knowledge loaded: {len(self.responses)} responses")
        return True