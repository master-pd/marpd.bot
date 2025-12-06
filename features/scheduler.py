import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List
import threading

class TaskScheduler:
    """Background Task Scheduler"""
    
    def __init__(self):
        self.config = Config()
        self.running = False
        self.tasks = {}
        self.thread = None
        
    async def start(self):
        """Start scheduler"""
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        print("⏰ Task scheduler started")
        
        # Schedule initial tasks
        self._schedule_tasks()
    
    async def stop(self):
        """Stop scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        print("⏰ Task scheduler stopped")
    
    def _run_scheduler(self):
        """Run scheduler in background thread"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def _schedule_tasks(self):
        """Schedule all periodic tasks"""
        
        # Daily reset (12:00 AM)
        schedule.every().day.at("00:00").do(self._run_daily_reset)
        
        # Hourly tasks
        schedule.every().hour.do(self._run_hourly_tasks)
        
        # Every 30 minutes
        schedule.every(30).minutes.do(self._run_30min_tasks)
        
        # Every 10 minutes
        schedule.every(10).minutes.do(self._run_10min_tasks)
        
        # Every 5 minutes
        schedule.every(5).minutes.do(self._run_5min_tasks)
        
        # Every minute
        schedule.every().minute.do(self._run_minute_tasks)
        
        print(f"📅 Scheduled {len(schedule.jobs)} tasks")
    
    def _run_daily_reset(self):
        """Run daily reset tasks"""
        print("🔄 Running daily reset...")
        
        try:
            # This would call async functions
            # For now, just log
            print("✅ Daily reset completed")
        except Exception as e:
            print(f"❌ Daily reset failed: {e}")
    
    def _run_hourly_tasks(self):
        """Run hourly tasks"""
        print("⏰ Running hourly tasks...")
        
        try:
            # Example: Backup, cleanup, etc.
            print("✅ Hourly tasks completed")
        except Exception as e:
            print(f"❌ Hourly tasks failed: {e}")
    
    def _run_30min_tasks(self):
        """Run 30-minute tasks"""
        # print("🕒 Running 30-minute tasks...")
        pass
    
    def _run_10min_tasks(self):
        """Run 10-minute tasks"""
        # print("🔟 Running 10-minute tasks...")
        pass
    
    def _run_5min_tasks(self):
        """Run 5-minute tasks"""
        # print("5️⃣ Running 5-minute tasks...")
        pass
    
    def _run_minute_tasks(self):
        """Run minute tasks"""
        # print("1️⃣ Running minute tasks...")
        pass
    
    def schedule_task(self, task_id: str, func, interval: int, unit: str = 'minutes'):
        """Schedule a custom task"""
        if unit == 'seconds':
            schedule.every(interval).seconds.do(func)
        elif unit == 'minutes':
            schedule.every(interval).minutes.do(func)
        elif unit == 'hours':
            schedule.every(interval).hours.do(func)
        elif unit == 'days':
            schedule.every(interval).days.do(func)
        else:
            raise ValueError(f"Invalid unit: {unit}")
        
        self.tasks[task_id] = {
            'func': func,
            'interval': interval,
            'unit': unit,
            'last_run': None
        }
        
        print(f"📅 Scheduled custom task: {task_id} ({interval} {unit})")
    
    def cancel_task(self, task_id: str):
        """Cancel a scheduled task"""
        if task_id in self.tasks:
            # Note: schedule doesn't have direct cancel by ID
            # We need to clear all and reschedule
            schedule.clear()
            del self.tasks[task_id]
            self._schedule_tasks()  # Reschedule remaining tasks
            print(f"❌ Cancelled task: {task_id}")
            return True
        return False
    
    def get_scheduled_tasks(self) -> Dict:
        """Get list of scheduled tasks"""
        task_list = []
        
        for job in schedule.jobs:
            task_list.append({
                'job': str(job),
                'next_run': job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else 'N/A',
                'interval': str(job.interval),
                'unit': job.unit
            })
        
        return {
            'total_tasks': len(schedule.jobs),
            'tasks': task_list,
            'custom_tasks': len(self.tasks)
        }