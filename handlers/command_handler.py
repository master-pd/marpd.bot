from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import html

class CommandHandler:
    """Handle all bot commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.db = bot.db
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        # Register user
        await self.db.register_user(user_id, user.first_name, user.username)
        
        # Send welcome message
        welcome = f"""
🎭 *MAR PD Bot এ স্বাগতম {user.first_name}!* 🎭

🚀 *উন্নত ফিচার সমূহ:*
• 🤖 এআই চ্যাট (ইউজার থেকে শিখে)
• 🎮 ২০+ গেমিং অপশন
• 💰 পয়েন্ট সিস্টেম
• 💸 বিকাশ/নগদ পেমেন্ট
• 📊 ফায়ারস্টোর ডাটাবেস
• 🔧 ম্যানুয়াল ম্যানেজমেন্ট
• 🛒 ভার্চুয়াল শপ
• 📈 রিয়েল-টাইম অ্যানালিটিক্স

🎯 *কমান্ড সমূহ:*
/start - বট শুরু করুন
/menu - মেইন মেনু
/help - সাহায্য
/game - গেম খেলুন
/points - পয়েন্ট চেক
/shop - শপ দেখুন
/recharge - রিচার্জ করুন
/withdraw - উইথড্র করুন
/profile - আপনার প্রোফাইল
/leaderboard - লিডারবোর্ড
/daily - ডেইলি বোনাস
/refer - রেফার করুন
/settings - সেটিংস

