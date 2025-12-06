import asyncio
import os
import shutil
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class BackupManager:
    """Automated Backup System"""
    
    def __init__(self, db=None):
        self.db = db
        self.config = Config()
        self.running = False
        
        # Ensure backup directory exists
        if not os.path.exists(self.config.BACKUP_DIR):
            os.makedirs(self.config.BACKUP_DIR)
    
    async def start(self):
        """Start backup manager"""
        self.running = True
        
        if self.config.AUTO_BACKUP:
            print("💾 Backup manager started (auto-backup enabled)")
        else:
            print("💾 Backup manager started (auto-backup disabled)")
    
    async def stop(self):
        """Stop backup manager"""
        self.running = False
        print("💾 Backup manager stopped")
    
    async def create_backup(self, backup_type: str = "full") -> Dict:
        """Create backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{backup_type}_{timestamp}"
            backup_path = os.path.join(self.config.BACKUP_DIR, backup_name)
            
            # Create backup directory
            os.makedirs(backup_path, exist_ok=True)
            
            backup_info = {
                'name': backup_name,
                'type': backup_type,
                'created_at': datetime.now().isoformat(),
                'files': [],
                'size_mb': 0
            }
            
            if backup_type == "full":
                # Backup database
                if self.db:
                    db_backup_file = os.path.join(backup_path, "database.json")
                    await self._backup_database(db_backup_file)
                    backup_info['files'].append('database.json')
                
                # Backup configuration
                config_backup_file = os.path.join(backup_path, "config.json")
                self._backup_config(config_backup_file)
                backup_info['files'].append('config.json')
                
                # Backup logs
                logs_backup_file = os.path.join(backup_path, "logs.tar.gz")
                self._backup_logs(logs_backup_file)
                backup_info['files'].append('logs.tar.gz')
                
                # Backup AI knowledge
                ai_backup_file = os.path.join(backup_path, "ai_knowledge.json")
                await self._backup_ai_knowledge(ai_backup_file)
                backup_info['files'].append('ai_knowledge.json')
                
            elif backup_type == "database":
                # Only backup database
                if self.db:
                    db_backup_file = os.path.join(backup_path, "database.json")
                    await self._backup_database(db_backup_file)
                    backup_info['files'].append('database.json')
            
            elif backup_type == "config":
                # Only backup configuration
                config_backup_file = os.path.join(backup_path, "config.json")
                self._backup_config(config_backup_file)
                backup_info['files'].append('config.json')
            
            # Create zip archive
            zip_path = backup_path + ".zip"
            self._create_zip(backup_path, zip_path)
            
            # Cleanup temp directory
            shutil.rmtree(backup_path)
            
            # Calculate size
            size_mb = os.path.getsize(zip_path) / (1024 * 1024)
            backup_info['size_mb'] = round(size_mb, 2)
            backup_info['file_path'] = zip_path
            
            # Save backup info
            info_file = os.path.join(self.config.BACKUP_DIR, f"{backup_name}_info.json")
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Backup created: {backup_name} ({size_mb:.2f} MB)")
            return backup_info
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return {'error': str(e), 'success': False}
    
    async def _backup_database(self, output_file: str):
        """Backup database to file"""
        if not self.db:
            return False
        
        try:
            # Backup users
            users_ref = self.db.db.collection('users')
            users_docs = users_ref.limit(10000).stream()
            
            users_data = []
            for doc in users_docs:
                user_data = doc.to_dict()
                # Remove sensitive data
                sensitive_fields = ['settings', 'stats', 'last_active']
                for field in sensitive_fields:
                    user_data.pop(field, None)
                users_data.append(user_data)
            
            # Backup transactions
            tx_ref = self.db.db.collection('transactions')
            tx_docs = tx_ref.limit(10000).stream()
            
            transactions_data = []
            for doc in tx_docs:
                transactions_data.append(doc.to_dict())
            
            # Backup messages (for AI)
            msg_ref = self.db.db.collection('messages')
            msg_docs = msg_ref.limit(5000).stream()
            
            messages_data = []
            for doc in msg_docs:
                messages_data.append(doc.to_dict())
            
            # Backup payments
            payments_ref = self.db.db.collection('payments')
            payments_docs = payments_ref.limit(5000).stream()
            
            payments_data = []
            for doc in payments_docs:
                payments_data.append(doc.to_dict())
            
            # Combine all data
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'users': {
                    'count': len(users_data),
                    'data': users_data[:1000]  # Limit to 1000 users
                },
                'transactions': {
                    'count': len(transactions_data),
                    'data': transactions_data[:2000]
                },
                'messages': {
                    'count': len(messages_data),
                    'data': messages_data[:1000]
                },
                'payments': {
                    'count': len(payments_data),
                    'data': payments_data[:500]
                }
            }
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error backing up database: {e}")
            return False
    
    def _backup_config(self, output_file: str):
        """Backup configuration"""
        try:
            config_data = {
                'bot_config': self.config.to_dict(),
                'backup_time': datetime.now().isoformat(),
                'version': self.config.BOT_VERSION
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error backing up config: {e}")
            return False
    
    def _backup_logs(self, output_file: str):
        """Backup log files"""
        try:
            import tarfile
            
            log_files = []
            if os.path.exists('logs'):
                for file in os.listdir('logs'):
                    if file.endswith('.log'):
                        log_files.append(os.path.join('logs', file))
            
            if log_files:
                with tarfile.open(output_file, 'w:gz') as tar:
                    for log_file in log_files:
                        tar.add(log_file, arcname=os.path.basename(log_file))
            
            return True
            
        except Exception as e:
            print(f"Error backing up logs: {e}")
            return False
    
    async def _backup_ai_knowledge(self, output_file: str):
        """Backup AI knowledge"""
        try:
            # This would backup AI training data
            # For now, create placeholder
            ai_data = {
                'backup_time': datetime.now().isoformat(),
                'note': 'AI knowledge backup (implement based on your AI system)'
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(ai_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error backing up AI knowledge: {e}")
            return False
    
    def _create_zip(self, source_dir: str, output_zip: str):
        """Create zip file from directory"""
        try:
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
            
            return True
            
        except Exception as e:
            print(f"Error creating zip: {e}")
            return False
    
    async def list_backups(self) -> List[Dict]:
        """List all backups"""
        backups = []
        
        try:
            for file in os.listdir(self.config.BACKUP_DIR):
                if file.endswith('.zip'):
                    file_path = os.path.join(self.config.BACKUP_DIR, file)
                    file_stat = os.stat(file_path)
                    
                    # Try to find info file
                    info_file = file_path.replace('.zip', '_info.json')
                    backup_info = {}
                    
                    if os.path.exists(info_file):
                        with open(info_file, 'r', encoding='utf-8') as f:
                            backup_info = json.load(f)
                    
                    backups.append({
                        'name': file,
                        'path': file_path,
                        'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                        'created_at': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        'info': backup_info
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return backups
            
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []
    
    async def restore_backup(self, backup_file: str) -> Dict:
        """Restore from backup"""
        try:
            # Extract backup
            extract_dir = os.path.join(self.config.BACKUP_DIR, "restore_temp")
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            
            os.makedirs(extract_dir)
            
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            # Find backup info
            backup_name = os.path.basename(backup_file).replace('.zip', '')
            info_file = os.path.join(extract_dir, f"{backup_name}_info.json")
            
            if not os.path.exists(info_file):
                # Look for info file in backup
                for file in os.listdir(extract_dir):
                    if file.endswith('_info.json'):
                        info_file = os.path.join(extract_dir, file)
                        break
            
            if os.path.exists(info_file):
                with open(info_file, 'r', encoding='utf-8') as f:
                    backup_info = json.load(f)
                
                backup_type = backup_info.get('type', 'unknown')
                
                if backup_type == 'full':
                    # Restore everything
                    print("🔧 Restoring full backup...")
                    
                    # Restore config
                    config_file = os.path.join(extract_dir, "config.json")
                    if os.path.exists(config_file):
                        self._restore_config(config_file)
                    
                    # Restore database
                    db_file = os.path.join(extract_dir, "database.json")
                    if os.path.exists(db_file):
                        await self._restore_database(db_file)
                    
                elif backup_type == 'database':
                    # Restore only database
                    db_file = os.path.join(extract_dir, "database.json")
                    if os.path.exists(db_file):
                        await self._restore_database(db_file)
                
                elif backup_type == 'config':
                    # Restore only config
                    config_file = os.path.join(extract_dir, "config.json")
                    if os.path.exists(config_file):
                        self._restore_config(config_file)
            
            # Cleanup
            shutil.rmtree(extract_dir)
            
            return {
                'success': True,
                'message': f"✅ Backup restored successfully: {backup_name}",
                'backup_info': backup_info if 'backup_info' in locals() else {}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"❌ Backup restore failed: {str(e)}"
            }
    
    async def _restore_database(self, backup_file: str):
        """Restore database from backup"""
        # Note: This is a complex operation and depends on your database
        # For Firestore, you would need to write data back
        print("⚠️ Database restore not implemented (requires manual implementation)")
        return False
    
    def _restore_config(self, backup_file: str):
        """Restore configuration from backup"""
        print("⚠️ Config restore not implemented (requires manual implementation)")
        return False
    
    async def cleanup_old_backups(self):
        """Cleanup old backups"""
        try:
            backups = await self.list_backups()
            
            if len(backups) <= self.config.MAX_BACKUPS:
                return 0
            
            # Sort by creation time (oldest first)
            backups.sort(key=lambda x: x['created_at'])
            
            # Delete old backups
            delete_count = 0
            for i in range(len(backups) - self.config.MAX_BACKUPS):
                backup = backups[i]
                
                try:
                    # Delete backup file
                    os.remove(backup['path'])
                    
                    # Delete info file if exists
                    info_file = backup['path'].replace('.zip', '_info.json')
                    if os.path.exists(info_file):
                        os.remove(info_file)
                    
                    delete_count += 1
                    print(f"🗑️ Deleted old backup: {backup['name']}")
                    
                except Exception as e:
                    print(f"Error deleting backup {backup['name']}: {e}")
            
            print(f"🧹 Cleaned up {delete_count} old backups")
            return delete_count
            
        except Exception as e:
            print(f"Error cleaning up old backups: {e}")
            return 0
    
    async def get_backup_stats(self) -> Dict:
        """Get backup statistics"""
        backups = await self.list_backups()
        
        total_size = sum(b['size_mb'] for b in backups)
        oldest_backup = backups[-1]['created_at'] if backups else 'N/A'
        newest_backup = backups[0]['created_at'] if backups else 'N/A'
        
        # Count by type
        types_count = {}
        for backup in backups:
            backup_type = backup.get('info', {}).get('type', 'unknown')
            types_count[backup_type] = types_count.get(backup_type, 0) + 1
        
        return {
            'total_backups': len(backups),
            'total_size_mb': round(total_size, 2),
            'oldest_backup': oldest_backup,
            'newest_backup': newest_backup,
            'backups_by_type': types_count,
            'max_backups': self.config.MAX_BACKUPS,
            'auto_backup_enabled': self.config.AUTO_BACKUP,
            'backup_interval': self.config.BACKUP_INTERVAL
        }
    
    async def run_scheduled_backup(self):
        """Run scheduled backup"""
        if not self.config.AUTO_BACKUP:
            return
        
        print("⏰ Running scheduled backup...")
        
        # Create backup
        backup_result = await self.create_backup("full")
        
        if 'error' not in backup_result:
            # Cleanup old backups
            await self.cleanup_old_backups()
            
            print("✅ Scheduled backup completed")
        else:
            print(f"❌ Scheduled backup failed: {backup_result.get('error')}")