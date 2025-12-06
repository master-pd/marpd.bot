import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import io

class AnalyticsSystem:
    """Analytics and Statistics System"""
    
    def __init__(self, db):
        self.db = db
        self.config = Config()
        
    async def get_daily_stats(self, date: datetime = None) -> Dict:
        """Get daily statistics"""
        if not date:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        
        try:
            # Get transactions for the day
            tx_ref = self.db.db.collection('transactions')
            tx_query = tx_ref.where('date', '==', date_str)
            tx_docs = tx_query.stream()
            
            daily_transactions = []
            total_credits = 0
            total_debits = 0
            
            for doc in tx_docs:
                tx_data = doc.to_dict()
                daily_transactions.append(tx_data)
                
                if tx_data['type'] == 'credit':
                    total_credits += tx_data['amount']
                else:
                    total_debits += tx_data['amount']
            
            # Get messages for the day
            msg_ref = self.db.db.collection('messages')
            # Need timestamp-based query
            # Simplified for now
            
            # Get games for the day
            games_ref = self.db.db.collection('games')
            games_query = games_ref.where('date', '==', date_str)
            games_docs = games_query.stream()
            daily_games = sum(1 for _ in games_docs)
            
            # Get new users for the day
            users_ref = self.db.db.collection('users')
            # Need to filter by created_at
            # Simplified for now
            
            return {
                'date': date_str,
                'total_transactions': len(daily_transactions),
                'total_credits': total_credits,
                'total_debits': total_debits,
                'net_change': total_credits - total_debits,
                'total_games': daily_games,
                'new_users': 0,  # Placeholder
                'active_users': 0   # Placeholder
            }
            
        except Exception as e:
            print(f"Error getting daily stats: {e}")
            return {
                'date': date_str,
                'total_transactions': 0,
                'total_credits': 0,
                'total_debits': 0,
                'net_change': 0,
                'total_games': 0,
                'new_users': 0,
                'active_users': 0
            }
    
    async def get_weekly_stats(self) -> Dict:
        """Get weekly statistics"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        stats_by_day = {}
        current_date = start_date
        
        while current_date <= end_date:
            day_stats = await self.get_daily_stats(current_date)
            stats_by_day[current_date.strftime('%Y-%m-%d')] = day_stats
            current_date += timedelta(days=1)
        
        # Calculate totals
        totals = {
            'total_transactions': sum(day['total_transactions'] for day in stats_by_day.values()),
            'total_credits': sum(day['total_credits'] for day in stats_by_day.values()),
            'total_debits': sum(day['total_debits'] for day in stats_by_day.values()),
            'total_games': sum(day['total_games'] for day in stats_by_day.values()),
            'total_new_users': sum(day['new_users'] for day in stats_by_day.values())
        }
        
        return {
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'days': stats_by_day,
            'totals': totals,
            'average_daily': {
                'transactions': totals['total_transactions'] / 7,
                'credits': totals['total_credits'] / 7,
                'debits': totals['total_debits'] / 7,
                'games': totals['total_games'] / 7
            }
        }
    
    async def get_monthly_stats(self) -> Dict:
        """Get monthly statistics"""
        end_date = datetime.now()
        start_date = end_date.replace(day=1)  # First day of current month
        
        stats_by_day = {}
        current_date = start_date
        
        while current_date <= end_date:
            day_stats = await self.get_daily_stats(current_date)
            stats_by_day[current_date.strftime('%Y-%m-%d')] = day_stats
            current_date += timedelta(days=1)
        
        # Calculate totals
        totals = {
            'total_transactions': sum(day['total_transactions'] for day in stats_by_day.values()),
            'total_credits': sum(day['total_credits'] for day in stats_by_day.values()),
            'total_debits': sum(day['total_debits'] for day in stats_by_day.values()),
            'total_games': sum(day['total_games'] for day in stats_by_day.values()),
            'total_new_users': sum(day['new_users'] for day in stats_by_day.values())
        }
        
        days_in_month = len(stats_by_day)
        
        return {
            'month': start_date.strftime('%Y-%m'),
            'days': stats_by_day,
            'totals': totals,
            'average_daily': {
                'transactions': totals['total_transactions'] / days_in_month if days_in_month > 0 else 0,
                'credits': totals['total_credits'] / days_in_month if days_in_month > 0 else 0,
                'debits': totals['total_debits'] / days_in_month if days_in_month > 0 else 0,
                'games': totals['total_games'] / days_in_month if days_in_month > 0 else 0
            }
        }
    
    async def get_user_growth_data(self, days: int = 30) -> Dict:
        """Get user growth data"""
        try:
            users_ref = self.db.db.collection('users')
            users_docs = users_ref.limit(1000).stream()
            
            # Group by join date
            growth_data = {}
            
            for doc in users_docs:
                user_data = doc.to_dict()
                join_date = user_data.get('created_at', '')
                
                if join_date:
                    date_part = join_date[:10]  # YYYY-MM-DD
                    growth_data[date_part] = growth_data.get(date_part, 0) + 1
            
            # Sort by date
            sorted_dates = sorted(growth_data.items())
            
            # Calculate cumulative growth
            cumulative = 0
            cumulative_growth = []
            
            for date, count in sorted_dates:
                cumulative += count
                cumulative_growth.append({
                    'date': date,
                    'daily_new': count,
                    'total_users': cumulative
                })
            
            # Get last N days
            recent_data = cumulative_growth[-days:] if len(cumulative_growth) > days else cumulative_growth
            
            return {
                'total_users': cumulative,
                'growth_data': recent_data,
                'average_daily_growth': cumulative / len(cumulative_growth) if cumulative_growth else 0
            }
            
        except Exception as e:
            print(f"Error getting user growth data: {e}")
            return {'total_users': 0, 'growth_data': [], 'average_daily_growth': 0}
    
    async def get_revenue_stats(self) -> Dict:
        """Get revenue statistics"""
        try:
            payments_ref = self.db.db.collection('payments')
            payments_docs = payments_ref.where('status', '==', 'completed').stream()
            
            total_revenue = 0
            revenue_by_method = {}
            revenue_by_day = {}
            
            for doc in payments_docs:
                payment_data = doc.to_dict()
                amount = payment_data['amount']
                method = payment_data['method']
                date = payment_data.get('completed_at', '')[:10]
                
                total_revenue += amount
                
                # By method
                revenue_by_method[method] = revenue_by_method.get(method, 0) + amount
                
                # By day
                if date:
                    revenue_by_day[date] = revenue_by_day.get(date, 0) + amount
            
            # Get withdrawal stats
            withdrawals_ref = self.db.db.collection('withdrawals')
            withdrawals_docs = withdrawals_ref.where('status', '==', 'completed').stream()
            
            total_withdrawn = 0
            
            for doc in withdrawals_docs:
                withdrawal_data = doc.to_dict()
                total_withdrawn += withdrawal_data['amount_taka']
            
            net_revenue = total_revenue - total_withdrawn
            
            return {
                'total_revenue': total_revenue,
                'total_withdrawn': total_withdrawn,
                'net_revenue': net_revenue,
                'revenue_by_method': revenue_by_method,
                'revenue_by_day': revenue_by_day
            }
            
        except Exception as e:
            print(f"Error getting revenue stats: {e}")
            return {
                'total_revenue': 0,
                'total_withdrawn': 0,
                'net_revenue': 0,
                'revenue_by_method': {},
                'revenue_by_day': {}
            }
    
    async def get_game_popularity_stats(self) -> Dict:
        """Get game popularity statistics"""
        try:
            games_ref = self.db.db.collection('games')
            games_docs = games_ref.limit(1000).stream()
            
            games_by_type = {}
            wins_by_type = {}
            
            for doc in games_docs:
                game_data = doc.to_dict()
                game_type = game_data['game_type']
                result = game_data['result']
                
                # Count games by type
                games_by_type[game_type] = games_by_type.get(game_type, 0) + 1
                
                # Count wins by type
                if result == 'win':
                    wins_by_type[game_type] = wins_by_type.get(game_type, 0) + 1
            
            # Calculate win rates
            win_rates = {}
            for game_type, total in games_by_type.items():
                wins = wins_by_type.get(game_type, 0)
                win_rate = (wins / total * 100) if total > 0 else 0
                win_rates[game_type] = round(win_rate, 2)
            
            # Find most popular game
            if games_by_type:
                most_popular = max(games_by_type.items(), key=lambda x: x[1])
            else:
                most_popular = ('None', 0)
            
            return {
                'total_games_played': sum(games_by_type.values()),
                'games_by_type': games_by_type,
                'win_rates': win_rates,
                'most_popular_game': most_popular[0],
                'most_popular_count': most_popular[1]
            }
            
        except Exception as e:
            print(f"Error getting game stats: {e}")
            return {
                'total_games_played': 0,
                'games_by_type': {},
                'win_rates': {},
                'most_popular_game': 'None',
                'most_popular_count': 0
            }
    
    async def generate_analytics_report(self, period: str = "weekly") -> str:
        """Generate analytics report"""
        if period == "daily":
            stats = await self.get_daily_stats()
            period_str = "Daily"
        elif period == "weekly":
            stats = await self.get_weekly_stats()
            period_str = "Weekly"
        else:  # monthly
            stats = await self.get_monthly_stats()
            period_str = "Monthly"
        
        # Get additional stats
        user_growth = await self.get_user_growth_data(days=7 if period == "weekly" else 30)
        revenue_stats = await self.get_revenue_stats()
        game_stats = await self.get_game_popularity_stats()
        
        report = f"""
