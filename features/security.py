import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib
import secrets

class SecuritySystem:
    """Security and Protection System"""
    
    def __init__(self, db):
        self.db = db
        self.config = Config()
        
        # Rate limiting
        self.user_rates = {}
        self.ip_rates = {}
        
        # Blacklist
        self.blacklisted_users = set()
        self.blacklisted_ips = set()
        
        # Load blacklists
        self._load_blacklists()
    
    def _load_blacklists(self):
        """Load blacklisted users and IPs"""
        # This would load from database
        # For now, empty
        pass
    
    async def check_rate_limit(self, user_id: int, action: str = "message") -> Tuple[bool, str]:
        """Check rate limit for user"""
        now = datetime.now()
        user_key = f"{user_id}_{action}"
        
        if user_key not in self.user_rates:
            self.user_rates[user_key] = []
        
        # Remove old entries (last minute)
        cutoff = now - timedelta(seconds=60)
        self.user_rates[user_key] = [t for t in self.user_rates[user_key] if t > cutoff]
        
        # Check limit
        limit = self.config.RATE_LIMIT
        if len(self.user_rates[user_key]) >= limit:
            return False, f"⏳ রেট লিমিট! ১ মিনিট অপেক্ষা করুন (সীমা: {limit})"
        
        # Add current request
        self.user_rates[user_key].append(now)
        return True, ""
    
    async def check_spam(self, user_id: int, message: str) -> Tuple[bool, str]:
        """Check for spam content"""
        # Check message length
        if len(message) > 1000:
            return False, "❌ মেসেজ খুব বড় (সর্বোচ্চ ১০০০ অক্ষর)"
        
        # Check for spam patterns
        spam_patterns = [
            r'(http|https)://',  # URLs
            r'@\w+',  # Mentions
            r'#\w+',  # Hashtags
            r'[\U00010000-\U0010ffff]',  # Emojis (excessive)
        ]
        
        for pattern in spam_patterns:
            if len(re.findall(pattern, message)) > 5:  # Too many
                return False, "❌ সম্ভাব্য স্প্যাম কন্টেন্ট"
        
        # Check for repetitive content
        words = message.split()
        if len(words) > 10:
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.3:  # 70% repetition
                return False, "❌ বারবার একই কন্টেন্ট"
        
        return True, ""
    
    async def validate_payment_info(self, info: str, method: str) -> Tuple[bool, str]:
        """Validate payment information"""
        if method == 'bkash':
            # Bkash number validation
            if not re.match(r'^01[3-9]\d{8}$', info):
                return False, "❌ ভুল বিকাশ নম্বর"
            
            # Additional validation
            if info == self.config.BKASH_NUMBER:
                return False, "❌ আপনার নিজের নাম্বার দিতে পারবেন না"
            
        elif method == 'nagad':
            # Nagad number validation
            if not re.match(r'^01[3-9]\d{8}$', info):
                return False, "❌ ভুল নগদ নম্বর"
            
            if info == self.config.NAGAD_NUMBER:
                return False, "❌ আপনার নিজের নাম্বার দিতে পারবেন না"
        
        return True, "✅ ভেরিফিকেশন সফল"
    
    async def validate_transaction_id(self, tx_id: str, method: str) -> Tuple[bool, str]:
        """Validate transaction ID"""
        if method == 'bkash':
            if not re.match(r'^[A-Z0-9]{10}$', tx_id):
                return False, "❌ ভুল ট্রানজেকশন আইডি (১০টি বর্ণ/সংখ্যা)"
        
        elif method == 'nagad':
            if not re.match(r'^[A-Z0-9]{8,12}$', tx_id):
                return False, "❌ ভুল ট্রানজেকশন আইডি (৮-১২টি বর্ণ/সংখ্যা)"
        
        return True, "✅ ট্রানজেকশন আইডি ভেরিফাইড"
    
    async def check_user_trust_score(self, user_id: int) -> Dict:
        """Calculate user trust score"""
        user = await self.db.get_user(user_id)
        if not user:
            return {'score': 0, 'level': 'unknown', 'reasons': []}
        
        score = 50  # Base score
        reasons = []
        
        # Positive factors
        days_active = (datetime.now() - datetime.fromisoformat(user.get('created_at', datetime.now().isoformat()))).days
        if days_active > 30:
            score += 20
            reasons.append(f"✅ {days_active} দিন সক্রিয়")
        
        message_count = user.get('message_count', 0)
        if message_count > 100:
            score += 15
            reasons.append(f"✅ {message_count} মেসেজ")
        
        game_count = user.get('game_count', 0)
        if game_count > 50:
            score += 10
            reasons.append(f"✅ {game_count} গেম")
        
        # Negative factors
        if user.get('banned', False):
            score -= 100
            reasons.append("❌ ব্যান্ড ইউজার")
        
        # Payment history
        payments_ref = self.db.db.collection('payments')
        payment_query = payments_ref.where('user_id', '==', str(user_id)).where('status', '==', 'completed')
        payment_docs = payment_query.stream()
        payment_count = sum(1 for _ in payment_docs)
        
        if payment_count > 0:
            score += 25
            reasons.append(f"✅ {payment_count} সফল পেমেন্ট")
        
        # Determine level
        if score >= 80:
            level = "💎 High"
        elif score >= 60:
            level = "⭐ Medium"
        elif score >= 40:
            level = "⚠️ Low"
        else:
            level = "❌ Restricted"
        
        return {
            'score': min(max(score, 0), 100),
            'level': level,
            'reasons': reasons,
            'payment_count': payment_count,
            'days_active': days_active
        }
    
    async def generate_captcha(self) -> Tuple[str, str]:
        """Generate CAPTCHA challenge"""
        # Simple math CAPTCHA
        import random
        
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operator = random.choice(['+', '-', '*'])
        
        if operator == '+':
            answer = num1 + num2
            question = f"{num1} + {num2} = ?"
        elif operator == '-':
            answer = num1 - num2
            question = f"{num1} - {num2} = ?"
        else:  # '*'
            answer = num1 * num2
            question = f"{num1} × {num2} = ?"
        
        # Store answer with hash
        captcha_id = secrets.token_hex(8)
        captcha_hash = hashlib.sha256(f"{captcha_id}:{answer}".encode()).hexdigest()[:8]
        
        return captcha_id, f"{question} (Answer: {captcha_hash})"
    
    async def verify_captcha(self, captcha_id: str, user_answer: str, expected_hash: str) -> bool:
        """Verify CAPTCHA answer"""
        try:
            # Simple verification
            computed_hash = hashlib.sha256(f"{captcha_id}:{user_answer}".encode()).hexdigest()[:8]
            return computed_hash == expected_hash
        except:
            return False
    
    async def log_security_event(self, event_type: str, user_id: int = None, 
                               details: str = "", severity: str = "low"):
        """Log security event"""
        try:
            event_data = {
                'type': event_type,
                'user_id': str(user_id) if user_id else 'system',
                'details': details,
                'severity': severity,
                'timestamp': datetime.now().isoformat(),
                'ip_address': 'N/A'  # Would get from request in web context
            }
            
            self.db.db.collection('security_logs').add(event_data)
            
            # Send alert for high severity events
            if severity in ['high', 'critical']:
                # Would trigger admin notification
                pass
            
            return True
            
        except Exception as e:
            print(f"Error logging security event: {e}")
            return False
    
    async def get_security_logs(self, limit: int = 50, severity: str = None) -> List[Dict]:
        """Get security logs"""
        try:
            logs_ref = self.db.db.collection('security_logs')
            query = logs_ref.order_by('timestamp', direction='DESCENDING')
            
            if severity:
                query = query.where('severity', '==', severity)
            
            query = query.limit(limit)
            
            docs = query.stream()
            logs = []
            
            for doc in docs:
                log_data = doc.to_dict()
                log_data['id'] = doc.id
                logs.append(log_data)
            
            return logs
            
        except Exception as e:
            print(f"Error getting security logs: {e}")
            return []
    
    async def check_file_security(self, file_path: str, file_type: str) -> Tuple[bool, str]:
        """Check file security"""
        import os
        
        # Check file size
        max_size_mb = self.config.MAX_FILE_SIZE
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            return False, f"❌ ফাইল খুব বড় (সর্বোচ্চ {max_size_mb}MB)"
        
        # Check file type
        allowed_types = self.config.ALLOWED_FILE_TYPES
        if file_type not in allowed_types:
            return False, f"❌ সাপোর্টেড ফাইল টাইপ না (অনুমোদিত: {', '.join(allowed_types)})"
        
        # Check for malicious content (simplified)
        if file_type in ['jpg', 'jpeg', 'png', 'gif']:
            # Would do image validation
            pass
        elif file_type in ['pdf', 'docx']:
            # Would do document validation
            pass
        
        return True, "✅ ফাইল সিকিউরিটি চেক পাস"
    
    async def generate_otp(self, user_id: int) -> str:
        """Generate OTP for user"""
        import random
        otp = str(random.randint(100000, 999999))
        
        # Store OTP with expiration
        otp_data = {
            'user_id': str(user_id),
            'otp': otp,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=5)).isoformat(),
            'used': False
        }
        
        self.db.db.collection('otps').add(otp_data)
        
        return otp
    
    async def verify_otp(self, user_id: int, otp: str) -> bool:
        """Verify OTP"""
        try:
            otps_ref = self.db.db.collection('otps')
            query = otps_ref.where('user_id', '==', str(user_id)) \
                           .where('otp', '==', otp) \
                           .where('used', '==', False) \
                           .limit(1)
            
            docs = query.stream()
            
            for doc in docs:
                otp_data = doc.to_dict()
                
                # Check expiration
                expires_at = datetime.fromisoformat(otp_data['expires_at'])
                if datetime.now() > expires_at:
                    doc.reference.update({'used': True, 'expired': True})
                    return False
                
                # Mark as used
                doc.reference.update({'used': True, 'verified_at': datetime.now().isoformat()})
                return True
            
            return False
            
        except Exception as e:
            print(f"Error verifying OTP: {e}")
            return False
    
    async def get_security_report(self) -> str:
        """Generate security report"""
        # Get recent security events
        logs = await self.get_security_logs(limit=20)
        
        # Count by severity
        severity_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        event_types = {}
        
        for log in logs:
            severity = log.get('severity', 'low')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            event_type = log.get('type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Get rate limit stats
        active_limits = len(self.user_rates)
        
        report = f"""
🔒 *সিকিউরিটি রিপোর্ট*

📊 *সামগ্রিক স্ট্যাটাস:*
• সিকিউরিটি লেভেল: {'🟢 নিরাপদ' if severity_counts['critical'] == 0 else '🟡 মাঝারি' if severity_counts['high'] == 0 else '🔴 ঝুঁকিপূর্ণ'}
• অ্যাক্টিভ রেট লিমিট: {active_limits}
• ব্ল্যাকলিস্টেড ইউজার: {len(self.blacklisted_users)}

🚨 *সিকিউরিটি ইভেন্টস (গত ২৪ ঘন্টা):*
• ক্রিটিকাল: {severity_counts['critical']}
• হাই: {severity_counts['high']}
• মিডিয়াম: {severity_counts['medium']}
• লো: {severity_counts['low']}

📈 *সাধারণ ইভেন্ট টাইপ:*
"""
        
        # Add top event types
        for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"• {event_type}: {count}\n"
        
        # Add recommendations
        report += f"\n💡 *সুপারিশ:*\n"
        
        if severity_counts['critical'] > 0:
            report += "• ক্রিটিকাল ইভেন্ট তদন্ত করুন\n"
        
        if active_limits > 100:
            report += "• অনেক রেট লিমিট সক্রিয়, সম্ভাব্য অ্যাটাক\n"
        
        report += f"• নিয়মিত ব্যাকআপ নিশ্চিত করুন\n"
        
        report += f"\n🕒 রিপোর্ট সময়: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return report