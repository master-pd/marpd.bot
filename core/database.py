import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime, timedelta
import json
import asyncio
from typing import Optional, Dict, List, Any

class Database:
    """Firestore Database Manager"""
    
    def __init__(self):
        self.config = Config()
        self.db = None
        self.storage = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize Firebase connection"""
        try:
            if not firebase_admin._apps:
                # Create credentials from config
                cred_dict = {
                    "type": "service_account",
                    "project_id": self.config.FIREBASE_PROJECT_ID,
                    "private_key_id": self.config.FIREBASE_API_KEY,
                    "private_key": "-----BEGIN PRIVATE KEY-----\n\n-----END PRIVATE KEY-----\n",
                    "client_email": f"firebase-adminsdk@{self.config.FIREBASE_PROJECT_ID}.iam.gserviceaccount.com",
                    "client_id": "",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk%40{self.config.FIREBASE_PROJECT_ID}.iam.gserviceaccount.com"
                }
                
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': self.config.FIREBASE_DB_URL,
                    'storageBucket': self.config.FIREBASE_STORAGE_BUCKET
                })
            
            self.db = firestore.client()
            self.storage = storage.bucket()
            self.initialized = True
            
            print("✅ Firebase connected successfully")
            return True
            
        except Exception as e:
            print(f"❌ Firebase connection failed: {e}")
            return False
    
    # ========== USER MANAGEMENT ==========
    
    async def create_user(self, user_id: int, user_data: Dict) -> bool:
        """Create a new user"""
        try:
            user_ref = self.db.collection('users').document(str(user_id))
            
            # Add default fields
            user_data.update({
                'user_id': str(user_id),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'points': 100,  # Starting bonus
                'total_points_earned': 100,
                'total_points_spent': 0,
                'message_count': 0,
                'game_count': 0,
                'payment_count': 0,
                'referral_code': self._generate_referral_code(user_id),
                'referrals': [],
                'settings': {
                    'language': self.config.DEFAULT_LANGUAGE,
                    'notifications': True,
                    'private_profile': False
                },
                'stats': {
                    'daily_messages': 0,
                    'daily_games': 0,
                    'last_active': datetime.now().isoformat(),
                    'streak_days': 0,
                    'last_daily_bonus': None
                }
            })
            
            user_ref.set(user_data)
            return True
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            user_ref = self.db.collection('users').document(str(user_id))
            doc = user_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    async def update_user(self, user_id: int, updates: Dict) -> bool:
        """Update user data"""
        try:
            user_ref = self.db.collection('users').document(str(user_id))
            
            # Add update timestamp
            updates['updated_at'] = datetime.now().isoformat()
            
            user_ref.update(updates)
            return True
            
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        try:
            user_ref = self.db.collection('users').document(str(user_id))
            user_ref.delete()
            return True
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    # ========== POINTS MANAGEMENT ==========
    
    async def add_points(self, user_id: int, points: int, reason: str) -> bool:
        """Add points to user"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return False
            
            current_points = user.get('points', 0)
            new_points = current_points + points
            
            # Update user
            await self.update_user(user_id, {
                'points': new_points,
                'total_points_earned': user.get('total_points_earned', 0) + points,
                'stats.last_active': datetime.now().isoformat()
            })
            
            # Log transaction
            await self.log_transaction(
                user_id=user_id,
                type='credit',
                amount=points,
                reason=reason,
                balance_after=new_points
            )
            
            return True
            
        except Exception as e:
            print(f"Error adding points: {e}")
            return False
    
    async def deduct_points(self, user_id: int, points: int, reason: str) -> bool:
        """Deduct points from user"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return False
            
            current_points = user.get('points', 0)
            
            if current_points < points:
                return False  # Insufficient points
            
            new_points = current_points - points
            
            # Update user
            await self.update_user(user_id, {
                'points': new_points,
                'total_points_spent': user.get('total_points_spent', 0) + points
            })
            
            # Log transaction
            await self.log_transaction(
                user_id=user_id,
                type='debit',
                amount=points,
                reason=reason,
                balance_after=new_points
            )
            
            return True
            
        except Exception as e:
            print(f"Error deducting points: {e}")
            return False
    
    async def transfer_points(self, from_user: int, to_user: int, points: int, reason: str) -> bool:
        """Transfer points between users"""
        try:
            # Check if sender has enough points
            sender = await self.get_user(from_user)
            if not sender or sender.get('points', 0) < points:
                return False
            
            # Deduct from sender
            await self.deduct_points(from_user, points, f"transfer_to_{to_user}: {reason}")
            
            # Add to receiver
            await self.add_points(to_user, points, f"transfer_from_{from_user}: {reason}")
            
            # Log transfer
            transfer_data = {
                'from_user': str(from_user),
                'to_user': str(to_user),
                'amount': points,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            self.db.collection('transfers').add(transfer_data)
            
            return True
            
        except Exception as e:
            print(f"Error transferring points: {e}")
            return False
    
    # ========== TRANSACTION LOGGING ==========
    
    async def log_transaction(self, user_id: int, type: str, amount: int, reason: str, balance_after: int):
        """Log a transaction"""
        try:
            tx_data = {
                'user_id': str(user_id),
                'type': type,  # credit/debit
                'amount': amount,
                'reason': reason,
                'balance_after': balance_after,
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
            self.db.collection('transactions').add(tx_data)
            return True
            
        except Exception as e:
            print(f"Error logging transaction: {e}")
            return False
    
    async def get_user_transactions(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's transaction history"""
        try:
            transactions_ref = self.db.collection('transactions')
            query = transactions_ref \
                .where('user_id', '==', str(user_id)) \
                .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                .limit(limit)
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
            
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    # ========== MESSAGE LOGGING ==========
    
    async def log_message(self, user_id: int, message: str, message_type: str = 'text'):
        """Log user message for AI training"""
        try:
            if len(message) < self.config.MIN_LEARN_LENGTH:
                return False
            
            if len(message) > self.config.MAX_LEARN_LENGTH:
                return False
            
            message_data = {
                'user_id': str(user_id),
                'message': message,
                'type': message_type,
                'timestamp': datetime.now().isoformat(),
                'used_for_training': False,
                'language': 'bn' if self._is_bangla(message) else 'en'
            }
            
            self.db.collection('messages').add(message_data)
            
            # Update user stats
            user = await self.get_user(user_id)
            if user:
                daily_messages = user.get('stats', {}).get('daily_messages', 0) + 1
                await self.update_user(user_id, {
                    'message_count': user.get('message_count', 0) + 1,
                    'stats.daily_messages': daily_messages,
                    'stats.last_active': datetime.now().isoformat()
                })
            
            return True
            
        except Exception as e:
            print(f"Error logging message: {e}")
            return False
    
    async def get_training_messages(self, limit: int = 1000) -> List[str]:
        """Get messages for AI training"""
        try:
            messages_ref = self.db.collection('messages')
            query = messages_ref \
                .where('used_for_training', '==', False) \
                .limit(limit)
            
            docs = query.stream()
            messages = []
            
            for doc in docs:
                data = doc.to_dict()
                messages.append(data['message'])
                
                # Mark as used
                doc.reference.update({'used_for_training': True})
            
            return messages
            
        except Exception as e:
            print(f"Error getting training messages: {e}")
            return []
    
    # ========== PAYMENT MANAGEMENT ==========
    
    async def create_payment_request(self, user_id: int, amount: float, method: str, transaction_id: str = None) -> str:
        """Create payment request"""
        try:
            payment_data = {
                'user_id': str(user_id),
                'amount': amount,
                'method': method,
                'transaction_id': transaction_id,
                'status': 'pending',  # pending, verified, completed, rejected
                'points': amount * self.config.RECHARGE_RATE,
                'created_at': datetime.now().isoformat(),
                'verified_at': None,
                'completed_at': None,
                'admin_note': None,
                'screenshot_url': None
            }
            
            doc_ref = self.db.collection('payments').document()
            doc_ref.set(payment_data)
            
            return doc_ref.id
            
        except Exception as e:
            print(f"Error creating payment request: {e}")
            return None
    
    async def update_payment_status(self, payment_id: str, status: str, admin_note: str = None):
        """Update payment status"""
        try:
            payment_ref = self.db.collection('payments').document(payment_id)
            
            updates = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }
            
            if status == 'verified':
                updates['verified_at'] = datetime.now().isoformat()
            elif status == 'completed':
                updates['completed_at'] = datetime.now().isoformat()
            
            if admin_note:
                updates['admin_note'] = admin_note
            
            payment_ref.update(updates)
            return True
            
        except Exception as e:
            print(f"Error updating payment: {e}")
            return False
    
    async def get_pending_payments(self) -> List[Dict]:
        """Get all pending payments"""
        try:
            payments_ref = self.db.collection('payments')
            query = payments_ref.where('status', '==', 'pending')
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
            
        except Exception as e:
            print(f"Error getting pending payments: {e}")
            return []
    
    # ========== GAME MANAGEMENT ==========
    
    async def log_game_result(self, user_id: int, game_type: str, result: str, points_won: int):
        """Log game result"""
        try:
            game_data = {
                'user_id': str(user_id),
                'game_type': game_type,
                'result': result,  # win/lose/draw
                'points_won': points_won,
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
            self.db.collection('games').add(game_data)
            
            # Update user stats
            user = await self.get_user(user_id)
            if user:
                daily_games = user.get('stats', {}).get('daily_games', 0) + 1
                await self.update_user(user_id, {
                    'game_count': user.get('game_count', 0) + 1,
                    'stats.daily_games': daily_games
                })
            
            return True
            
        except Exception as e:
            print(f"Error logging game: {e}")
            return False
    
    async def get_user_games(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's game history"""
        try:
            games_ref = self.db.collection('games')
            query = games_ref \
                .where('user_id', '==', str(user_id)) \
                .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                .limit(limit)
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
            
        except Exception as e:
            print(f"Error getting games: {e}")
            return []
    
    # ========== STATISTICS ==========
    
    async def get_total_users(self) -> int:
        """Get total number of users"""
        try:
            users_ref = self.db.collection('users')
            docs = users_ref.limit(10000).stream()
            return sum(1 for _ in docs)
            
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0
    
    async def get_active_users(self, days: int = 7) -> int:
        """Get number of active users in last X days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()
            
            users_ref = self.db.collection('users')
            query = users_ref.where('stats.last_active', '>=', cutoff_str)
            
            docs = query.limit(10000).stream()
            return sum(1 for _ in docs)
            
        except Exception as e:
            print(f"Error counting active users: {e}")
            return 0
    
    async def get_total_points(self) -> int:
        """Get total points in system"""
        try:
            users_ref = self.db.collection('users')
            docs = users_ref.limit(10000).stream()
            
            total = 0
            for doc in docs:
                user_data = doc.to_dict()
                total += user_data.get('points', 0)
            
            return total
            
        except Exception as e:
            print(f"Error calculating total points: {e}")
            return 0
    
    async def get_leaderboard(self, limit: int = 100) -> List[Dict]:
        """Get points leaderboard"""
        try:
            users_ref = self.db.collection('users')
            query = users_ref.order_by('points', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            leaderboard = []
            
            for rank, doc in enumerate(docs, 1):
                user_data = doc.to_dict()
                leaderboard.append({
                    'rank': rank,
                    'user_id': user_data.get('user_id'),
                    'name': user_data.get('name', 'Unknown'),
                    'points': user_data.get('points', 0),
                    'message_count': user_data.get('message_count', 0)
                })
            
            return leaderboard
            
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    # ========== HELPER METHODS ==========
    
    def _generate_referral_code(self, user_id: int) -> str:
        """Generate referral code for user"""
        import hashlib
        hash_obj = hashlib.md5(f"MARPD{user_id}".encode())
        return hash_obj.hexdigest()[:8].upper()
    
    def _is_bangla(self, text: str) -> bool:
        """Check if text contains Bangla characters"""
        import re
        bangla_range = r'[\u0980-\u09FF]'
        return bool(re.search(bangla_range, text))
    
    async def close(self):
        """Close database connection"""
        # Firebase doesn't require explicit closing
        print("Database connection closed")
    
    async def backup_data(self, backup_path: str):
        """Backup data to file"""
        try:
            # Backup users
            users_ref = self.db.collection('users')
            users_docs = users_ref.limit(1000).stream()
            
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'users': [],
                'total_users': 0
            }
            
            for doc in users_docs:
                user_data = doc.to_dict()
                # Remove sensitive data
                user_data.pop('settings', None)
                user_data.pop('stats', None)
                backup_data['users'].append(user_data)
            
            backup_data['total_users'] = len(backup_data['users'])
            
            # Save to file
            import json
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error backing up data: {e}")
            return False