📊 *{period_str} Analytics Report*

📅 *Period:* {stats.get('period', stats.get('date', 'N/A'))}

👥 *User Statistics:*
• Total Users: {user_growth['total_users']:,}
• Daily Growth: {user_growth['average_daily_growth']:.1f}
• Active Users: {stats.get('active_users', 'N/A')}

💰 *Economic Statistics:*
• Total Revenue: ৳{revenue_stats['total_revenue']:.2f}
• Total Withdrawn: ৳{revenue_stats['total_withdrawn']:.2f}
• Net Revenue: ৳{revenue_stats['net_revenue']:.2f}
• Total Credits: {stats.get('total_credits', 0):,} points
• Total Debits: {stats.get('total_debits', 0):,} points
• Net Change: {stats.get('net_change', 0):,} points

🎮 *Gaming Statistics:*
• Total Games: {game_stats['total_games_played']:,}
• Most Popular: {game_stats['most_popular_game']} ({game_stats['most_popular_count']} games)
• Avg Win Rate: {sum(game_stats['win_rates'].values())/len(game_stats['win_rates']) if game_stats['win_rates'] else 0:.1f}%

📈 *Activity Summary:*
• Transactions: {stats.get('total_transactions', 0):,}
• Games Played: {stats.get('total_games', 0):,}
• New Users: {stats.get('new_users', 0):,}

