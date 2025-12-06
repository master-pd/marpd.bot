import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class EconomySystem:
    """Complete Economy System"""
    
    def __init__(self, db):
        self.db = db
        self.config = Config()
        
        # Daily bonus system
        self.daily_bonus_levels = {
            1: 10,    # Day 1
            2: 15,    # Day 2
            3: 20,    # Day 3
            4: 25,    # Day 4
            5: 30,    # Day 5
            6: 40,    # Day 6
            7: 50     # Day 7
        }
    
    async def add_daily_bonus(self, user_id: int) -> Tuple[bool, str, int]:
        """Add daily bonus to user"""
        user = await self.db.get_user(user_id)
        if not user:
            return False, "❌ ইউজার ডাটা পাওয়া যায়নি", 0
        
        today = datetime.now().date()
        today_str = today.isoformat()
        
        # Check last bonus date
        last_bonus_date = user.get('stats', {}).get('last_daily_bonus')
        
        if last_bonus_date:
            last_date = datetime.fromisoformat(last_bonus_date).date()
            
            # Check if already claimed today
            if last_date == today:
                return False, "❌ আজকের ডেইলি বোনাস ইতিমধ্যে নিয়েছেন", 0
            
            # Check streak
            yesterday = today - timedelta(days=1)
            
            if last_date == yesterday:
                # Continue streak
                streak_days = user.get('stats', {}).get('streak_days', 0) + 1
            else:
                # Reset streak
                streak_days = 1
        else:
            # First time
            streak_days = 1
        
        # Calculate bonus
        if streak_days >= 7:
            bonus_amount = self.daily_bonus_levels[7]
        else:
            bonus_amount = self.daily_bonus_levels.get(streak_days, 10)
        
        # Add bonus points
        await self.db.add_points(user_id, bonus_amount, f"daily_bonus_day_{streak_days}")
        
        # Update user stats
        await self.db.update_user(user_id, {
            'stats.last_daily_bonus': today_str,
            'stats.streak_days': streak_days,
            'stats.daily_bonus_total': user.get('stats', {}).get('daily_bonus_total', 0) + bonus_amount
        })
        
        # Streak bonus for 7 days
        if streak_days == 7:
            streak_bonus = 100
            await self.db.add_points(user_id, streak_bonus, "weekly_streak_bonus")
            bonus_amount += streak_bonus
        
        message = self._generate_daily_bonus_message(streak_days, bonus_amount)
        return True, message, bonus_amount
    
    def _generate_daily_bonus_message(self, streak_days: int, bonus_amount: int) -> str:
        """Generate daily bonus message"""
        message = f"""
🎁 *ডেইলি বোনাস!*

✅ বোনাস ক্লেইম করা হয়েছে!
💰 পরিমাণ: {bonus_amount} পয়েন্ট
🔥 স্ট্রিক: {streak_days} দিন
        
"""
        
        if streak_days == 7:
            message += "\n🎉 *সাপ্তাহিক স্ট্রিক বোনাস!* +১০০ পয়েন্ট\n"
            message += "স্ট্রিক রিসেট হয়েছে, আগামীকাল থেকে আবার শুরু করুন!\n"
        elif streak_days == 1:
            message += "\n🔥 নতুন স্ট্রিক শুরু হয়েছে!\n"
            message += "প্রতিদিন বোনাস নিয়ে স্ট্রিক চালিয়ে যান!\n"
        else:
            days_to_7 = 7 - streak_days
            message += f"\n⏳ {days_to_7} দিন পর পাবেন সাপ্তাহিক বোনাস!\n"
        
        message += f"\nআপনার নতুন ব্যালেন্স চেক করতে /points লিখুন"
        
        return message
    
    async def add_referral_bonus(self, referrer_id: int, referred_id: int) -> Tuple[bool, str]:
        """Add referral bonus"""
        # Check if user was already referred
        referrer = await self.db.get_user(referrer_id)
        referred = await self.db.get_user(referred_id)
        
        if not referrer or not referred:
            return False, "❌ ইউজার ডাটা পাওয়া যায়নি"
        
        # Check if already referred
        referrals = referrer.get('referrals', [])
        if str(referred_id) in referrals:
            return False, "❌ ইতিমধ্যে রেফার করা হয়েছে"
        
        # Add referral bonus
        bonus = self.config.REFERRAL_BONUS
        
        await self.db.add_points(referrer_id, bonus, f"referral_bonus:{referred_id}")
        
        # Also give bonus to referred user
        await self.db.add_points(referred_id, 50, f"referred_by:{referrer_id}")
        
        # Update referral list
        referrals.append(str(referred_id))
        await self.db.update_user(referrer_id, {
            'referrals': referrals,
            'referral_count': len(referrals)
        })
        
        # Update referred user
        await self.db.update_user(referred_id, {
            'referred_by': str(referrer_id)
        })
        
        return True, (
            f"✅ রেফারাল বোনাস যোগ করা হয়েছে!\n\n"
            f"👥 রেফারার: {referrer_id}\n"
            f"👤 রেফার্ড: {referred_id}\n"
            f"💰 বোনাস: {bonus} পয়েন্ট\n"
            f"📊 টোটাল রেফারাল: {len(referrals)}\n\n"
            f"আরও রেফার করে পয়েন্ট পান!"
        )
    
    async def send_points(self, sender_id: int, receiver_username: str, points: int, note: str = "") -> Tuple[bool, str]:
        """Send points to another user"""
        # Validate points
        if points <= 0:
            return False, "❌ পয়েন্ট 0 থেকে বেশি হতে হবে"
        
        if points > 10000:
            return False, "❌ একবারে সর্বোচ্চ ১০,০০০ পয়েন্ট পাঠাতে পারেন"
        
        # Check sender balance
        sender = await self.db.get_user(sender_id)
        if not sender:
            return False, "❌ আপনার অ্যাকাউন্ট পাওয়া যায়নি"
        
        sender_points = sender.get('points', 0)
        if sender_points < points:
            return False, f"❌ আপনার কাছে {points} পয়েন্ট নেই। আপনার ব্যালেন্স: {sender_points} পয়েন্ট"
        
        # Find receiver by username or ID
        receiver_id = None
        
        # Try to find by username (remove @ if present)
        if receiver_username.startswith('@'):
            receiver_username = receiver_username[1:]
        
        # Search for user by username
        users_ref = self.db.db.collection('users')
        users_docs = users_ref.limit(100).stream()
        
        for doc in users_docs:
            user_data = doc.to_dict()
            if user_data.get('username', '').lower() == receiver_username.lower():
                receiver_id = int(user_data['user_id'])
                break
        
        if not receiver_id:
            # Try as user ID
            try:
                receiver_id = int(receiver_username)
            except ValueError:
                return False, "❌ ইউজার পাওয়া যায়নি। সঠিক ইউজারনেম বা আইডি দিন"
        
        # Check if receiver exists
        receiver = await self.db.get_user(receiver_id)
        if not receiver:
            return False, f"❌ {receiver_id} আইডির ইউজার পাওয়া যায়নি"
        
        # Don't allow sending to self
        if sender_id == receiver_id:
            return False, "❌ নিজেকে পয়েন্ট পাঠাতে পারবেন না"
        
        # Transfer points
        success = await self.db.transfer_points(sender_id, receiver_id, points, f"send:{note}")
        
        if success:
            # Send notifications
            sender_name = sender.get('name', 'Unknown')
            receiver_name = receiver.get('name', 'Unknown')
            
            # Generate receipt
            receipt = self._generate_transfer_receipt(
                sender_id, sender_name,
                receiver_id, receiver_name,
                points, note
            )
            
            return True, receipt
        else:
            return False, "❌ পয়েন্ট ট্রান্সফার ব্যর্থ"
    
    def _generate_transfer_receipt(self, sender_id: int, sender_name: str,
                                 receiver_id: int, receiver_name: str,
                                 points: int, note: str) -> str:
        """Generate transfer receipt"""
        return f"""
🧾 *পয়েন্ট ট্রান্সফার*

✅ পয়েন্ট পাঠানো হয়েছে!

📋 *বিবরণ:*
👤 পাঠানোর: {sender_name} ({sender_id})
👥 প্রাপ্তের: {receiver_name} ({receiver_id})
💰 পরিমাণ: {points} পয়েন্ট
📝 নোট: {note or 'No note'}
📅 তারিখ: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}

💳 *রসিদ:*
TXN{datetime.now().strftime('%Y%m%d%H%M%S')}

✅ ট্রানজেকশন সম্পন্ন হয়েছে।
        """
    
    async def get_user_economy_stats(self, user_id: int) -> Dict:
        """Get user's economy statistics"""
        user = await self.db.get_user(user_id)
        if not user:
            return {}
        
        # Get transactions
        transactions = await self.db.get_user_transactions(user_id, limit=100)
        
        # Calculate statistics
        total_earned = user.get('total_points_earned', 0)
        total_spent = user.get('total_points_spent', 0)
        current_balance = user.get('points', 0)
        
        # Calculate by category
        earned_by_category = {}
        spent_by_category = {}
        
        for tx in transactions:
            reason = tx.get('reason', '')
            amount = tx.get('amount', 0)
            
            if tx['type'] == 'credit':
                # Categorize earnings
                if 'message' in reason:
                    earned_by_category['messages'] = earned_by_category.get('messages', 0) + amount
                elif 'game' in reason:
                    earned_by_category['games'] = earned_by_category.get('games', 0) + amount
                elif 'daily' in reason:
                    earned_by_category['daily_bonus'] = earned_by_category.get('daily_bonus', 0) + amount
                elif 'referral' in reason:
                    earned_by_category['referrals'] = earned_by_category.get('referrals', 0) + amount
                elif 'recharge' in reason:
                    earned_by_category['recharge'] = earned_by_category.get('recharge', 0) + amount
                else:
                    earned_by_category['other'] = earned_by_category.get('other', 0) + amount
            
            else:  # debit
                # Categorize spending
                if 'game' in reason:
                    spent_by_category['games'] = spent_by_category.get('games', 0) + amount
                elif 'shop' in reason:
                    spent_by_category['shop'] = spent_by_category.get('shop', 0) + amount
                elif 'withdrawal' in reason:
                    spent_by_category['withdrawal'] = spent_by_category.get('withdrawal', 0) + amount
                elif 'send' in reason:
                    spent_by_category['transfer'] = spent_by_category.get('transfer', 0) + amount
                else:
                    spent_by_category['other'] = spent_by_category.get('other', 0) + amount
        
        # Get streak info
        streak_days = user.get('stats', {}).get('streak_days', 0)
        last_bonus = user.get('stats', {}).get('last_daily_bonus')
        
        if last_bonus:
            last_date = datetime.fromisoformat(last_bonus).date()
            today = datetime.now().date()
            
            if last_date == today:
                daily_bonus_claimed = True
            else:
                daily_bonus_claimed = False
        else:
            daily_bonus_claimed = False
        
        # Get referrals
        referral_count = len(user.get('referrals', []))
        referral_earnings = earned_by_category.get('referrals', 0)
        
        return {
            'current_balance': current_balance,
            'total_earned': total_earned,
            'total_spent': total_spent,
            'net_worth': total_earned - total_spent,
            
            'earned_by_category': earned_by_category,
            'spent_by_category': spent_by_category,
            
            'streak_days': streak_days,
            'daily_bonus_claimed': daily_bonus_claimed,
            
            'referral_count': referral_count,
            'referral_earnings': referral_earnings,
            
            'message_count': user.get('message_count', 0),
            'game_count': user.get('game_count', 0),
            'payment_count': user.get('payment_count', 0),
            
            'daily_stats': {
                'messages': user.get('stats', {}).get('daily_messages', 0),
                'games': user.get('stats', {}).get('daily_games', 0)
            }
        }
    
    async def get_leaderboard(self, limit: int = 100) -> List[Dict]:
        """Get points leaderboard"""
        return await self.db.get_leaderboard(limit)
    
    async def get_richest_users(self, limit: int = 10) -> List[Dict]:
        """Get richest users by points"""
        leaderboard = await self.get_leaderboard(limit)
        
        # Format for display
        formatted = []
        for user in leaderboard:
            formatted.append({
                'rank': user['rank'],
                'user_id': user['user_id'],
                'name': user['name'],
                'points': user['points'],
                'message_count': user.get('message_count', 0)
            })
        
        return formatted
    
    async def reset_daily_stats(self):
        """Reset daily statistics for all users"""
        # This would be called by a scheduled task
        try:
            # Get all users
            users_ref = self.db.db.collection('users')
            users_docs = users_ref.limit(1000).stream()
            
            for doc in users_docs:
                user_id = doc.id
                user_ref = users_ref.document(user_id)
                
                # Reset daily stats
                user_ref.update({
                    'stats.daily_messages': 0,
                    'stats.daily_games': 0,
                    'updated_at': datetime.now().isoformat()
                })
            
            print("✅ Daily stats reset complete")
            return True
            
        except Exception as e:
            print(f"Error resetting daily stats: {e}")
            return False
    
    async def get_system_economy_stats(self) -> Dict:
        """Get overall economy statistics"""
        total_points = await self.db.get_total_points()
        total_users = await self.db.get_total_users()
        active_users = await self.db.get_active_users(days=1)
        
        # Get today's economy activity
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_str = today_start.isoformat()
        
        try:
            # Today's transactions
            tx_ref = self.db.db.collection('transactions')
            tx_query = tx_ref.where('timestamp', '>=', today_str)
            tx_docs = tx_query.limit(1000).stream()
            
            today_credits = 0
            today_debits = 0
            
            for doc in tx_docs:
                tx_data = doc.to_dict()
                if tx_data['type'] == 'credit':
                    today_credits += tx_data['amount']
                else:
                    today_debits += tx_data['amount']
            
            # Today's messages (for points calculation)
            msg_ref = self.db.db.collection('messages')
            msg_query = msg_ref.where('timestamp', '>=', today_str)
            msg_docs = msg_query.limit(1000).stream()
            today_messages = sum(1 for _ in msg_docs)
            
            # Today's games
            games_ref = self.db.db.collection('games')
            games_query = games_ref.where('timestamp', '>=', today_str)
            games_docs = games_query.limit(1000).stream()
            today_games = sum(1 for _ in games_docs)
            
            # Average points per user
            avg_points = total_points / total_users if total_users > 0 else 0
            
            return {
                'total_points': total_points,
                'total_users': total_users,
                'active_users': active_users,
                'avg_points_per_user': round(avg_points, 2),
                
                'today_credits': today_credits,
                'today_debits': today_debits,
                'today_net': today_credits - today_debits,
                
                'today_messages': today_messages,
                'today_message_points': today_messages * self.config.POINTS_PER_MESSAGE,
                'today_games': today_games,
                
                'economy_health': self._calculate_economy_health(today_credits, today_debits)
            }
            
        except Exception as e:
            print(f"Error getting economy stats: {e}")
            return {
                'total_points': total_points,
                'total_users': total_users,
                'active_users': active_users,
                'avg_points_per_user': 0,
                'today_credits': 0,
                'today_debits': 0,
                'today_net': 0,
                'today_messages': 0,
                'today_message_points': 0,
                'today_games': 0,
                'economy_health': 'unknown'
            }
    
    def _calculate_economy_health(self, credits: int, debits: int) -> str:
        """Calculate economy health"""
        if credits == 0:
            return "⚠️ Inactive"
        
        ratio = debits / credits if credits > 0 else 0
        
        if ratio < 0.3:
            return "✅ Healthy"
        elif ratio < 0.6:
            return "⚠️ Moderate"
        else:
            return "🔴 High Inflation"
    
    async def generate_economy_report(self) -> str:
        """Generate economy report"""
        stats = await self.get_system_economy_stats()
        
        report = f"""
📊 *ইকোনমি রিপোর্ট*

📈 *মূল স্ট্যাটস:*
• টোটাল পয়েন্ট: {stats['total_points']:,}
• টোটাল ইউজার: {stats['total_users']}
• অ্যাক্টিভ ইউজার: {stats['active_users']}
• গড় পয়েন্ট: {stats['avg_points_per_user']:.1f}

📅 *আজকের কার্যক্রম:*
• যোগ পয়েন্ট: {stats['today_credits']:,}
• খরচ পয়েন্ট: {stats['today_debits']:,}
• নেট পরিবর্তন: {stats['today_net']:,}
• মেসেজ: {stats['today_messages']}
• গেম: {stats['today_games']}

🏥 *ইকোনমি স্বাস্থ্য:* {stats['economy_health']}

📈 *বিশ্লেষণ:*
"""
        
        # Add analysis based on stats
        if stats['today_net'] > 0:
            report += "• ইকোনমিতে পয়েন্ট যোগ হচ্ছে ✅\n"
        else:
            report += "• পয়েন্ট খরচ বেশি ⚠️\n"
        
        if stats['economy_health'] == 'Healthy':
            report += "• ইকোনমি ভারসাম্যপূর্ণ ✅\n"
        else:
            report += "• ভারসাম্য বজায় রাখার প্রয়োজন ⚠️\n"
        
        report += f"\n🕒 রিপোর্ট সময়: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}"
        
        return report