import asyncio
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class PaymentSystem:
    """Manual Bkash/Nagad Payment System"""
    
    def __init__(self, db):
        self.db = db
        self.config = Config()
        
        # Payment methods
        self.payment_methods = {
            'bkash': {
                'name': 'বিকাশ',
                'number': self.config.BKASH_NUMBER,
                'min_amount': 10,
                'max_amount': 5000,
                'rate': self.config.RECHARGE_RATE  # 1 Taka = 10 points
            },
            'nagad': {
                'name': 'নগদ',
                'number': self.config.NAGAD_NUMBER,
                'min_amount': 10,
                'max_amount': 5000,
                'rate': self.config.RECHARGE_RATE
            }
        }
        
        # Withdrawal settings
        self.withdrawal_settings = {
            'min_amount': self.config.MIN_WITHDRAW,
            'max_amount': self.config.MAX_WITHDRAW,
            'fee_percent': self.config.WITHDRAW_FEE * 100,  # 20%
            'fee_fixed': 0
        }
    
    async def get_payment_methods(self) -> List[Dict]:
        """Get available payment methods"""
        methods = []
        for method_id, method_data in self.payment_methods.items():
            methods.append({
                'id': method_id,
                'name': method_data['name'],
                'number': method_data['number'],
                'min_amount': method_data['min_amount'],
                'max_amount': method_data['max_amount'],
                'rate': method_data['rate']
            })
        return methods
    
    async def validate_payment_amount(self, amount: float, method: str) -> Tuple[bool, str]:
        """Validate payment amount"""
        if method not in self.payment_methods:
            return False, "❌ সাপোর্টেড পেমেন্ট মেথড না"
        
        method_data = self.payment_methods[method]
        
        if amount < method_data['min_amount']:
            return False, f"❌ সর্বনিম্ন {method_data['min_amount']} টাকা প্রয়োজন"
        
        if amount > method_data['max_amount']:
            return False, f"❌ সর্বোচ্চ {method_data['max_amount']} টাকা সেন্ড করতে পারেন"
        
        return True, "✅ পরিমাণ ঠিক আছে"
    
    async def create_payment_request(self, user_id: int, amount: float, method: str) -> Tuple[bool, str, str]:
        """Create payment request"""
        # Validate
        is_valid, message = await self.validate_payment_amount(amount, method)
        if not is_valid:
            return False, message, ""
        
        # Calculate points
        points = int(amount * self.payment_methods[method]['rate'])
        
        # Create payment record
        payment_id = await self.db.create_payment_request(user_id, amount, method)
        
        if not payment_id:
            return False, "❌ পেমেন্ট রিকুয়েস্ট তৈরি ব্যর্থ", ""
        
        # Generate instructions
        method_data = self.payment_methods[method]
        instructions = self._generate_payment_instructions(
            method_data['name'],
            method_data['number'],
            amount,
            points,
            payment_id
        )
        
        return True, instructions, payment_id
    
    def _generate_payment_instructions(self, method_name: str, number: str, amount: float, points: int, payment_id: str) -> str:
        """Generate payment instructions"""
        return f"""
💸 *{method_name} রিচার্জ*

📋 *নির্দেশাবলী:*
1️⃣ {method_name} এ *{number}* নম্বরে *{amount}* টাকা সেন্ড করুন
2️⃣ ট্রানজেকশন আইডি নোট করুন
3️⃣ ট্রানজেকশন স্ক্রিনশট সেভ করুন

💰 *বিবরণ:*
📱 পদ্ধতি: {method_name}
💵 পরিমাণ: {amount} টাকা
🪙 পয়েন্ট: {points} পয়েন্ট
🆔 রিকুয়েস্ট: {payment_id}

📝 *পরবর্তী ধাপ:*
✅ টাকা সেন্ড করার পর নিচের ফর্ম্যাটে মেসেজ দিন:

`verify {payment_id} TX12345678`

📸 *অথবা* স্ক্রিনশট + ট্রানজেকশন আইডি এডমিনকে পাঠান

👮 *এডমিন যোগাযোগ:* @mar_pd_admin
⏱️ *প্রক্রিয়াকরণ:* ২৪ ঘন্টার মধ্যে
        """
    
    async def verify_payment(self, user_id: int, payment_id: str, transaction_id: str) -> Tuple[bool, str]:
        """User submits payment verification"""
        try:
            # Get payment data
            payment_ref = self.db.db.collection('payments').document(payment_id)
            payment_doc = payment_ref.get()
            
            if not payment_doc.exists:
                return False, "❌ পেমেন্ট রিকুয়েস্ট পাওয়া যায়নি"
            
            payment_data = payment_doc.to_dict()
            
            # Check if payment belongs to user
            if payment_data['user_id'] != str(user_id):
                return False, "❌ এই পেমেন্ট রিকুয়েস্ট আপনার না"
            
            # Check status
            if payment_data['status'] != 'pending':
                return False, f"❌ পেমেন্ট ইতিমধ্যে {payment_data['status']} স্ট্যাটাসে আছে"
            
            # Update with transaction ID
            await self.db.update_payment_status(payment_id, 'pending_verification', 
                                              f"Transaction ID: {transaction_id}")
            
            # Update transaction ID
            payment_ref.update({
                'transaction_id': transaction_id,
                'user_verified_at': datetime.now().isoformat()
            })
            
            return True, (
                f"✅ পেমেন্ট ভেরিফিকেশন জমা দেওয়া হয়েছে!\n\n"
                f"🆔 রিকুয়েস্ট: {payment_id}\n"
                f"📱 ট্রানজেকশন: {transaction_id}\n"
                f"💰 পরিমাণ: {payment_data['amount']} টাকা\n"
                f"🪙 পয়েন্ট: {payment_data['points']} পয়েন্ট\n\n"
                f"এডমিন ভেরিফাই করলে পয়েন্ট যোগ করা হবে।"
            )
            
        except Exception as e:
            return False, f"❌ ভেরিফিকেশন ব্যর্থ: {str(e)}"
    
    async def withdraw_request(self, user_id: int, amount: float, method: str, account_number: str) -> Tuple[bool, str]:
        """Request withdrawal"""
        # Validate amount
        if amount < self.withdrawal_settings['min_amount']:
            return False, f"❌ সর্বনিম্ন {self.withdrawal_settings['min_amount']} পয়েন্ট প্রয়োজন"
        
        if amount > self.withdrawal_settings['max_amount']:
            return False, f"❌ সর্বোচ্চ {self.withdrawal_settings['max_amount']} পয়েন্ট উইথড্র করতে পারেন"
        
        # Check user balance
        user = await self.db.get_user(user_id)
        if not user:
            return False, "❌ ইউজার ডাটা পাওয়া যায়নি"
        
        user_points = user.get('points', 0)
        if user_points < amount:
            return False, f"❌ আপনার কাছে {amount} পয়েন্ট নেই। আপনার ব্যালেন্স: {user_points} পয়েন্ট"
        
        # Calculate fee and net amount
        fee = int(amount * self.withdrawal_settings['fee_percent'] / 100)
        net_amount_taka = (amount - fee) / self.config.RECHARGE_RATE
        
        # Create withdrawal record
        withdrawal_data = {
            'user_id': str(user_id),
            'amount_points': amount,
            'amount_taka': net_amount_taka,
            'fee_points': fee,
            'method': method,
            'account_number': account_number,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'processed_at': None,
            'admin_note': None
        }
        
        withdrawal_ref = self.db.db.collection('withdrawals').document()
        withdrawal_ref.set(withdrawal_data)
        
        withdrawal_id = withdrawal_ref.id
        
        # Deduct points immediately
        await self.db.deduct_points(user_id, amount, f"withdrawal_request:{withdrawal_id}")
        
        instructions = self._generate_withdrawal_instructions(
            amount, fee, net_amount_taka, method, account_number, withdrawal_id
        )
        
        return True, instructions
    
    def _generate_withdrawal_instructions(self, amount: int, fee: int, net_taka: float, method: str, account: str, withdrawal_id: str) -> str:
        """Generate withdrawal instructions"""
        return f"""
🏧 *উইথড্র রিকুয়েস্ট*

✅ *রিকুয়েস্ট গ্রহণ করা হয়েছে!*

📋 *বিবরণ:*
🪙 পয়েন্ট: {amount}
💸 ফি: {fee} পয়েন্ট ({self.withdrawal_settings['fee_percent']}%)
💰 নেট টাকা: {net_taka:.2f} ৳
📱 পদ্ধতি: {method}
📞 একাউন্ট: {account}
🆔 রিকুয়েস্ট: {withdrawal_id}

⏳ *প্রক্রিয়াকরণ:*
• পয়েন্ট কাটা হয়েছে
• এডমিন ম্যানুয়ালি টাকা পাঠাবেন
• সময় লাগতে পারে ২৪-৪৮ ঘন্টা

👮 *এডমিন যোগাযোগ:* @mar_pd_admin
📞 *জরুরি:* {self.config.BKASH_NUMBER}

⚠️ *সতর্কতা:* ভুল একাউন্ট নম্বর দিলে টাকা ফেরত যাবে না।
        """
    
    async def get_user_payment_history(self, user_id: int) -> List[Dict]:
        """Get user's payment history"""
        try:
            payments_ref = self.db.db.collection('payments')
            query = payments_ref \
                .where('user_id', '==', str(user_id)) \
                .order_by('created_at', direction='DESCENDING') \
                .limit(20)
            
            docs = query.stream()
            payments = []
            
            for doc in docs:
                payment_data = doc.to_dict()
                payment_data['id'] = doc.id
                payments.append(payment_data)
            
            return payments
            
        except Exception as e:
            print(f"Error getting payment history: {e}")
            return []
    
    async def get_user_withdrawal_history(self, user_id: int) -> List[Dict]:
        """Get user's withdrawal history"""
        try:
            withdrawals_ref = self.db.db.collection('withdrawals')
            query = withdrawals_ref \
                .where('user_id', '==', str(user_id)) \
                .order_by('created_at', direction='DESCENDING') \
                .limit(20)
            
            docs = query.stream()
            withdrawals = []
            
            for doc in docs:
                withdrawal_data = doc.to_dict()
                withdrawal_data['id'] = doc.id
                withdrawals.append(withdrawal_data)
            
            return withdrawals
            
        except Exception as e:
            print(f"Error getting withdrawal history: {e}")
            return []
    
    async def get_pending_withdrawals(self) -> List[Dict]:
        """Get all pending withdrawals"""
        try:
            withdrawals_ref = self.db.db.collection('withdrawals')
            query = withdrawals_ref.where('status', '==', 'pending')
            
            docs = query.stream()
            withdrawals = []
            
            for doc in docs:
                withdrawal_data = doc.to_dict()
                withdrawal_data['id'] = doc.id
                withdrawals.append(withdrawal_data)
            
            return withdrawals
            
        except Exception as e:
            print(f"Error getting pending withdrawals: {e}")
            return []
    
    async def process_withdrawal(self, admin_id: int, withdrawal_id: str, status: str, note: str = "") -> Tuple[bool, str]:
        """Process withdrawal request (admin only)"""
        try:
            withdrawal_ref = self.db.db.collection('withdrawals').document(withdrawal_id)
            withdrawal_doc = withdrawal_ref.get()
            
            if not withdrawal_doc.exists:
                return False, "❌ উইথড্র রিকুয়েস্ট পাওয়া যায়নি"
            
            withdrawal_data = withdrawal_doc.to_dict()
            
            if withdrawal_data['status'] != 'pending':
                return False, f"❌ উইথড্র ইতিমধ্যে {withdrawal_data['status']} স্ট্যাটাসে আছে"
            
            # Update status
            update_data = {
                'status': status,
                'processed_at': datetime.now().isoformat(),
                'processed_by': str(admin_id),
                'admin_note': note
            }
            
            withdrawal_ref.update(update_data)
            
            user_id = int(withdrawal_data['user_id'])
            
            if status == 'completed':
                # Send success notification
                message = (
                    f"✅ *উইথড্র সম্পন্ন!*\n\n"
                    f"🆔 রিকুয়েস্ট: {withdrawal_id}\n"
                    f"💰 টাকা: {withdrawal_data['amount_taka']:.2f} ৳\n"
                    f"📱 পদ্ধতি: {withdrawal_data['method']}\n"
                    f"📞 একাউন্ট: {withdrawal_data['account_number']}\n"
                    f"📅 তারিখ: {datetime.now().strftime('%d/%m/%Y')}\n\n"
                    f"টাকা পাঠানো হয়েছে, কিছুক্ষণের মধ্যে পেয়ে যাবেন।"
                )
                
                return True, f"✅ উইথড্র সম্পন্ন করা হয়েছে\n\nUser ID: {user_id}\nAmount: {withdrawal_data['amount_taka']:.2f} ৳"
            
            elif status == 'rejected':
                # Refund points
                amount_points = withdrawal_data['amount_points']
                await self.db.add_points(user_id, amount_points, f"withdrawal_refund:{withdrawal_id}")
                
                message = (
                    f"❌ *উইথড্র বাতিল!*\n\n"
                    f"🆔 রিকুয়েস্ট: {withdrawal_id}\n"
                    f"🪙 পয়েন্ট: {amount_points} (ফেরত দেওয়া হয়েছে)\n"
                    f"📋 কারণ: {note}\n\n"
                    f"আপনার পয়েন্ট ফেরত দেওয়া হয়েছে।"
                )
                
                return True, f"✅ উইথড্র বাতিল করা হয়েছে, পয়েন্ট ফেরত দেওয়া হয়েছে\n\nUser ID: {user_id}\nPoints: {amount_points}"
            
            else:
                return True, f"✅ উইথড্র স্ট্যাটাস আপডেট করা হয়েছে: {status}"
            
        except Exception as e:
            return False, f"❌ প্রসেস ব্যর্থ: {str(e)}"
    
    async def get_payment_stats(self) -> Dict:
        """Get payment statistics"""
        try:
            # Total payments
            payments_ref = self.db.db.collection('payments')
            payments_docs = payments_ref.limit(1000).stream()
            
            total_payments = 0
            total_amount = 0
            total_points = 0
            
            for doc in payments_docs:
                payment_data = doc.to_dict()
                if payment_data['status'] == 'completed':
                    total_payments += 1
                    total_amount += payment_data['amount']
                    total_points += payment_data['points']
            
            # Total withdrawals
            withdrawals_ref = self.db.db.collection('withdrawals')
            withdrawals_docs = withdrawals_ref.limit(1000).stream()
            
            total_withdrawals = 0
            total_withdrawn_points = 0
            total_withdrawn_taka = 0
            
            for doc in withdrawals_docs:
                withdrawal_data = doc.to_dict()
                if withdrawal_data['status'] == 'completed':
                    total_withdrawals += 1
                    total_withdrawn_points += withdrawal_data['amount_points']
                    total_withdrawn_taka += withdrawal_data['amount_taka']
            
            return {
                'total_payments': total_payments,
                'total_amount': total_amount,
                'total_points_added': total_points,
                'total_withdrawals': total_withdrawals,
                'total_points_withdrawn': total_withdrawn_points,
                'total_taka_withdrawn': total_withdrawn_taka,
                'pending_payments': len(await self.db.get_pending_payments()),
                'pending_withdrawals': len(await self.get_pending_withdrawals())
            }
            
        except Exception as e:
            print(f"Error getting payment stats: {e}")
            return {
                'total_payments': 0,
                'total_amount': 0,
                'total_points_added': 0,
                'total_withdrawals': 0,
                'total_points_withdrawn': 0,
                'total_taka_withdrawn': 0,
                'pending_payments': 0,
                'pending_withdrawals': 0
            }
    
    def extract_transaction_id(self, text: str, method: str) -> Optional[str]:
        """Extract transaction ID from text"""
        patterns = {
            'bkash': [
                r'TRXID[: ]*([A-Z0-9]{10})',
                r'Transaction ID[: ]*([A-Z0-9]{10})',
                r'TX[: ]*([A-Z0-9]{10})',
                r'([A-Z0-9]{10})'
            ],
            'nagad': [
                r'TxnID[: ]*([A-Z0-9]{8,12})',
                r'Transaction[: ]*([A-Z0-9]{8,12})',
                r'Nagad[: ].*?([A-Z0-9]{8,12})'
            ]
        }
        
        if method in patterns:
            for pattern in patterns[method]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return None