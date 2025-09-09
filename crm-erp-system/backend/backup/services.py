import os
import subprocess
import zipfile
import shutil
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management import call_command
from django.core.cache import cache
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class BackupService:
    def __init__(self):
        self.backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_database_backup(self):
        """Create database backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"database_backup_{timestamp}.sql"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            # Get database settings
            db_settings = settings.DATABASES['default']
            
            # Create database dump
            cmd = [
                'pg_dump',
                '-h', db_settings['HOST'],
                '-U', db_settings['USER'],
                '-d', db_settings['NAME'],
                '-f', backup_path
            ]
            
            # Set password via environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = db_settings['PASSWORD']
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database backup created: {backup_path}")
                return backup_path
            else:
                logger.error(f"Database backup failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Database backup error: {str(e)}")
            return None
    
    def create_media_backup(self):
        """Create media files backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"media_backup_{timestamp}.zip"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            media_dir = settings.MEDIA_ROOT
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(media_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, media_dir)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Media backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Media backup error: {str(e)}")
            return None
    
    def create_code_backup(self):
        """Create code backup (excluding certain directories)"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"code_backup_{timestamp}.zip"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            exclude_dirs = {
                '__pycache__', '.git', 'node_modules', 'venv', 'env',
                '.pytest_cache', 'logs', 'backups', 'staticfiles'
            }
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(settings.BASE_DIR):
                    # Remove excluded directories
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    
                    for file in files:
                        if not file.startswith('.') and not file.endswith('.pyc'):
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, settings.BASE_DIR)
                            zipf.write(file_path, arcname)
            
            logger.info(f"Code backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Code backup error: {str(e)}")
            return None
    
    def create_full_backup(self):
        """Create full system backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"full_backup_{timestamp}"
        backup_dir = os.path.join(self.backup_dir, backup_name)
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create database backup
            db_backup = self.create_database_backup()
            if db_backup:
                shutil.move(db_backup, os.path.join(backup_dir, 'database.sql'))
            
            # Create media backup
            media_backup = self.create_media_backup()
            if media_backup:
                shutil.move(media_backup, os.path.join(backup_dir, 'media.zip'))
            
            # Create code backup
            code_backup = self.create_code_backup()
            if code_backup:
                shutil.move(code_backup, os.path.join(backup_dir, 'code.zip'))
            
            # Create backup info file
            info_file = os.path.join(backup_dir, 'backup_info.txt')
            with open(info_file, 'w') as f:
                f.write(f"Backup created: {datetime.now().isoformat()}\n")
                f.write(f"Database: {'Yes' if db_backup else 'No'}\n")
                f.write(f"Media: {'Yes' if media_backup else 'No'}\n")
                f.write(f"Code: {'Yes' if code_backup else 'No'}\n")
            
            # Create final zip
            final_backup = f"{backup_name}.zip"
            final_path = os.path.join(self.backup_dir, final_backup)
            
            with zipfile.ZipFile(final_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(backup_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, backup_dir)
                        zipf.write(file_path, arcname)
            
            # Clean up temporary directory
            shutil.rmtree(backup_dir)
            
            logger.info(f"Full backup created: {final_path}")
            return final_path
            
        except Exception as e:
            logger.error(f"Full backup error: {str(e)}")
            return None
    
    def cleanup_old_backups(self, days_to_keep=30):
        """Remove backups older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for filename in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, filename)
                
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        logger.info(f"Removed old backup: {filename}")
            
        except Exception as e:
            logger.error(f"Backup cleanup error: {str(e)}")
    
    def upload_to_s3(self, backup_path, bucket_name=None):
        """Upload backup to S3"""
        if not bucket_name:
            bucket_name = getattr(settings, 'AWS_BACKUP_BUCKET', None)
        
        if not bucket_name:
            logger.warning("No S3 bucket configured for backup upload")
            return False
        
        try:
            s3_client = boto3.client('s3')
            
            with open(backup_path, 'rb') as f:
                s3_client.upload_fileobj(f, bucket_name, os.path.basename(backup_path))
            
            logger.info(f"Backup uploaded to S3: {os.path.basename(backup_path)}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            return False
    
    def get_backup_list(self):
        """Get list of available backups"""
        try:
            backups = []
            
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.zip'):
                    file_path = os.path.join(self.backup_dir, filename)
                    file_size = os.path.getsize(file_path)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    backups.append({
                        'filename': filename,
                        'size': file_size,
                        'created_at': file_time.isoformat(),
                        'path': file_path
                    })
            
            return sorted(backups, key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting backup list: {str(e)}")
            return []


class BackupScheduler:
    def __init__(self):
        self.backup_service = BackupService()
    
    def schedule_daily_backup(self):
        """Schedule daily backup"""
        cache_key = 'last_daily_backup'
        last_backup = cache.get(cache_key)
        
        if not last_backup or last_backup.date() < datetime.now().date():
            logger.info("Starting scheduled daily backup")
            
            backup_path = self.backup_service.create_full_backup()
            if backup_path:
                # Upload to S3 if configured
                self.backup_service.upload_to_s3(backup_path)
                
                # Clean up old backups
                self.backup_service.cleanup_old_backups()
                
                # Update last backup time
                cache.set(cache_key, datetime.now(), 86400)  # 24 hours
                
                logger.info("Daily backup completed successfully")
            else:
                logger.error("Daily backup failed")
    
    def schedule_weekly_backup(self):
        """Schedule weekly backup"""
        cache_key = 'last_weekly_backup'
        last_backup = cache.get(cache_key)
        
        if not last_backup or (datetime.now() - last_backup).days >= 7:
            logger.info("Starting scheduled weekly backup")
            
            backup_path = self.backup_service.create_full_backup()
            if backup_path:
                # Upload to S3 if configured
                self.backup_service.upload_to_s3(backup_path)
                
                # Update last backup time
                cache.set(cache_key, datetime.now(), 604800)  # 7 days
                
                logger.info("Weekly backup completed successfully")
            else:
                logger.error("Weekly backup failed")