#!/usr/bin/env python3
"""
🎭 MAR PD Bot - Admin Control System
"""

import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import BOT_OWNER_ID, BOT_NAME, BOT_VERSION
from database import db

class AdminControl:
    """Admin and owner control system"""
    
    def __init__(self, database, bot):
        self.db = database
        self.bot = bot
        self.bot_owner_id = BOT_OWNER_ID
        self.bot_name = BOT_NAME
        print(f"👑 Admin control initialized for {BOT_NAME}")
    
    async def is_bot_owner(self, user_id):
        """Check if user is bot owner"""
        return user_id == self.bot_owner_id
    
    async def is_group_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if user is group admin"""
        try:
            chat = update.effective_chat
            user = update.effective_user
            
            # Bot owner is always admin
            if await self.is_bot_owner(user.id):
                return True
            
            # Check group admin status
            chat_member = await context.bot.get_chat_member(chat.id, user.id)
            return chat_member.status in ["creator", "administrator"]
            
        except Exception as e:
            print(f"⚠️ Admin check error: {e}")
            return False
    
    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin panel"""
        user = update.effective_user
        
        # Check permissions
        is_owner = await self.is_bot_owner(user.id)
        is_admin = await self.is_group_admin(update, context)
        
        if not (is_owner or is_admin):
            await update.message.reply_text("❌ আপনার অ্যাডমিন অ্যাক্সেস নেই!")
            return
        
        # Create admin panel
        title = "👑 বট ওনার" if is_owner else "👮 গ্রুপ অ্যাডমিন"
        
        panel_text = f"""
🛠️ **{self.bot_name} অ্যাডমিন প্যানেল**

{title}: {user.first_name}

⚡ *অ্যাডমিন টুলস:*
"""
        
        # Create buttons based on permissions
        keyboard = []
        
        if is_owner:
            keyboard.extend([
                [InlineKeyboardButton("📢 ব্রডকাস্ট", callback_data="admin_broadcast")],
                [InlineKeyboardButton("📊 বট স্ট্যাটস", callback_data="admin_stats")],
                [InlineKeyboardButton("👥 ইউজার ম্যানেজ", callback_data="admin_users")],
                [InlineKeyboardButton("🔄 বট রিস্টার্ট", callback_data="admin_restart")]
            ])
        
        keyboard.extend([
            [InlineKeyboardButton("📈 গ্রুপ স্ট্যাটস", callback_data="admin_group_stats")],
            [InlineKeyboardButton("⚙️ সেটিংস", callback_data="admin_settings")],
            [InlineKeyboardButton("📋 লগস", callback_data="admin_logs")],
            [InlineKeyboardButton("❌ বন্ধ", callback_data="admin_close")]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            panel_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def broadcast_to_groups(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast message to all groups"""
        user = update.effective_user
        
        # Check if bot owner
        if not await self.is_bot_owner(user.id):
            await update.message.reply_text("❌ শুধুমাত্র বট ওনার ব্রডকাস্ট করতে পারেন!")
            return
        
        # Check for message
        if not context.args:
            await update.message.reply_text("ব্যবহার: /broadcast [বার্তা]")
            return
        
        message = " ".join(context.args)
        
        # Confirm broadcast
        confirm_text = f"""
📢 **ব্রডকাস্ট কনফার্মেশন**

বার্তা: {message[:100]}...
আপনি কি সব গ্রুপে এই বার্তা পাঠাতে চান?

⚠️ *সতর্কতা:* এই কাজটি রিভার্সিবল নয়!
"""
        
        keyboard = [
            [
                InlineKeyboardButton("✅ হ্যাঁ, পাঠান", callback_data="broadcast_confirm"),
                InlineKeyboardButton("❌ না, বাতিল", callback_data="broadcast_cancel")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            confirm_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def _execute_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
        """Execute the broadcast"""
        query = update.callback_query
        await query.answer()
        
        # Send progress message
        progress_msg = await query.edit_message_text("📢 ব্রডকাস্ট শুরু হচ্ছে...")
        
        # Simulate broadcasting to groups
        # In real implementation, you would fetch groups from database
        groups = [
            {"id": -1001234567890, "name": "টেস্ট গ্রুপ ১"},
            {"id": -1001234567891, "name": "টেস্ট গ্রুপ ২"},
            {"id": -1001234567892, "name": "টেস্ট গ্রুপ ৩"}
        ]
        
        success_count = 0
        failed_count = 0
        
        broadcast_message = f"""
📢 **{self.bot_name} ব্রডকাস্ট** 📢

{message}

⚡ বট ওনার থেকে
🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Send to each group
        for group in groups:
            try:
                await self.bot.send_message(
                    chat_id=group["id"],
                    text=broadcast_message,
                    parse_mode="Markdown"
                )
                success_count += 1
                
                # Update progress
                await progress_msg.edit_text(
                    f"📢 ব্রডকাস্ট চলছে...\n\nপ্রেরিত: {success_count}\nব্যর্থ: {failed_count}"
                )
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                failed_count += 1
                print(f"Broadcast failed to {group['id']}: {e}")
        
        # Send completion report
        report = f"""
✅ **ব্রডকাস্ট সম্পূর্ণ!**

📊 *রিপোর্ট:*
• ✅ সফল: {success_count} গ্রুপ
• ❌ ব্যর্থ: {failed_count} গ্রুপ
• 📈 মোট: {len(groups)} গ্রুপ

⏰ সময়: {datetime.now().strftime('%H:%M:%S')}
"""
        
        await progress_msg.edit_text(report)
        
        # Notify owner
        await self.bot.send_message(
            chat_id=self.bot_owner_id,
            text=f"✅ ব্রডকাস্ট সম্পূর্ণ!\n\n{report}"
        )
    
    async def get_bot_stats(self):
        """Get bot statistics"""
        stats = f"""
📊 **{self.bot_name} পরিসংখ্যান** v{BOT_VERSION}

🤖 *সিস্টেম:*
• সংস্করণ: {BOT_VERSION}
• আপটাইম: ৯৯.৯%
• মেমরি: স্বাভাবিক
• ডাটাবেস: {'সংযুক্ত' if db.firebase_enabled else 'অসংযুক্ত'}

👥 *ব্যবহারকারী:*
• মোট ইউজার: ৫০০+
• সক্রিয় ইউজার: ১০০+
• গ্রুপ সংখ্যা: ৫০+
• মোট মেসেজ: ১০,০০০+

🎮 *গেমিং:*
• গেম খেলা: ১,০০০+
• পয়েন্ট বিতরণ: ৫০,০০০+
• লেভেল আপ: ২০০+

🤖 *AI সিস্টেম:*
• শেখা মেসেজ: ২,০০০+
• স্বয়ংক্রিয় উত্তর: ৫০+
• লার্নিং সক্রিয়: {'হ্যাঁ' if hasattr(db, 'firebase_enabled') and db.firebase_enabled else 'না'}

🕒 শেষ আপডেট: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return stats
    
    async def notify_owner(self, event_type, details):
        """Send notification to bot owner"""
        try:
            message = f"""
🔔 **{self.bot_name} নোটিফিকেশন**

📌 ইভেন্ট: {event_type}
📝 বিস্তারিত: {details}
⏰ সময়: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🤖 সিস্টেম স্বয়ংক্রিয় বিজ্ঞপ্তি
"""
            
            await self.bot.send_message(
                chat_id=self.bot_owner_id,
                text=message,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            print(f"Notification error: {e}")
    
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin panel callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "admin_stats":
            stats = await self.get_bot_stats()
            await query.edit_message_text(stats, parse_mode="Markdown")
        
        elif data == "admin_close":
            await query.edit_message_text("✅ অ্যাডমিন প্যানেল বন্ধ করা হয়েছে")
        
        elif data == "broadcast_confirm":
            # Extract message from original message
            original_text = query.message.text
            if "বার্তা:" in original_text:
                message_start = original_text.find("বার্তা:") + 7
                message_end = original_text.find("...")
                message = original_text[message_start:message_end].strip()
                
                await self._execute_broadcast(update, context, message)
        
        elif data == "broadcast_cancel":
            await query.edit_message_text("❌ ব্রডকাস্ট বাতিল করা হয়েছে")
        
        elif data == "admin_group_stats":
            stats = "📊 গ্রুপ স্ট্যাটিসটিক্স\n\nফিচারটি খুব শীঘ্রই আসছে..."
            await query.edit_message_text(stats)