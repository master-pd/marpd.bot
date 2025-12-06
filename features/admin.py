import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class AdminSystem:
    """Complete Admin Control System"""
    
    def __init__(self, db):
        self.db = db
        self.config = Config()
        self.admin_users = set([str(self.config.BOT_OWNER_ID)])
        
        # Load additional admins
        self._load_admins()
    
    def _load_admins(self):
        """Load admin users"""
        # Add payment admin
        if self.config.PAYMENT_ADMIN_ID:
            self.admin_users.add(str(self.config.PAYMENT_ADMIN_ID))
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return str(user_id) in self.admin_users
    
    async def add_admin(self, current_admin_id: int, new_admin_id: int) -> Tuple[bool, str]:
        """Add new admin"""
        if not self.is_admin(current_admin_id):
            return False, "❌ শুধুমাত্র এডমিন এই কমান্ড ব্যবহার করতে পারেন"
        
        self.admin_users.add(str(new_admin_id))
        return True, f"✅ {new_admin_id} কে এডমিন করা হয়েছে"
    
    async def remove_admin(self, current_admin_id: int, admin_id: int) -> Tuple[bool, str]:
        """Remove admin"""
        if not self.is_admin(current_admin_id):
            return False, "❌ শুধুমাত্র এডমিন এই কমান্ড ব্যবহার করতে পারেন"
        
        # Cannot remove owner
        if str(admin_id) == str(self.config.BOT_OWNER_ID):
            return False, "❌ মালিককে এডমিন থেকে সরানো যাবে না"
        
        if str(admin_id) in self.admin_users:
            self.admin_users.remove(str(admin_id))
            return True, f"✅ {admin_id} কে এডমিন থেকে সরানো হয়েছে"
        
        return False, "❌ ইউজার এডমিন না"
    
    async def get_all_users(self, page: int = 1, limit: int = 50) -> Dict:
        """Get all users with pagination"""
        try:
            # In Firestore, we need to query all and paginate manually
            # This is simplified version
            users_ref = self.db.db.collection('users')
            
            # Get total count
            total_query = users_ref.limit(10000)
            total_docs = total_query.stream()
            total_users = sum(1 for _ in total_docs)
            
            # Calculate pages
            total_pages = (total_users + limit - 1) // limit
            offset = (page - 1) * limit
            
            # Query with pagination (simplified)
            query = users_ref.limit(limit)
            docs = query.stream()
            
            users = []
            for doc in docs:
                user_data = doc.to_dict()
                # Add document ID
                user_data['id'] = doc.id
                users.append(user_data)
            
            return {
                'users': users,
                'total': total_users,
                'page': page,
                'limit': limit,
                'pages': total_pages
            }
            
        except Exception as e:
            print(f"Error getting users: {e}")
            return {'users': [], 'total': 0, 'page': 1, 'limit': limit, 'pages': 0}
    
    async def search_users(self, query: str) -> List[Dict]:
        """Search users by name or ID"""
        try:
            users_ref = self.db.db.collection('users')
            
            # Search by user_id
            results = []
            
            # Try exact user_id match first
            try:
                user_id = int(query)
                user_doc = users_ref.document(str(user_id)).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    user_data['id'] = user_doc.id
                    results.append(user_data)
            except ValueError:
                pass
            
            # Search by name (case insensitive, partial match)
            all_users = users_ref.limit(100).stream()
            for doc in all_users:
                user_data = doc.to_dict()
                name = user_data.get('name', '').lower()
                username = user_data.get('username', '').lower()
                
                if (query.lower() in name) or (query.lower() in username):
                    user_data['id'] = doc.id
                    results.append(user_data)
            
            return results
            
        except Exception as e:
            print(f"Error searching users: {e}")
            return []
    
    async def get_user_details(self, user_id: int) -> Optional[Dict]:
        """Get detailed user information"""
        user = await self.db.get_user(user_id)
        if not user:
            return None
        
        # Get transactions
        transactions = await self.db.get_user_transactions(user_id, limit=20)
        
        # Get games
        games = await self.db.get_user_games(user_id, limit=20)
        
        # Get payments
        payments_ref = self.db.db.collection('payments')
        payment_query = payments_ref.where('user_id', '==', str(user_id)).limit(20)
        payment_docs = payment_query.stream()
        payments = [doc.to_dict() for doc in payment_docs]
        
        # Calculate statistics
        total_earned = user.get('total_points_earned', 0)
        total_spent = user.get('total_points_spent', 0)
        net_points = total_earned - total_spent
        
        return {
            'basic_info': user,
            'transactions': transactions,
            'games': games,
            'payments': payments,
            'stats': {
                'total_earned': total_earned,
                'total_spent': total_spent,
                'net_points': net_points,
                'message_count': user.get('message_count', 0),
                'game_count': user.get('game_count', 0),
                'payment_count': user.get('payment_count', 0),
                'referrals': len(user.get('referrals', [])),
                'days_active': self._calculate_days_active(user)
            }
        }
    
    def _calculate_days_active(self, user_data: Dict) -> int:
        """Calculate days user has been active"""
        try:
            created = datetime.fromisoformat(user_data.get('created_at', datetime.now().isoformat()))
            now = datetime.now()
            return (now - created).days
        except:
            return 0
    
    async def add_points(self, admin_id: int, target_user_id: int, points: int, reason: str) -> Tuple[bool, str]:
        """Add points to user"""
        if not self.is_admin(admin_id):
            return False, "❌ শুধুমাত্র এডমিন"
        
        if points <= 0:
            return False, "❌ পয়েন্ট 0 থেকে বেশি হতে হবে"
        
        success = await self.db.add_points(target_user_id, points, f"admin_add:{reason}")
        if success:
            return True, f"✅ {target_user_id} ইউজারকে {points} পয়েন্ট যোগ করা হয়েছে\nকারণ: {reason}"
        else:
            return False, "❌ পয়েন্ট যোগ করা যায়নি"
    
    async def deduct_points(self, admin_id: int, target_user_id: int, points: int, reason: str) -> Tuple[bool, str]:
        """Deduct points from user"""
        if not self.is_admin(admin_id):
            return False, "❌ শুধুমাত্র এডমিন"
        
        if points <= 0:
            return False, "❌ পয়েন্ট 0 থেকে বেশি হতে হবে"
        
        success = await self.db.deduct_points(target_user_id, points, f"admin_deduct:{reason}")
        if success:
            return True, f"✅ {target_user_id} ইউজার থেকে {points} পয়েন্ট কাটা হয়েছে\nকারণ: {reason}"
        else:
            return False, "❌ পয়েন্ট কাটা যায়নি (পর্যাপ্ত পয়েন্ট নেই)"
    
    async def reset_user_points(self, admin_id: int, target_user_id: int) -> Tuple[bool, str]:
        """Reset user points to 0"""
        if not self.is_admin(admin_id):
            return False, "❌ শুধুমাত্র এডমিন"
        
        user = await self.db.get_user(target_user_id)
        if not user:
            return False, "❌ ইউজার পাওয়া যায়নি"
        
        current_points = user.get('points', 0)
        if current_points > 0:
            await self.db.deduct_points(target_user_id, current_points, "admin_reset")
        
        return True, f"✅ {target_user_id} ইউজারের {current_points} পয়েন্ট রিসেট করা হয়েছে"
    
    async def ban_user(self, admin_id: int, target_user_id: int, reason: str = "No reason provided") -> Tuple[bool, str]:
        """Ban user from bot"""
        if not self.is_admin(admin_id):
            return False, "❌ শুধুমাত্র এডমিন"
        
        # Update user with ban status
        await self.db.update_user(target_user_id, {
            'banned': True,
            'ban_reason': reason,
            'ban_date': datetime.now().isoformat(),
            'banned_by': str(admin_id)
        })
        
        return True, f"✅ {target_user_id} ইউজার ব্যান করা হয়েছে\nকারণ: {reason}"
    
    async def unban_user(self, admin_id: int, target_user_id: int) -> Tuple[bool, str]:
        """Unban user"""
        if not self.is_admin(admin_id):
            return False, "❌ শুধুমাত্র এডমিন"
        
        await self.db.update_user(target_user_id, {
            'banned': False,
            'unban_date': datetime.now().isoformat(),
            'unbanned_by': str(admin_id)
        })
        
        return True, f"✅ {target_user_id} ইউজার আনবান করা হয়েছে"
    
    async def get_pending_payments(self) -> List[Dict]:
        """Get all pending payment requests"""
        return await self.db.get_pending_payments()
    
    async def verify_payment(self, admin_id: int, payment_id: str, transaction_proof: str = None) -> Tuple[bool, str]:
        """Verify payment manually"""
        if not self.is_admin(admin_id):
            return False, "❌ শুধুমাত্র এডমিন"
        
        try:
            # Get payment document
            payment_ref = self.db.db.collection('payments').document(payment_id)
            payment_doc = payment_ref.get()
            
            if not payment_doc.exists:
                return False, "❌ পেমেন্ট রিকুয়েস্ট পাওয়া যায়নি"
            
            payment_data = payment_doc.to_dict()
            
            if payment_data['status'] != 'pending':
                return False, f"❌ পেমেন্ট ইতিমধ্যে {payment_data['status']} স্ট্যাটাসে আছে"
            
            # Update to verified
            await self.db.update_payment_status(payment_id, 'verified', f"Verified by admin {admin_id}")
            
            # Add points to user
            user_id = int(payment_data['user_id'])
            points = payment_data['points']
            
            await self.db.add_points(user_id, points, f"recharge_{payment_data['method']}_verified")
            
            # Update payment to completed
            await self.db.update_payment_status(payment_id, 'completed', 
                                              f"Points added: {points}")
            
            return True, (
                f"✅ পেমেন্ট ভেরিফাই ও সম্পন্ন করা হয়েছে!\n\n"
                f"👤 ইউজার: {user_id}\n"
                f"💰 টাকা: {payment_data['amount']}\n"
                f"🪙 পয়েন্ট: {points}\n"
                f"📱 পদ্ধতি: {payment_data['method']}\n"
                f"🆔 ট্রানজেকশন: {payment_data.get('transaction_id', 'N/A')}"
            )
            
        except Exception as e:
            return False, f"❌ ভেরিফিকেশন ব্যর্থ: {str(e)}"
    
    async def reject_payment(self, admin_id: int, payment_id: str, reason: str) -> Tuple[bool, str]:
        """Reject payment request"""
        if not self.is_admin(admin_id):
            return False, "❌ শুধুমাত্র এডমিন"
        
        try:
            await self.db.update_payment_status(payment_id, 'rejected', reason)
            return True, f"✅ পেমেন্ট রিকুয়েস্ট রিজেক্ট করা হয়েছে\nকারণ: {reason}"
        except Exception as e:
            return False, f"❌ রিজেক্ট ব্যর্থ: {str(e)}"
    
    async def send_broadcast(self, admin_id: int, message: str, target: str = "all") -> Tuple[bool, str]:
        """Send broadcast message to users"""
        if not self.is_admin(admin_id):
            return False, "❌ শুধুমাত্র এডমিন"
        
        try:
            # Get all users
            users_ref = self.db.db.collection('users')
            users_docs = users_ref.limit(1000).stream()
            
            user_ids = []
            for doc in users_docs:
                user_data = doc.to_dict()
                user_ids.append(int(user_data['user_id']))
            
            total_users = len(user_ids)
            
            return True, (
                f"📢 ব্রডকাস্ট প্রস্তুত!\n\n"
                f"💬 মেসেজ: {message[:100]}...\n"
                f"👥 টার্গেট: {target}\n"
                f"👤 টোটাল ইউজার: {total_users}\n\n"
                f"ব্রডকাস্ট পাঠাতে 'confirm' লিখুন"
            )
            
        except Exception as e:
            return False, f"❌ ব্রডকাস্ট ব্যর্থ: {str(e)}"
    
    async def get_bot_stats(self) -> Dict:
        """Get bot statistics"""
        total_users = await self.db.get_total_users()
        active_users = await self.db.get_active_users(days=1)
        total_points = await self.db.get_total_points()
        
        # Get today's transactions
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_str = today_start.isoformat()
        
        try:
            # Get today's transactions count
            tx_ref = self.db.db.collection('transactions')
            tx_query = tx_ref.where('timestamp', '>=', today_str)
            tx_docs = tx_query.limit(1000).stream()
            today_transactions = sum(1 for _ in tx_docs)
            
            # Get today's messages
            msg_ref = self.db.db.collection('messages')
            msg_query = msg_ref.where('timestamp', '>=', today_str)
            msg_docs = msg_query.limit(1000).stream()
            today_messages = sum(1 for _ in msg_docs)
            
            # Get today's games
            games_ref = self.db.db.collection('games')
            games_query = games_ref.where('timestamp', '>=', today_str)
            games_docs = games_query.limit(1000).stream()
            today_games = sum(1 for _ in games_docs)
            
        except Exception as e:
            print(f"Error getting daily stats: {e}")
            today_transactions = 0
            today_messages = 0
            today_games = 0
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_points': total_points,
            'today_transactions': today_transactions,
            'today_messages': today_messages,
            'today_games': today_games,
            'pending_payments': len(await self.get_pending_payments())
        }
    
    async def get_system_health(self) -> Dict:
        """Get system health status"""
        try:
            # Test database connection
            db_ok = await self.db.get_total_users() >= 0
            
            # Check disk space (simplified)
            import os
            statvfs = os.statvfs('.')
            free_space_gb = (statvfs.f_frsize * statvfs.f_bfree) / (1024**3)
            disk_ok = free_space_gb > 1  # More than 1GB free
            
            # Check memory (simplified)
            import psutil
            memory = psutil.virtual_memory()
            memory_ok = memory.percent < 90
            
            return {
                'database': '✅ OK' if db_ok else '❌ Error',
                'disk_space': f'{free_space_gb:.2f} GB free',
                'disk_status': '✅ OK' if disk_ok else '⚠️ Low',
                'memory': f'{memory.percent}% used',
                'memory_status': '✅ OK' if memory_ok else '⚠️ High',
                'uptime': str(datetime.now() - self.db.start_time if hasattr(self.db, 'start_time') else 'N/A')
            }
            
        except Exception as e:
            return {
                'database': '❌ Error',
                'disk_space': 'N/A',
                'disk_status': '❌ Error',
                'memory': 'N/A',
                'memory_status': '❌ Error',
                'uptime': 'N/A',
                'error': str(e)
            }
    
    async def backup_database(self, admin_id: int) -> Tuple[bool, str]:
        """Create database backup"""
        if not self.is_admin(admin_id):
            return False, "❌ শুধুমাত্র এডমিন"
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backups/backup_{timestamp}.json"
            
            success = await self.db.backup_data(backup_file)
            
            if success:
                return True, f"✅ ব্যাকআপ তৈরি করা হয়েছে: {backup_file}"
            else:
                return False, "❌ ব্যাকআপ তৈরি ব্যর্থ"
                
        except Exception as e:
            return False, f"❌ ব্যাকআপ ব্যর্থ: {str(e)}"
    
    async def restore_database(self, admin_id: int, backup_file: str) -> Tuple[bool, str]:
        """Restore database from backup"""
        if not self.is_admin(admin_id):
            return False, "❌ শুধুমাত্র এডমিন"
        
        return False, "⚠️ রিস্টোর ফিচার উন্নয়নাধীন"