🕒 *Report Generated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return report
    
    async def create_chart(self, chart_type: str, data: Dict) -> Optional[bytes]:
        """Create chart image"""
        try:
            plt.figure(figsize=(10, 6))
            
            if chart_type == "user_growth":
                dates = [item['date'] for item in data['growth_data']]
                totals = [item['total_users'] for item in data['growth_data']]
                
                plt.plot(dates, totals, marker='o', linewidth=2, markersize=8)
                plt.title('User Growth Over Time', fontsize=16, fontweight='bold')
                plt.xlabel('Date', fontsize=12)
                plt.ylabel('Total Users', fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                
            elif chart_type == "revenue":
                dates = list(data['revenue_by_day'].keys())[-30:]  # Last 30 days
                revenues = [data['revenue_by_day'][date] for date in dates]
                
                plt.bar(dates, revenues, color='green', alpha=0.7)
                plt.title('Daily Revenue', fontsize=16, fontweight='bold')
                plt.xlabel('Date', fontsize=12)
                plt.ylabel('Revenue (৳)', fontsize=12)
                plt.grid(True, alpha=0.3, axis='y')
                plt.xticks(rotation=45)
                plt.tight_layout()
                
            elif chart_type == "game_popularity":
                games = list(data['games_by_type'].keys())[:10]  # Top 10 games
                counts = [data['games_by_type'][game] for game in games]
                
                plt.barh(games, counts, color='blue', alpha=0.7)
                plt.title('Game Popularity', fontsize=16, fontweight='bold')
                plt.xlabel('Number of Games Played', fontsize=12)
                plt.tight_layout()
            
            # Save to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            plt.close()
            buf.seek(0)
            
            return buf.getvalue()
            
        except Exception as e:
            print(f"Error creating chart: {e}")
            return None