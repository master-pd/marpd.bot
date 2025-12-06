import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class GamingSystem:
    """Gaming System with 20+ Games"""
    
    def __init__(self, db):
        self.db = db
        self.config = Config()
        
        # Game definitions
        self.games = {}
        self.active_games = {}
        self.user_cooldowns = {}
        
        # Load games
        self._load_games()
    
    def _load_games(self):
        """Load all games"""
        # Quiz Games
        self.games['quiz_bangla'] = {
            'name': '🧠 বাংলা কুইজ',
            'description': 'বাংলা ভাষা ও সাহিত্য সম্পর্কিত প্রশ্ন',
            'cost': 5,
            'reward': 15,
            'type': 'quiz'
        }
        
        self.games['quiz_math'] = {
            'name': '🔢 গণিত কুইজ',
            'description': 'সহজ গণিতের প্রশ্ন',
            'cost': 5,
            'reward': 15,
            'type': 'quiz'
        }
        
        self.games['quiz_general'] = {
            'name': '🌍 সাধারণ জ্ঞান',
            'description': 'সাধারণ জ্ঞান প্রশ্ন',
            'cost': 5,
            'reward': 15,
            'type': 'quiz'
        }
        
        # Number Games
        self.games['number_guess'] = {
            'name': '🎯 সংখ্যা অনুমান',
            'description': '১-১০০ এর মধ্যে সংখ্যা অনুমান করুন',
            'cost': 10,
            'reward': 30,
            'type': 'number'
        }
        
        self.games['number_race'] = {
            'name': '🏁 সংখ্যা দৌড়',
            'description': 'দ্রুত সংখ্যা টাইপ করুন',
            'cost': 8,
            'reward': 25,
            'type': 'speed'
        }
        
        # Word Games
        self.games['word_scramble'] = {
            'name': '🔠 শব্দ জগাখিচুড়ি',
            'description': 'জগাখিচুড়ি করা শব্দ সাজান',
            'cost': 7,
            'reward': 20,
            'type': 'word'
        }
        
        self.games['word_find'] = {
            'name': '🔍 শব্দ খুঁজুন',
            'description': 'লুকানো শব্দ খুঁজে বের করুন',
            'cost': 8,
            'reward': 25,
            'type': 'word'
        }
        
        # Card Games
        self.games['card_highlow'] = {
            'name': '🃏 হাই-লো কার্ড',
            'description': 'পরের কার্ড হাই হবে নাকি লো?',
            'cost': 10,
            'reward': 30,
            'type': 'card'
        }
        
        # Luck Games
        self.games['dice_roll'] = {
            'name': '🎲 দাইস রোল',
            'description': 'দাইস রোল করে জিতুন',
            'cost': 5,
            'reward': 20,
            'type': 'luck'
        }
        
        self.games['coin_flip'] = {
            'name': '🪙 কয়েন ফ্লিপ',
            'description': 'হেড নাকি টেল?',
            'cost': 5,
            'reward': 15,
            'type': 'luck'
        }
        
        self.games['slot_machine'] = {
            'name': '🎰 স্লট মেশিন',
            'description': 'স্লট মেশিন স্পিন করুন',
            'cost': 20,
            'reward': 100,
            'type': 'luck'
        }
        
        # Memory Games
        self.games['memory_match'] = {
            'name': '🧩 মেমোরি ম্যাচ',
            'description': 'মেমোরি টেস্ট গেম',
            'cost': 15,
            'reward': 50,
            'type': 'memory'
        }
        
        # Trivia Games
        self.games['trivia_bangladesh'] = {
            'name': '🇧🇩 বাংলাদেশ ট্রিভিয়া',
            'description': 'বাংলাদেশ সম্পর্কিত প্রশ্ন',
            'cost': 5,
            'reward': 20,
            'type': 'trivia'
        }
        
        # Puzzle Games
        self.games['puzzle_solve'] = {
            'name': '🧩 পাজল সমাধান',
            'description': 'ছবি পাজল সমাধান করুন',
            'cost': 12,
            'reward': 40,
            'type': 'puzzle'
        }
        
        # Reaction Games
        self.games['reaction_test'] = {
            'name': '⚡ রিএকশন টেস্ট',
            'description': 'দ্রুত রিএকশন দেখান',
            'cost': 5,
            'reward': 20,
            'type': 'reaction'
        }
        
        # Multiplayer Games
        self.games['tictactoe'] = {
            'name': '❌ টিক ট্যাক টো',
            'description': 'অনলাইন টিক ট্যাক টো',
            'cost': 10,
            'reward': 30,
            'type': 'multiplayer'
        }
        
        self.games['hangman'] = {
            'name': '🪢 হ্যাংম্যান',
            'description': 'ক্লাসিক হ্যাংম্যান গেম',
            'cost': 5,
            'reward': 25,
            'type': 'word'
        }
        
        # Math Games
        self.games['math_quick'] = {
            'name': '➕ দ্রুত গণিত',
            'description': 'দ্রুত গণিত সমাধান করুন',
            'cost': 5,
            'reward': 20,
            'type': 'math'
        }
        
        # Collection Games
        self.games['collect_items'] = {
            'name': '📦 আইটেম কালেক্ট',
            'description': 'আইটেম কালেক্ট করে জিতুন',
            'cost': 8,
            'reward': 30,
            'type': 'collection'
        }
        
        print(f"🎮 Loaded {len(self.games)} games")
    
    async def load_games(self):
        """Load games from database"""
        # Currently using hardcoded games
        return True
    
    async def get_available_games(self) -> List[Dict]:
        """Get list of available games"""
        return list(self.games.values())
    
    async def can_play_game(self, user_id: int, game_id: str) -> Tuple[bool, str]:
        """Check if user can play game"""
        # Check cooldown
        if user_id in self.user_cooldowns:
            last_play = self.user_cooldowns[user_id]
            cooldown = timedelta(seconds=self.config.GAME_COOLDOWN)
            if datetime.now() - last_play < cooldown:
                remaining = cooldown - (datetime.now() - last_play)
                return False, f"⏳ {int(remaining.total_seconds())} সেকেন্ড অপেক্ষা করুন"
        
        # Check game exists
        if game_id not in self.games:
            return False, "❌ গেমটি পাওয়া যায়নি"
        
        # Check user points
        user = await self.db.get_user(user_id)
        if not user:
            return False, "❌ ইউজার ডাটা পাওয়া যায়নি"
        
        game_cost = self.games[game_id]['cost']
        if user.get('points', 0) < game_cost:
            return False, f"❌ {game_cost} পয়েন্ট প্রয়োজন, আপনার আছে {user.get('points', 0)} পয়েন্ট"
        
        # Check daily limit
        daily_games = user.get('stats', {}).get('daily_games', 0)
        if daily_games >= self.config.MAX_GAMES_PER_DAY:
            return False, f"❌ আজকের গেম লিমিট শেষ, আগামীকাল আবার চেষ্টা করুন"
        
        return True, ""
    
    async def start_game(self, user_id: int, game_id: str):
        """Start a game"""
        can_play, message = await self.can_play_game(user_id, game_id)
        if not can_play:
            return None, message
        
        # Deduct points
        game_cost = self.games[game_id]['cost']
        await self.db.deduct_points(user_id, game_cost, f"game_{game_id}_fee")
        
        # Set cooldown
        self.user_cooldowns[user_id] = datetime.now()
        
        # Start game based on type
        game_type = self.games[game_id]['type']
        
        if game_type == 'quiz':
            return await self._start_quiz_game(user_id, game_id)
        elif game_type == 'number':
            return await self._start_number_game(user_id, game_id)
        elif game_type == 'word':
            return await self._start_word_game(user_id, game_id)
        elif game_type == 'luck':
            return await self._start_luck_game(user_id, game_id)
        else:
            return await self._start_default_game(user_id, game_id)
    
    async def _start_quiz_game(self, user_id: int, game_id: str):
        """Start quiz game"""
        questions = {
            'quiz_bangla': [
                {
                    'question': 'বাংলা ভাষায় মোট স্বরবর্ণ কয়টি?',
                    'options': ['৯', '১১', '৭', '৫'],
                    'answer': '১১',
                    'explanation': 'বাংলা ভাষায় মোট ১১টি স্বরবর্ণ আছে'
                },
                {
                    'question': 'রবীন্দ্রনাথ ঠাকুরের প্রথম কাব্যগ্রন্থের নাম কি?',
                    'options': ['গীতাঞ্জলি', 'সোনার তরী', 'কবি কাহিনী', 'বনফুল'],
                    'answer': 'কবি কাহিনী',
                    'explanation': '১৮৭৮ সালে কবি কাহিনী প্রকাশিত হয়'
                },
                {
                    'question': 'বাংলা নববর্ষের প্রথম মাসের নাম কি?',
                    'options': ['চৈত্র', 'বৈশাখ', 'আষাঢ়', 'জ্যৈষ্ঠ'],
                    'answer': 'বৈশাখ',
                    'explanation': 'বৈশাখ বাংলা সনের প্রথম মাস'
                }
            ],
            'quiz_math': [
                {
                    'question': '২ + ২ × ২ = ?',
                    'options': ['৬', '৮', '৪', '১০'],
                    'answer': '৬',
                    'explanation': 'গুণ আগে, তারপর যোগ: ২×২=৪, ৪+২=৬'
                },
                {
                    'question': 'এক ডজনে কয়টি?',
                    'options': ['১০', '১২', '১৪', '১৬'],
                    'answer': '১২',
                    'explanation': 'এক ডজন = ১২টি'
                },
                {
                    'question': '১০০ এর ৫০% কত?',
                    'options': ['২৫', '৫০', '৭৫', '১০০'],
                    'answer': '৫০',
                    'explanation': '১০০ × ৫০/১০০ = ৫০'
                }
            ]
        }
        
        if game_id in questions:
            question_set = questions[game_id]
            question = random.choice(question_set)
            
            # Store active game
            self.active_games[user_id] = {
                'game_id': game_id,
                'type': 'quiz',
                'question': question,
                'started_at': datetime.now().isoformat()
            }
            
            # Format question
            question_text = f"❓ {question['question']}\n\n"
            for i, option in enumerate(question['options'], 1):
                question_text += f"{i}. {option}\n"
            
            return question_text, "প্রশ্নের উত্তর দিন (1-4)"
        
        return "❌ প্রশ্ন পাওয়া যায়নি", ""
    
    async def _start_number_game(self, user_id: int, game_id: str):
        """Start number guessing game"""
        target_number = random.randint(1, 100)
        attempts = 7
        
        self.active_games[user_id] = {
            'game_id': game_id,
            'type': 'number',
            'target': target_number,
            'attempts': attempts,
            'attempts_used': 0,
            'started_at': datetime.now().isoformat()
        }
        
        return (
            f"🎯 *সংখ্যা অনুমান গেম*\n\n"
            f"১ থেকে ১০০ এর মধ্যে একটি সংখ্যা লুকানো আছে।\n"
            f"আপনার {attempts} বার চেষ্টা করার সুযোগ আছে।\n\n"
            f"একটি সংখ্যা দিন (১-১০০):",
            "সংখ্যা দিন"
        )
    
    async def _start_word_game(self, user_id: int, game_id: str):
        """Start word game"""
        words = ['বাংলাদেশ', 'ঢাকা', 'নদী', 'বই', 'স্কুল', 'কলম', 'গাছ', 'ফুল']
        word = random.choice(words)
        scrambled = ''.join(random.sample(word, len(word)))
        
        self.active_games[user_id] = {
            'game_id': game_id,
            'type': 'word_scramble',
            'word': word,
            'scrambled': scrambled,
            'started_at': datetime.now().isoformat()
        }
        
        return (
            f"🔠 *শব্দ জগাখিচুড়ি গেম*\n\n"
            f"জগাখিচুড়ি শব্দ: *{scrambled}*\n\n"
            f"সঠিক শব্দটি লিখুন:",
            "শব্দ দিন"
        )
    
    async def _start_luck_game(self, user_id: int, game_id: str):
        """Start luck-based game"""
        if game_id == 'dice_roll':
            user_dice = random.randint(1, 6)
            bot_dice = random.randint(1, 6)
            
            self.active_games[user_id] = {
                'game_id': game_id,
                'type': 'dice',
                'user_dice': user_dice,
                'bot_dice': bot_dice,
                'started_at': datetime.now().isoformat()
            }
            
            result = "জিতেছেন! 🎉" if user_dice > bot_dice else "হারেছেন! 😢" if user_dice < bot_dice else "ড্র! 🤝"
            
            return (
                f"🎲 *দাইস রোল গেম*\n\n"
                f"আপনার দাইস: {user_dice}\n"
                f"বটের দাইস: {bot_dice}\n\n"
                f"ফলাফল: {result}",
                ""
            )
        
        elif game_id == 'coin_flip':
            choices = ['হেড', 'টেল']
            user_choice = random.choice(choices)
            actual = random.choice(choices)
            
            self.active_games[user_id] = {
                'game_id': game_id,
                'type': 'coin',
                'user_choice': user_choice,
                'actual': actual,
                'started_at': datetime.now().isoformat()
            }
            
            win = user_choice == actual
            
            return (
                f"🪙 *কয়েন ফ্লিপ গেম*\n\n"
                f"আপনার পছন্দ: {user_choice}\n"
                f"ফলাফল: {actual}\n\n"
                f"ফলাফল: {'জিতেছেন! 🎉' if win else 'হারেছেন! 😢'}",
                ""
            )
        
        return "❌ গেম শুরু করা যায়নি", ""
    
    async def _start_default_game(self, user_id: int, game_id: str):
        """Start default game"""
        game_name = self.games[game_id]['name']
        
        # Simulate game result
        win_chance = 0.6  # 60% win chance
        win = random.random() < win_chance
        
        if win:
            reward = self.games[game_id]['reward']
            await self.db.add_points(user_id, reward, f"game_{game_id}_win")
            await self.db.log_game_result(user_id, game_id, 'win', reward)
            
            return (
                f"🎮 *{game_name}*\n\n"
                f"🎉 অভিনন্দন! আপনি জিতেছেন!\n"
                f"💰 পুরস্কার: {reward} পয়েন্ট\n\n"
                f"আপনার নতুন ব্যালেন্স চেক করতে /points লিখুন",
                ""
            )
        else:
            await self.db.log_game_result(user_id, game_id, 'lose', 0)
            
            return (
                f"🎮 *{game_name}*\n\n"
                f"😢 দুঃখিত! আপনি হারেছেন।\n"
                f"💪 আবার চেষ্টা করুন!\n\n"
                f"আরেকটি গেম খেলতে /game লিখুন",
                ""
            )
    
    async def process_game_answer(self, user_id: int, answer: str):
        """Process game answer"""
        if user_id not in self.active_games:
            return "❌ কোনো সক্রিয় গেম নেই"
        
        game_data = self.active_games[user_id]
        game_type = game_data['type']
        game_id = game_data['game_id']
        
        if game_type == 'quiz':
            return await self._process_quiz_answer(user_id, answer, game_data)
        elif game_type == 'number':
            return await self._process_number_answer(user_id, answer, game_data)
        elif game_type == 'word_scramble':
            return await self._process_word_answer(user_id, answer, game_data)
        else:
            # Game already processed
            del self.active_games[user_id]
            return "✅ গেম শেষ হয়েছে"
    
    async def _process_quiz_answer(self, user_id: int, answer: str, game_data: Dict):
        """Process quiz answer"""
        try:
            answer_index = int(answer) - 1
            question = game_data['question']
            options = question['options']
            
            if 0 <= answer_index < len(options):
                user_answer = options[answer_index]
                correct_answer = question['answer']
                
                if user_answer == correct_answer:
                    reward = self.games[game_data['game_id']]['reward']
                    await self.db.add_points(user_id, reward, f"quiz_correct")
                    await self.db.log_game_result(user_id, game_data['game_id'], 'win', reward)
                    
                    result = (
                        f"✅ সঠিক উত্তর!\n\n"
                        f"💰 পুরস্কার: {reward} পয়েন্ট\n"
                        f"📝 ব্যাখ্যা: {question['explanation']}\n\n"
                        f"আরেকটি গেম খেলতে /game লিখুন"
                    )
                else:
                    await self.db.log_game_result(user_id, game_data['game_id'], 'lose', 0)
                    
                    result = (
                        f"❌ ভুল উত্তর!\n\n"
                        f"সঠিক উত্তর: {correct_answer}\n"
                        f"📝 ব্যাখ্যা: {question['explanation']}\n\n"
                        f"আবার চেষ্টা করুন!"
                    )
            else:
                result = "❌ দয়া করে 1-4 এর মধ্যে একটি সংখ্যা দিন"
        
        except ValueError:
            result = "❌ দয়া করে একটি সংখ্যা দিন"
        
        # Clean up
        del self.active_games[user_id]
        return result
    
    async def _process_number_answer(self, user_id: int, answer: str, game_data: Dict):
        """Process number guessing answer"""
        try:
            guess = int(answer)
            target = game_data['target']
            attempts_left = game_data['attempts'] - game_data['attempts_used'] - 1
            
            game_data['attempts_used'] += 1
            
            if guess == target:
                reward = self.games[game_data['game_id']]['reward']
                await self.db.add_points(user_id, reward, f"number_guess_win")
                await self.db.log_game_result(user_id, game_data['game_id'], 'win', reward)
                
                del self.active_games[user_id]
                
                return (
                    f"🎉 অভিনন্দন! সঠিক সংখ্যা!\n\n"
                    f"সংশ্লিষ্ট সংখ্যা: {target}\n"
                    f"চেষ্টা: {game_data['attempts_used']}\n"
                    f"💰 পুরস্কার: {reward} পয়েন্ট\n\n"
                    f"আরেকটি গেম খেলতে /game লিখুন"
                )
            
            elif attempts_left <= 0:
                await self.db.log_game_result(user_id, game_data['game_id'], 'lose', 0)
                
                del self.active_games[user_id]
                
                return (
                    f"😢 গেম শেষ!\n\n"
                    f"সঠিক সংখ্যা ছিল: {target}\n"
                    f"আপনার শেষ অনুমান: {guess}\n\n"
                    f"আবার চেষ্টা করুন!"
                )
            
            else:
                hint = "📈 বেশি" if guess < target else "📉 কম"
                self.active_games[user_id] = game_data
                
                return (
                    f"{hint}! আবার চেষ্টা করুন\n\n"
                    f"অনুমান: {guess}\n"
                    f"বাকি চেষ্টা: {attempts_left}\n\n"
                    f"আরেকটি সংখ্যা দিন:"
                )
        
        except ValueError:
            return "❌ দয়া করে একটি সংখ্যা দিন"
    
    async def _process_word_answer(self, user_id: int, answer: str, game_data: Dict):
        """Process word scramble answer"""
        correct_word = game_data['word']
        user_answer = answer.strip()
        
        if user_answer.lower() == correct_word.lower():
            reward = self.games[game_data['game_id']]['reward']
            await self.db.add_points(user_id, reward, f"word_game_win")
            await self.db.log_game_result(user_id, game_data['game_id'], 'win', reward)
            
            result = (
                f"✅ সঠিক শব্দ!\n\n"
                f"সংশ্লিষ্ট শব্দ: {correct_word}\n"
                f"💰 পুরস্কার: {reward} পয়েন্ট\n\n"
                f"আরেকটি গেম খেলতে /game লিখুন"
            )
        else:
            await self.db.log_game_result(user_id, game_data['game_id'], 'lose', 0)
            
            result = (
                f"❌ ভুল শব্দ!\n\n"
                f"সঠিক শব্দ ছিল: {correct_word}\n"
                f"আপনার উত্তর: {user_answer}\n\n"
                f"আবার চেষ্টা করুন!"
            )
        
        del self.active_games[user_id]
        return result
    
    async def get_game_stats(self, user_id: int) -> Dict:
        """Get user game statistics"""
        games = await self.db.get_user_games(user_id, limit=100)
        
        if not games:
            return {
                'total_games': 0,
                'wins': 0,
                'losses': 0,
                'total_points_won': 0,
                'favorite_game': None
            }
        
        stats = {
            'total_games': len(games),
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'total_points_won': 0,
            'games_by_type': {}
        }
        
        for game in games:
            if game['result'] == 'win':
                stats['wins'] += 1
                stats['total_points_won'] += game.get('points_won', 0)
            elif game['result'] == 'lose':
                stats['losses'] += 1
            else:
                stats['draws'] += 1
            
            # Count by game type
            game_type = game['game_type']
            stats['games_by_type'][game_type] = stats['games_by_type'].get(game_type, 0) + 1
        
        # Find favorite game
        if stats['games_by_type']:
            favorite = max(stats['games_by_type'].items(), key=lambda x: x[1])
            stats['favorite_game'] = favorite[0]
        
        # Calculate win rate
        if stats['total_games'] > 0:
            stats['win_rate'] = (stats['wins'] / stats['total_games']) * 100
        else:
            stats['win_rate'] = 0
        
        return stats