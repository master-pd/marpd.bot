import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ShopSystem:
    """Virtual Shop System"""
    
    def __init__(self, db):
        self.db = db
        self.config = Config()
        
        # Shop items
        self.items = {}
        self.user_items = {}
        
        # Load shop items
        self._load_shop_items()
    
    def _load_shop_items(self):
        """Load shop items"""
        self.items = {
            # VIP Packages
            'vip_1day': {
                'id': 'vip_1day',
                'name': '⭐ VIP 1 দিন',
                'description': 'VIP স্ট্যাটাস ১ দিনের জন্য',
                'price': 100,
                'type': 'vip',
                'duration': 1,  # days
                'icon': '⭐',
                'features': ['2x পয়েন্ট', 'বিশেষ ব্যাজ', 'প্রাইভেট চ্যাট']
            },
            'vip_7days': {
                'id': 'vip_7days',
                'name': '💎 VIP 7 দিন',
                'description': 'VIP স্ট্যাটাস ৭ দিনের জন্য',
                'price': 500,
                'type': 'vip',
                'duration': 7,
                'icon': '💎',
                'features': ['2x পয়েন্ট', 'বিশেষ ব্যাজ', 'প্রাইভেট চ্যাট', 'প্রাইওরিটি সাপোর্ট']
            },
            'vip_30days': {
                'id': 'vip_30days',
                'name': '👑 VIP 30 দিন',
                'description': 'VIP স্ট্যাটাস ৩০ দিনের জন্য',
                'price': 1500,
                'type': 'vip',
                'duration': 30,
                'icon': '👑',
                'features': ['3x পয়েন্ট', 'গোল্ড ব্যাজ', 'প্রাইভেট চ্যাট', 'প্রাইওরিটি সাপোর্ট', 'বিশেষ গেম অ্যাক্সেস']
            },
            
            # Boosts
            'boost_2x_1h': {
                'id': 'boost_2x_1h',
                'name': '⚡ 2x বুস্ট 1 ঘণ্টা',
                'description': '১ ঘণ্টার জন্য ২x পয়েন্ট বুস্ট',
                'price': 50,
                'type': 'boost',
                'duration': 1,  # hours
                'multiplier': 2.0,
                'icon': '⚡'
            },
            'boost_2x_24h': {
                'id': 'boost_2x_24h',
                'name': '⚡ 2x বুস্ট 24 ঘণ্টা',
                'description': '২৪ ঘণ্টার জন্য ২x পয়েন্ট বুস্ট',
                'price': 300,
                'type': 'boost',
                'duration': 24,
                'multiplier': 2.0,
                'icon': '⚡⚡'
            },
            
            # Cosmetics
            'badge_gold': {
                'id': 'badge_gold',
                'name': '🥇 গোল্ড ব্যাজ',
                'description': 'বিশেষ গোল্ড ব্যাজ আপনার প্রোফাইলে',
                'price': 200,
                'type': 'cosmetic',
                'icon': '🥇',
                'permanent': True
            },
            'badge_diamond': {
                'id': 'badge_diamond',
                'name': '💎 ডায়মন্ড ব্যাজ',
                'description': 'এক্সক্লুসিভ ডায়মন্ড ব্যাজ',
                'price': 500,
                'type': 'cosmetic',
                'icon': '💎',
                'permanent': True
            },
            
            # Game Items
            'game_hint': {
                'id': 'game_hint',
                'name': '💡 গেম হিন্ট',
                'description': 'গেমে হিন্ট পাওয়ার জন্য',
                'price': 20,
                'type': 'game_item',
                'consumable': True,
                'icon': '💡'
            },
            'game_extra_chance': {
                'id': 'game_extra_chance',
                'name': '🔄 এক্সট্রা চান্স',
                'description': 'গেমে এক্সট্রা চান্স',
                'price': 30,
                'type': 'game_item',
                'consumable': True,
                'icon': '🔄'
            },
            
            # Special
            'name_color': {
                'id': 'name_color',
                'name': '🎨 রঙিন নাম',
                'description': 'আপনার নাম রঙিন দেখাবে',
                'price': 150,
                'type': 'cosmetic',
                'icon': '🎨',
                'permanent': True
            },
            'custom_title': {
                'id': 'custom_title',
                'name': '📛 কাস্টম টাইটেল',
                'description': 'বিশেষ কাস্টম টাইটেল',
                'price': 250,
                'type': 'cosmetic',
                'icon': '📛',
                'permanent': True
            }
        }
        
        print(f"🛒 লোডেড {len(self.items)} শপ আইটেম")
    
    async def get_shop_items(self, category: str = None) -> List[Dict]:
        """Get shop items, optionally filtered by category"""
        if category:
            return [item for item in self.items.values() if item['type'] == category]
        return list(self.items.values())
    
    async def get_item(self, item_id: str) -> Optional[Dict]:
        """Get item by ID"""
        return self.items.get(item_id)
    
    async def can_afford(self, user_id: int, item_id: str) -> Tuple[bool, str, int]:
        """Check if user can afford item"""
        item = await self.get_item(item_id)
        if not item:
            return False, "❌ আইটেম পাওয়া যায়নি", 0
        
        user = await self.db.get_user(user_id)
        if not user:
            return False, "❌ ইউজার ডাটা পাওয়া যায়নি", 0
        
        user_points = user.get('points', 0)
        item_price = item['price']
        
        if user_points < item_price:
            return False, f"❌ {item_price} পয়েন্ট প্রয়োজন, আপনার আছে {user_points} পয়েন্ট", item_price
        
        return True, "", item_price
    
    async def purchase_item(self, user_id: int, item_id: str) -> Tuple[bool, str]:
        """Purchase item from shop"""
        # Check if user can afford
        can_afford, message, price = await self.can_afford(user_id, item_id)
        if not can_afford:
            return False, message
        
        item = await self.get_item(item_id)
        if not item:
            return False, "❌ আইটেম পাওয়া যায়নি"
        
        # Deduct points
        success = await self.db.deduct_points(user_id, price, f"shop_purchase:{item_id}")
        if not success:
            return False, "❌ পয়েন্ট কাটা যায়নি"
        
        # Add item to user inventory
        await self._add_to_inventory(user_id, item)
        
        # Log purchase
        await self._log_purchase(user_id, item_id, price)
        
        # Generate receipt
        receipt = self._generate_receipt(user_id, item, price)
        
        return True, receipt
    
    async def _add_to_inventory(self, user_id: int, item: Dict):
        """Add item to user inventory"""
        try:
            inventory_ref = self.db.db.collection('inventory').document(str(user_id))
            inventory_doc = inventory_ref.get()
            
            if inventory_doc.exists:
                inventory_data = inventory_doc.to_dict()
                items = inventory_data.get('items', [])
            else:
                items = []
            
            # Add new item
            item_data = {
                'item_id': item['id'],
                'name': item['name'],
                'type': item['type'],
                'purchased_at': datetime.now().isoformat(),
                'expires_at': None,
                'active': True
            }
            
            # Set expiration for timed items
            if item['type'] in ['vip', 'boost']:
                duration = item.get('duration', 1)
                if item['type'] == 'vip':
                    expires_at = datetime.now() + timedelta(days=duration)
                else:  # boost
                    expires_at = datetime.now() + timedelta(hours=duration)
                
                item_data['expires_at'] = expires_at.isoformat()
            
            items.append(item_data)
            
            # Update inventory
            inventory_ref.set({
                'user_id': str(user_id),
                'items': items,
                'updated_at': datetime.now().isoformat()
            }, merge=True)
            
        except Exception as e:
            print(f"Error adding to inventory: {e}")
    
    async def _log_purchase(self, user_id: int, item_id: str, price: int):
        """Log purchase transaction"""
        try:
            purchase_data = {
                'user_id': str(user_id),
                'item_id': item_id,
                'price': price,
                'purchased_at': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
            self.db.db.collection('purchases').add(purchase_data)
            
        except Exception as e:
            print(f"Error logging purchase: {e}")
    
    def _generate_receipt(self, user_id: int, item: Dict, price: int) -> str:
        """Generate purchase receipt"""
        receipt = f"""
🧾 *পারচেজ রসিদ*

🛒 আইটেম: {item['name']}
💰 মূল্য: {price} পয়েন্ট
📝 বিবরণ: {item['description']}
👤 ইউজার: {user_id}
📅 তারিখ: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}

"""
        
        # Add item-specific info
        if item['type'] == 'vip':
            receipt += f"⏳ সময়: {item['duration']} দিন\n"
            receipt += f"✨ ফিচার:\n"
            for feature in item.get('features', []):
                receipt += f"  • {feature}\n"
        
        elif item['type'] == 'boost':
            receipt += f"⏳ সময়: {item['duration']} ঘণ্টা\n"
            receipt += f"📈 মাল্টিপ্লায়ার: {item['multiplier']}x\n"
        
        receipt += f"\n✅ ক্রয় সফলভাবে সম্পন্ন হয়েছে!\n"
        
        if item.get('consumable'):
            receipt += f"📦 আইটেম আপনার ইনভেন্টরিতে যোগ করা হয়েছে\n"
        
        return receipt
    
    async def get_user_inventory(self, user_id: int) -> Dict:
        """Get user's inventory"""
        try:
            inventory_ref = self.db.db.collection('inventory').document(str(user_id))
            inventory_doc = inventory_ref.get()
            
            if inventory_doc.exists:
                inventory_data = inventory_doc.to_dict()
                
                # Filter out expired items
                items = inventory_data.get('items', [])
                active_items = []
                expired_items = []
                
                now = datetime.now()
                
                for item in items:
                    expires_at = item.get('expires_at')
                    if expires_at:
                        expires = datetime.fromisoformat(expires_at)
                        if expires < now:
                            expired_items.append(item)
                            continue
                    
                    active_items.append(item)
                
                # Update inventory if there are expired items
                if expired_items:
                    inventory_ref.update({
                        'items': active_items,
                        'updated_at': datetime.now().isoformat()
                    })
                
                return {
                    'active': active_items,
                    'expired': expired_items,
                    'total_items': len(active_items)
                }
            
            return {'active': [], 'expired': [], 'total_items': 0}
            
        except Exception as e:
            print(f"Error getting inventory: {e}")
            return {'active': [], 'expired': [], 'total_items': 0}
    
    async def get_active_boost(self, user_id: int) -> Optional[Dict]:
        """Get user's active boost"""
        inventory = await self.get_user_inventory(user_id)
        
        for item in inventory['active']:
            if item['type'] == 'boost' and item.get('active', True):
                # Check if not expired
                expires_at = item.get('expires_at')
                if expires_at:
                    expires = datetime.fromisoformat(expires_at)
                    if expires > datetime.now():
                        return item
        
        return None
    
    async def get_vip_status(self, user_id: int) -> Optional[Dict]:
        """Get user's VIP status"""
        inventory = await self.get_user_inventory(user_id)
        
        for item in inventory['active']:
            if item['type'] == 'vip' and item.get('active', True):
                # Check if not expired
                expires_at = item.get('expires_at')
                if expires_at:
                    expires = datetime.fromisoformat(expires_at)
                    if expires > datetime.now():
                        # Calculate remaining time
                        remaining = expires - datetime.now()
                        days = remaining.days
                        hours = remaining.seconds // 3600
                        
                        return {
                            'active': True,
                            'expires_at': expires_at,
                            'remaining_days': days,
                            'remaining_hours': hours,
                            'item_name': item['name']
                        }
        
        return {'active': False}
    
    async def use_consumable(self, user_id: int, item_id: str) -> Tuple[bool, str]:
        """Use consumable item"""
        inventory = await self.get_user_inventory(user_id)
        
        # Find item
        item_to_use = None
        item_index = -1
        
        for i, item in enumerate(inventory['active']):
            if item['item_id'] == item_id:
                item_to_use = item
                item_index = i
                break
        
        if not item_to_use:
            return False, "❌ আইটেম আপনার ইনভেন্টরিতে নেই"
        
        # Get item details
        item_details = await self.get_item(item_id)
        if not item_details:
            return False, "❌ আইটেম ডাটা পাওয়া যায়নি"
        
        if not item_details.get('consumable', False):
            return False, "❌ এই আইটেম ইউজ করা যায় না"
        
        # Remove from inventory
        try:
            inventory_ref = self.db.db.collection('inventory').document(str(user_id))
            inventory_doc = inventory_ref.get()
            
            if inventory_doc.exists:
                inventory_data = inventory_doc.to_dict()
                items = inventory_data.get('items', [])
                
                # Remove the used item
                if 0 <= item_index < len(items):
                    items.pop(item_index)
                    
                    # Update inventory
                    inventory_ref.update({
                        'items': items,
                        'updated_at': datetime.now().isoformat()
                    })
                    
                    # Log usage
                    usage_data = {
                        'user_id': str(user_id),
                        'item_id': item_id,
                        'used_at': datetime.now().isoformat()
                    }
                    
                    self.db.db.collection('item_usage').add(usage_data)
                    
                    return True, f"✅ {item_details['name']} সফলভাবে ইউজ করা হয়েছে!"
            
            return False, "❌ আইটেম ইউজ করা যায়নি"
            
        except Exception as e:
            return False, f"❌ ত্রুটি: {str(e)}"
    
    async def get_shop_stats(self) -> Dict:
        """Get shop statistics"""
        try:
            # Total purchases
            purchases_ref = self.db.db.collection('purchases')
            purchases_docs = purchases_ref.limit(1000).stream()
            
            total_purchases = 0
            total_revenue = 0
            popular_items = {}
            
            for doc in purchases_docs:
                purchase_data = doc.to_dict()
                total_purchases += 1
                total_revenue += purchase_data['price']
                
                item_id = purchase_data['item_id']
                popular_items[item_id] = popular_items.get(item_id, 0) + 1
            
            # Most popular items
            if popular_items:
                most_popular = max(popular_items.items(), key=lambda x: x[1])
                most_popular_item = await self.get_item(most_popular[0])
                most_popular_name = most_popular_item['name'] if most_popular_item else most_popular[0]
            else:
                most_popular_name = "N/A"
            
            return {
                'total_purchases': total_purchases,
                'total_revenue': total_revenue,
                'most_popular_item': most_popular_name,
                'total_items_available': len(self.items)
            }
            
        except Exception as e:
            print(f"Error getting shop stats: {e}")
            return {
                'total_purchases': 0,
                'total_revenue': 0,
                'most_popular_item': "N/A",
                'total_items_available': len(self.items)
            }