💡 *টিপ:* সরাসরি মেসেজ লিখলে AI রেসপন্স দিবে!
        """
        
        keyboard = [
            [InlineKeyboardButton("🎮 গেম খেলুন", callback_data="game_menu")],
            [InlineKeyboardButton("💰 পয়েন্ট চেক", callback_data="check_points")],
            [InlineKeyboardButton("🛒 শপ", callback_data="shop_menu")],
            [InlineKeyboardButton("💸 রিচার্জ", callback_data="recharge_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /menu command"""
        keyboard = [
            [
                InlineKeyboardButton("🤖 AI চ্যাট", callback_data="ai_chat"),
                InlineKeyboardButton("🎮 গেমস", callback_data="game_menu")
            ],
            [
                InlineKeyboardButton("💰 পয়েন্ট", callback_data="points_menu"),
                InlineKeyboardButton("💸 পেমেন্ট", callback_data="payment_menu")
            ],
            [
                InlineKeyboardButton("🛒 শপ", callback_data="shop_menu"),
                InlineKeyboardButton("👤 প্রোফাইল", callback_data="profile")
            ],
            [
                InlineKeyboardButton("📊 লিডারবোর্ড", callback_data="leaderboard"),
                InlineKeyboardButton("⚙️ সেটিংস", callback_data="settings")
            ],
            [
                InlineKeyboardButton("👮 অ্যাডমিন", callback_data="admin_panel"),
                InlineKeyboardButton("🆘 সাহায্য", callback_data="help")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎭 *MAR PD Bot - মেইন মেনু*\n\nনিচের বাটন থেকে নির্বাচন করুন:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🆘 *MAR PD Bot - সাহায্য*

🎯 *মূল কমান্ড:*
/start - বট শুরু
/menu - মেনু দেখান
/help - সাহায্য

💰 *পয়েন্ট সিস্টেম:*
/points - আপনার পয়েন্ট চেক
/send - অন্যকে পয়েন্ট পাঠান
/daily - ডেইলি বোনাস নিন
/refer - বন্ধুকে রেফার করুন

🎮 *গেমিং:*
/game - গেম খেলুন
/leaderboard - লিডারবোর্ড দেখুন

💸 *পেমেন্ট:*
/recharge - পয়েন্ট কিনুন
/withdraw - পয়েন্ট ক্যাশ আউট করুন

🛒 *শপ:*
/shop - শপ দেখুন
/inventory - আপনার আইটেম দেখুন

👤 *অ্যাকাউন্ট:*
/profile - প্রোফাইল দেখুন
/settings - সেটিংস

👮 *এডমিন:*
/admin - এডমিন প্যানেল (এডমিনদের জন্য)

💡 *টিপস:*
• প্রতিদিন /daily কমান্ড দিয়ে বোনাস নিন
• বন্ধুদের রেফার করে অতিরিক্ত পয়েন্ট পান
• গেম খেলে বড় অঙ্কের পয়েন্ট জিতুন
• AI এর সাথে সরাসরি চ্যাট করুন

📞 *সাপোর্ট:*
সমস্যা হলে: @mar_pd_support
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def points(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /points command"""
        user_id = update.effective_user.id
        user = await self.db.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ ইউজার ডাটা পাওয়া যায়নি!")
            return
        
        points = user.get('points', 0)
        total_earned = user.get('total_points_earned', 0)
        total_spent = user.get('total_points_spent', 0)
        
        # Get rank
        leaderboard = await self.db.get_leaderboard(limit=1000)
        rank = None
        
        for i, entry in enumerate(leaderboard, 1):
            if entry['user_id'] == str(user_id):
                rank = i
                break
        
        message = f"""
💰 *পয়েন্ট স্ট্যাটাস*

🪙 বর্তমান পয়েন্ট: *{points:,}*
📊 টোটাল আয়: *{total_earned:,}*
💸 টোটাল খরচ: *{total_spent:,}*
📈 নেট ওয়ার্থ: *{total_earned - total_spent:,}*
        """
        
        if rank:
            message += f"\n🏆 গ্লোবাল র‌্যাংক: *#{rank}*"
        
        # Add quick actions
        keyboard = [
            [
                InlineKeyboardButton("💸 রিচার্জ", callback_data="recharge_menu"),
                InlineKeyboardButton("🏧 উইথড্র", callback_data="withdraw_menu")
            ],
            [
                InlineKeyboardButton("📤 পাঠান", callback_data="send_points"),
                InlineKeyboardButton("📊 ডিটেইলস", callback_data="points_details")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /game command"""
        games = await self.bot.gaming.get_available_games()
        
        if not games:
            await update.message.reply_text("❌ কোনো গেম পাওয়া যায়নি!")
            return
        
        # Create game buttons (4 per row)
        keyboard = []
        row = []
        
        for i, game in enumerate(games[:12]):  # Show first 12 games
            row.append(InlineKeyboardButton(
                game['name'],
                callback_data=f"game_start_{game['id']}"
            ))
            
            if len(row) == 2:  # 2 buttons per row
                keyboard.append(row)
                row = []
        
        if row:  # Add remaining buttons
            keyboard.append(row)
        
        # Add navigation buttons
        keyboard.append([
            InlineKeyboardButton("📊 আমার স্ট্যাটস", callback_data="game_stats"),
            InlineKeyboardButton("🔙 মেনু", callback_data="main_menu")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎮 *গেমস মেনু*\n\nনিচের গেমস থেকে নির্বাচন করুন:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def shop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /shop command"""
        categories = {
            'vip': '⭐ VIP প্যাকেজ',
            'boost': '⚡ বুস্ট',
            'cosmetic': '🎨 কসমেটিক',
            'game_item': '🎮 গেম আইটেম'
        }
        
        keyboard = []
        for cat_id, cat_name in categories.items():
            keyboard.append([InlineKeyboardButton(cat_name, callback_data=f"shop_category_{cat_id}")])
        
        keyboard.append([
            InlineKeyboardButton("📦 ইনভেন্টরি", callback_data="inventory"),
            InlineKeyboardButton("💰 পয়েন্ট", callback_data="check_points")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🛒 *শপ মেনু*\n\nক্যাটেগরি নির্বাচন করুন:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def recharge(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /recharge command"""
        methods = await self.bot.payment.get_payment_methods()
        
        keyboard = []
        for method in methods:
            keyboard.append([
                InlineKeyboardButton(
                    f"{method['name']} - {method['number']}",
                    callback_data=f"recharge_method_{method['id']}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("📜 হিস্ট্রি", callback_data="payment_history"),
            InlineKeyboardButton("🔙 বাক", callback_data="payment_menu")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """
💸 *রিচার্জ পয়েন্ট*

📱 *পেমেন্ট মেথড:*
• বিকাশ - {}
• নগদ - {}

💡 *নির্দেশনা:*
1. উপরের নাম্বারে টাকা সেন্ড করুন
2. ট্রানজেকশন আইডি নোট করুন
3. স্ক্রিনশট সেভ করুন
4. এডমিনকে প্রুফ পাঠান
5. এডমিন ম্যানুয়ালি পয়েন্ট যোগ করবেন

⚡ *রেট:* ১ টাকা = ১০ পয়েন্ট
        """.format(methods[0]['number'], methods[1]['number'])
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def withdraw(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /withdraw command"""
        user_id = update.effective_user.id
        user = await self.db.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ ইউজার ডাটা পাওয়া যায়নি!")
            return
        
        points = user.get('points', 0)
        min_withdraw = self.config.MIN_WITHDRAW
        fee_percent = self.config.WITHDRAW_FEE * 100
        
        if points < min_withdraw:
            await update.message.reply_text(
                f"❌ ন্যূনতম {min_withdraw} পয়েন্ট প্রয়োজন।\n"
                f"আপনার আছে {points} পয়েন্ট।\n\n"
                f"পয়েন্ট বাড়াতে:\n"
                f"• প্রতিদিন /daily কমান্ড দিন\n"
                f"• গেম খেলুন /game\n"
                f"• বন্ধুদের রেফার করুন /refer\n"
                f"• রিচার্জ করুন /recharge"
            )
            return
        
        # Calculate withdrawal amounts
        amounts = [
            min_withdraw,
            500,
            1000,
            2000,
            5000
        ]
        
        keyboard = []
        for amount in amounts:
            if amount <= self.config.MAX_WITHDRAW:
                fee = int(amount * self.config.WITHDRAW_FEE)
                net_points = amount - fee
                net_taka = net_points / self.config.RECHARGE_RATE
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"{amount} পয়েন্ট → {net_taka:.0f} টাকা",
                        callback_data=f"withdraw_amount_{amount}"
                    )
                ])
        
        keyboard.append([
            InlineKeyboardButton("📜 হিস্ট্রি", callback_data="withdrawal_history"),
            InlineKeyboardButton("🔙 বাক", callback_data="payment_menu")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
🏧 *উইথড্র পয়েন্ট*

💰 *আপনার পয়েন্ট:* {points:,}
💸 *ন্যূনতম:* {min_withdraw} পয়েন্ট
📉 *ফি:* {fee_percent}%
⚡ *রেট:* ১০ পয়েন্ট = ১ টাকা

💡 *উইথড্র পদ্ধতি:*
1. পয়েন্ট নির্বাচন করুন
2. বিকাশ/নগদ নম্বর দিন
3. এডমিন ম্যানুয়ালি টাকা পাঠাবেন
4. সময় লাগতে পারে ২৪-৪৮ ঘন্টা

⚠️ *সতর্কতা:* ভুল নম্বর দিলে টাকা ফেরত যাবে না।
        """
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def send_points(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /send command"""
        if context.args:
            # If arguments provided, process directly
            if len(context.args) >= 2:
                receiver = context.args[0]
                try:
                    points = int(context.args[1])
                    note = " ".join(context.args[2:]) if len(context.args) > 2 else ""
                    
                    success, message = await self.bot.economy.send_points(
                        update.effective_user.id,
                        receiver,
                        points,
                        note
                    )
                    
                    await update.message.reply_text(message, parse_mode='Markdown')
                    return
                    
                except ValueError:
                    await update.message.reply_text("❌ পয়েন্ট একটি সংখ্যা হতে হবে!")
                    return
        
        # Show send form
        text = """
📤 *পয়েন্ট পাঠান*

📋 *ফর্ম্যাট:*
`/send ইউজারনেম পয়েন্ট নোট`

📝 *উদাহরণ:*
`/send @username 100 ধন্যবাদ`
`/send 123456789 500 গিফট`

💡 *টিপস:*
• ইউজারনেম (@username) বা ইউজার আইডি ব্যবহার করুন
• নোট অপশনাল (সর্বোচ্চ ৫০ অক্ষর)
• একবারে সর্বোচ্চ ১০,০০০ পয়েন্ট পাঠাতে পারবেন
        """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command"""
        user = update.effective_user
        user_id = user.id
        
        user_data = await self.db.get_user(user_id)
        if not user_data:
            await update.message.reply_text("❌ ইউজার ডাটা পাওয়া যায়নি!")
            return
        
        # Get economy stats
        economy_stats = await self.bot.economy.get_user_economy_stats(user_id)
        
        # Get VIP status
        vip_status = await self.bot.shop.get_vip_status(user_id)
        
        # Format profile
        profile = f"""
👤 *প্রোফাইল*

🆔 *আইডি:* `{user_id}`
📛 *নাম:* {user.first_name}
📧 *ইউজারনেম:* @{user.username if user.username else 'N/A'}
📅 *জয়েন তারিখ:* {user_data.get('created_at', 'Unknown')[:10]}

💰 *ইকোনমি:*
• বর্তমান পয়েন্ট: *{user_data.get('points', 0):,}*
• টোটাল আয়: *{economy_stats.get('total_earned', 0):,}*
• টোটাল খরচ: *{economy_stats.get('total_spent', 0):,}*
• নেট ওয়ার্থ: *{economy_stats.get('net_worth', 0):,}*

📊 *স্ট্যাটিস্টিক্স:*
• মেসেজ: *{economy_stats.get('message_count', 0)}*
• গেম: *{economy_stats.get('game_count', 0)}*
• রেফারাল: *{economy_stats.get('referral_count', 0)}*
• স্ট্রিক: *{economy_stats.get('streak_days', 0)} দিন*
        """
        
        # Add VIP status if active
        if vip_status.get('active'):
            profile += f"\n⭐ *VIP স্ট্যাটাস:* সক্রিয়\n"
            profile += f"⏳ শেষ হয়: {vip_status.get('remaining_days', 0)} দিন\n"
        
        keyboard = [
            [
                InlineKeyboardButton("📊 বিস্তারিত", callback_data="profile_details"),
                InlineKeyboardButton("💰 পয়েন্ট", callback_data="check_points")
            ],
            [
                InlineKeyboardButton("🎮 গেম স্ট্যাটস", callback_data="game_stats"),
                InlineKeyboardButton("📜 ট্রানজেকশন", callback_data="transaction_history")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(profile, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /leaderboard command"""
        leaderboard = await self.bot.economy.get_richest_users(limit=20)
        
        if not leaderboard:
            await update.message.reply_text("❌ লিডারবোর্ড ডাটা পাওয়া যায়নি!")
            return
        
        # Format leaderboard
        text = "🏆 *লিডারবোর্ড*\n\n"
        
        for entry in leaderboard[:10]:  # Show top 10
            medal = ""
            if entry['rank'] == 1:
                medal = "🥇 "
            elif entry['rank'] == 2:
                medal = "🥈 "
            elif entry['rank'] == 3:
                medal = "🥉 "
            
            text += f"{medal}*#{entry['rank']}* {entry['name']}\n"
            text += f"   💰 {entry['points']:,} পয়েন্ট | 📝 {entry['message_count']} মেসেজ\n\n"
        
        # Add user's rank if not in top 10
        user_id = update.effective_user.id
        user_rank = None
        
        for entry in leaderboard:
            if entry['user_id'] == str(user_id):
                user_rank = entry['rank']
                break
        
        if user_rank and user_rank > 10:
            user_entry = next((e for e in leaderboard if e['user_id'] == str(user_id)), None)
            if user_entry:
                text += f"\n📊 *আপনার র‌্যাংক:* #{user_rank}\n"
                text += f"💰 পয়েন্ট: {user_entry['points']:,}\n"
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 রিফ্রেশ", callback_data="leaderboard_refresh"),
                InlineKeyboardButton("📊 আমার র‌্যাংক", callback_data="my_rank")
            ],
            [
                InlineKeyboardButton("🎮 গেম লিডারবোর্ড", callback_data="game_leaderboard"),
                InlineKeyboardButton("🔙 মেনু", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def daily_bonus(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /daily command"""
        success, message, amount = await self.bot.economy.add_daily_bonus(update.effective_user.id)
        
        if success:
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text(message)
    
    async def refer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /refer command"""
        user_id = update.effective_user.id
        user = await self.db.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ ইউজার ডাটা পাওয়া যায়নি!")
            return
        
        referral_code = user.get('referral_code', 'N/A')
        referral_count = len(user.get('referrals', []))
        referral_earnings = user.get('stats', {}).get('referral_earnings', 0)
        
        text = f"""
👥 *রেফার অ্যান্ড আর্ন*

🎯 *আপনার রেফার লিংক:*
`https://t.me/{self.config.BOT_USERNAME[1:]}?start={referral_code}`

💰 *রেফার বোনাস:*
• আপনি পান: {self.config.REFERRAL_BONUS} পয়েন্ট
• বন্ধু পান: ৫০ পয়েন্ট
• প্রতি রেফারেলের জন্য

📊 *আপনার রেফার স্ট্যাটস:*
• টোটাল রেফার: {referral_count}
• টোটাল আয়: {referral_earnings} পয়েন্ট

💡 *কিভাবে রেফার করবেন:*
1. উপরের লিংক শেয়ার করুন
2. বন্ধু লিংক ক্লিক করে বটে জয়েন করবে
3. বটে /start দিবে
4. অটোমেটিক বোনাস যোগ হবে

📝 *নোট:* শুধুমাত্র নতুন ইউজারদের জন্য কাজ করবে
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📋 লিংক কপি", callback_data="copy_referral_link"),
                InlineKeyboardButton("📊 ডিটেইলস", callback_data="referral_details")
            ],
            [
                InlineKeyboardButton("👥 রেফার লিস্ট", callback_data="referral_list"),
                InlineKeyboardButton("🔙 মেনু", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        user_id = update.effective_user.id
        
        if not self.bot.admin.is_admin(user_id):
            await update.message.reply_text("❌ শুধুমাত্র এডমিনের জন্য!")
            return
        
        keyboard = [
            [
                InlineKeyboardButton("👥 ইউজার ম্যানেজ", callback_data="admin_users"),
                InlineKeyboardButton("💰 পয়েন্ট ম্যানেজ", callback_data="admin_points")
            ],
            [
                InlineKeyboardButton("💸 পেমেন্ট ম্যানেজ", callback_data="admin_payments"),
                InlineKeyboardButton("📊 স্ট্যাটিস্টিক্স", callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton("🤖 AI ম্যানেজ", callback_data="admin_ai"),
                InlineKeyboardButton("⚙️ সিস্টেম", callback_data="admin_system")
            ],
            [
                InlineKeyboardButton("📢 ব্রডকাস্ট", callback_data="admin_broadcast"),
                InlineKeyboardButton("💾 ব্যাকআপ", callback_data="admin_backup")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👮 *এডমিন প্যানেল*\n\nনিচের অপশন থেকে নির্বাচন করুন:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        user_id = update.effective_user.id
        user = await self.db.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ ইউজার ডাটা পাওয়া যায়নি!")
            return
        
        settings = user.get('settings', {})
        
        text = f"""
⚙️ *সেটিংস*

🌐 *ভাষা:* {settings.get('language', 'bn').upper()}
🔔 *নোটিফিকেশন:* {'চালু ✅' if settings.get('notifications', True) else 'বন্ধ ❌'}
👤 *প্রোফাইল:* {'প্রাইভেট 🔒' if settings.get('private_profile', False) else 'পাবলিক 🌐'}

💡 *সেটিংস পরিবর্তন:*
• ভাষা পরিবর্তন: /language
• নোটিফিকেশন: /notifications
• প্রোফাইল প্রাইভেসি: /privacy

📱 *অ্যাকাউন্ট:*
• ইউজার আইডি: `{user_id}`
• রেফারাল কোড: `{user.get('referral_code', 'N/A')}`
• একাউন্ট তৈরি: {user.get('created_at', 'Unknown')[:10]}
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🌐 ভাষা", callback_data="change_language"),
                InlineKeyboardButton("🔔 নোটিফিকেশন", callback_data="toggle_notifications")
            ],
            [
                InlineKeyboardButton("👤 প্রাইভেসি", callback_data="toggle_privacy"),
                InlineKeyboardButton("🗑️ অ্যাকাউন্ট", callback_data="account_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')