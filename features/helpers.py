import re
import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import hashlib
import json

class Helpers:
    """Utility helper functions"""
    
    @staticmethod
    def format_number(number: Union[int, float]) -> str:
        """Format number with commas"""
        return f"{number:,}"
    
    @staticmethod
    def format_points(points: int) -> str:
        """Format points with emoji based on amount"""
        if points >= 10000:
            return f"🏆 {points:,}"
        elif points >= 5000:
            return f"💎 {points:,}"
        elif points >= 1000:
            return f"⭐ {points:,}"
        elif points >= 100:
            return f"✨ {points:,}"
        else:
            return f"🪙 {points:,}"
    
    @staticmethod
    def format_time_ago(timestamp: str) -> str:
        """Format time ago in Bangla"""
        try:
            past_time = datetime.fromisoformat(timestamp)
            now = datetime.now()
            diff = now - past_time
            
            if diff.days > 365:
                years = diff.days // 365
                return f"{years} বছর আগে"
            elif diff.days > 30:
                months = diff.days // 30
                return f"{months} মাস আগে"
            elif diff.days > 0:
                return f"{diff.days} দিন আগে"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} ঘণ্টা আগে"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} মিনিট আগে"
            else:
                return "এইমাত্র"
        except:
            return "অজানা সময়"
    
    @staticmethod
    def generate_random_string(length: int = 8) -> str:
        """Generate random string"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_transaction_id(prefix: str = "TXN") -> str:
        """Generate transaction ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{timestamp}{random_part}"
    
    @staticmethod
    def calculate_percentage(part: int, total: int) -> float:
        """Calculate percentage"""
        if total == 0:
            return 0.0
        return round((part / total) * 100, 2)
    
    @staticmethod
    def create_progress_bar(progress: int, total: int = 100, length: int = 10) -> str:
        """Create progress bar"""
        filled = int((progress / total) * length)
        empty = length - filled
        
        bar = "█" * filled + "░" * empty
        percentage = (progress / total) * 100
        
        return f"{bar} {percentage:.1f}%"
    
    @staticmethod
    def is_bangla(text: str) -> bool:
        """Check if text contains Bangla characters"""
        bangla_range = r'[\u0980-\u09FF]'
        return bool(re.search(bangla_range, text))
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Extract hashtags from text"""
        return re.findall(r'#\w+', text)
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """Extract mentions from text"""
        return re.findall(r'@\w+', text)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone_bd(phone: str) -> bool:
        """Validate Bangladeshi phone number"""
        pattern = r'^01[3-9]\d{8}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def format_phone_bd(phone: str) -> str:
        """Format Bangladeshi phone number"""
        if phone.startswith('+880'):
            phone = phone[4:]
        elif phone.startswith('880'):
            phone = phone[3:]
        
        if len(phone) == 10 and phone.startswith('1'):
            phone = '0' + phone
        
        return phone
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        salt = "MARPD_SALT_2024"  # In production, use unique salt per user
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    @staticmethod
    def generate_referral_code(user_id: int) -> str:
        """Generate referral code from user ID"""
        hash_obj = hashlib.md5(f"MARPD{user_id}".encode())
        return hash_obj.hexdigest()[:6].upper()
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to max length"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def safe_json_parse(json_str: str, default: Any = None) -> Any:
        """Safely parse JSON string"""
        try:
            return json.loads(json_str)
        except:
            return default
    
    @staticmethod
    def dict_to_query_string(params: Dict) -> str:
        """Convert dictionary to query string"""
        return '&'.join([f"{k}={v}" for k, v in params.items()])
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension"""
        return filename.split('.')[-1].lower() if '.' in filename else ''
    
    @staticmethod
    def format_file_size(bytes_size: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"
    
    @staticmethod
    def calculate_age(birth_date: str) -> int:
        """Calculate age from birth date"""
        try:
            birth = datetime.fromisoformat(birth_date)
            today = datetime.now()
            
            age = today.year - birth.year
            
            # Adjust if birthday hasn't occurred this year
            if (today.month, today.day) < (birth.month, birth.day):
                age -= 1
            
            return age
        except:
            return 0
    
    @staticmethod
    def days_until(date_str: str) -> int:
        """Calculate days until a date"""
        try:
            target_date = datetime.fromisoformat(date_str)
            today = datetime.now()
            
            delta = target_date - today
            return max(0, delta.days)
        except:
            return 0
    
    @staticmethod
    def generate_qr_code_data(data: str) -> Dict:
        """Generate QR code data (placeholder)"""
        # In production, use qrcode library
        return {
            'data': data,
            'type': 'text',
            'size': 'medium'
        }
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in km"""
        from math import radians, sin, cos, sqrt, atan2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # Earth radius in kilometers
        radius = 6371
        
        return round(radius * c, 2)