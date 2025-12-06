import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp

class NotificationSystem:
    """Notification and Alert System"""
    
    def __init__(self, db):
        self.db = db
        self.config = Config()
        self.session = None
        
    async def start(self):
        """Start notification system"""
        self.session = aiohttp.ClientSession()
        print("🔔 Notification system started")
    
    async def stop(self):
        """Stop notification system"""
        if self.session:
            await self.session.close()
        print("🔔 Notification system stopped")
    
    async def send_notification(self, user_id: int, title: str, message: str, 
                              notification_type: str = "info") -> bool:
        """Send notification to user"""
        try:
            # Store notification in database
            notif_data = {
                'user_id': str(user_id),
                'title': title,
                'message': message,
                'type': notification_type,
                'read': False,
                'created_at': datetime.now().isoformat()
            }
            
            self.db.db.collection('notifications').add(notif_data)
            
            # Try to send via Telegram (simplified)
            # In real implementation, you would use Telegram's sendMessage
            
            return True
            
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False
    
    async def send_bulk_notification(self, user_ids: List[int], title: str, 
                                   message: str, notification_type: str = "info") -> Dict:
        """Send notification to multiple users"""
        results = {
            'total': len(user_ids),
            'success': 0,
            'failed': 0,
            'failed_ids': []
        }
        
        for user_id in user_ids:
            success = await self.send_notification(user_id, title, message, notification_type)
            
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
                results['failed_ids'].append(user_id)
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.1)
        
        return results
    
    async def send_admin_alert(self, title: str, message: str, level: str = "info"):
        """Send alert to admin"""
        if not self.config.NOTIFY_OWNER:
            return False
        
        admin_id = self.config.BOT_OWNER_ID
        
        alert_message = f"""
🚨 *{title}*

{message}

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 Level: {level}
        """
        
        return await self.send_notification(admin_id, f"ALERT: {title}", alert_message, "alert")
    
    async def send_startup_message(self):
        """Send bot startup notification"""
        if not self.config.NOTIFY_ON_START:
            return
        
        message = f"""
✅ *MAR PD Bot Started*

🤖 Version: {self.config.BOT_VERSION}
🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🚀 Status: Running
🔧 Mode: {'Development' if self.config.DEBUG_MODE else 'Production'}

🎭 All systems operational!
        """
        
        await self.send_admin_alert("Bot Started", message, "success")
    
    async def send_error_alert(self, error_type: str, error_message: str, context: str = ""):
        """Send error alert to admin"""
        if not self.config.NOTIFY_ON_ERROR:
            return
        
        message = f"""
❌ *Error Alert*

Type: {error_type}
Error: {error_message}
Context: {context}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        await self.send_admin_alert(f"Error: {error_type}", message, "error")
    
    async def send_payment_notification(self, user_id: int, payment_data: Dict):
        """Send payment notification"""
        title = "💰 Payment Update"
        
        if payment_data['status'] == 'completed':
            message = f"""
✅ *Payment Completed*

Amount: {payment_data['amount']} Taka
Points: {payment_data['points']} points
Method: {payment_data['method']}
Time: {datetime.fromisoformat(payment_data['completed_at']).strftime('%Y-%m-%d %H:%M')}
            """
        elif payment_data['status'] == 'verified':
            message = f"""
⏳ *Payment Verified*

Your payment is being processed.
Amount: {payment_data['amount']} Taka
Points: {payment_data['points']} points
            """
        elif payment_data['status'] == 'rejected':
            message = f"""
❌ *Payment Rejected*

Reason: {payment_data.get('admin_note', 'No reason provided')}
Contact admin for more information.
            """
        else:
            return False
        
        return await self.send_notification(user_id, title, message, "payment")
    
    async def send_withdrawal_notification(self, user_id: int, withdrawal_data: Dict):
        """Send withdrawal notification"""
        title = "🏧 Withdrawal Update"
        
        if withdrawal_data['status'] == 'completed':
            message = f"""
✅ *Withdrawal Completed*

Amount: {withdrawal_data['amount_taka']:.2f} Taka
Points: {withdrawal_data['amount_points']} points
Method: {withdrawal_data['method']}
Time: {datetime.fromisoformat(withdrawal_data['processed_at']).strftime('%Y-%m-%d %H:%M')}
            """
        elif withdrawal_data['status'] == 'rejected':
            message = f"""
❌ *Withdrawal Rejected*

Reason: {withdrawal_data.get('admin_note', 'No reason provided')}
Points have been refunded to your account.
            """
        else:
            message = f"""
⏳ *Withdrawal Processing*

Your withdrawal request is being processed.
Amount: {withdrawal_data['amount_taka']:.2f} Taka
Points: {withdrawal_data['amount_points']} points
            """
        
        return await self.send_notification(user_id, title, message, "withdrawal")
    
    async def send_daily_summary(self, user_id: int, stats: Dict):
        """Send daily summary to user"""
        if not stats:
            return False
        
        title = "📊 Daily Summary"
        
        message = f"""
📅 *Your Daily Activity*

💰 Points Earned: {stats.get('points_earned', 0)}
🎮 Games Played: {stats.get('games_played', 0)}
💬 Messages Sent: {stats.get('messages_sent', 0)}
🔥 Current Streak: {stats.get('streak_days', 0)} days

📈 Total Points: {stats.get('total_points', 0)}
🏆 Global Rank: #{stats.get('rank', 'N/A')}

💡 Don't forget to claim your daily bonus tomorrow!
        """
        
        return await self.send_notification(user_id, title, message, "summary")
    
    async def get_user_notifications(self, user_id: int, unread_only: bool = False, 
                                   limit: int = 20) -> List[Dict]:
        """Get user notifications"""
        try:
            notif_ref = self.db.db.collection('notifications')
            query = notif_ref.where('user_id', '==', str(user_id))
            
            if unread_only:
                query = query.where('read', '==', False)
            
            query = query.order_by('created_at', direction='DESCENDING').limit(limit)
            
            docs = query.stream()
            notifications = []
            
            for doc in docs:
                notif_data = doc.to_dict()
                notif_data['id'] = doc.id
                notifications.append(notif_data)
            
            return notifications
            
        except Exception as e:
            print(f"Error getting notifications: {e}")
            return []
    
    async def mark_as_read(self, user_id: int, notification_id: str = None) -> bool:
        """Mark notification(s) as read"""
        try:
            notif_ref = self.db.db.collection('notifications')
            
            if notification_id:
                # Mark single notification
                notif_ref.document(notification_id).update({'read': True})
            else:
                # Mark all user notifications
                query = notif_ref.where('user_id', '==', str(user_id)).where('read', '==', False)
                docs = query.stream()
                
                for doc in docs:
                    doc.reference.update({'read': True})
            
            return True
            
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False
    
    async def cleanup_old_notifications(self, days: int = 30):
        """Cleanup old notifications"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()
            
            notif_ref = self.db.db.collection('notifications')
            query = notif_ref.where('created_at', '<', cutoff_str)
            
            docs = query.limit(1000).stream()
            deleted_count = 0
            
            for doc in docs:
                doc.reference.delete()
                deleted_count += 1
            
            print(f"🧹 Cleaned up {deleted_count} old notifications")
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up notifications: {e}")
            return 0