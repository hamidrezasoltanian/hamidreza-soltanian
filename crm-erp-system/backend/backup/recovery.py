import os
import zipfile
import subprocess
import shutil
from datetime import datetime
from django.conf import settings
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


class RecoveryService:
    def __init__(self):
        self.backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        self.temp_dir = os.path.join(settings.BASE_DIR, 'temp_recovery')
    
    def ensure_temp_dir(self):
        """Create temporary directory for recovery"""
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def cleanup_temp_dir(self):
        """Clean up temporary directory"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def extract_backup(self, backup_path):
        """Extract backup file"""
        try:
            self.ensure_temp_dir()
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.temp_dir)
            
            logger.info(f"Backup extracted to: {self.temp_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error extracting backup: {str(e)}")
            return False
    
    def restore_database(self, backup_path):
        """Restore database from backup"""
        try:
            # Get database settings
            db_settings = settings.DATABASES['default']
            
            # Create restore command
            cmd = [
                'psql',
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
                logger.info("Database restored successfully")
                return True
            else:
                logger.error(f"Database restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Database restore error: {str(e)}")
            return False
    
    def restore_media(self, media_zip_path):
        """Restore media files from backup"""
        try:
            # Clear existing media files
            if os.path.exists(settings.MEDIA_ROOT):
                shutil.rmtree(settings.MEDIA_ROOT)
            
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            
            # Extract media files
            with zipfile.ZipFile(media_zip_path, 'r') as zipf:
                zipf.extractall(settings.MEDIA_ROOT)
            
            logger.info("Media files restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Media restore error: {str(e)}")
            return False
    
    def restore_code(self, code_zip_path):
        """Restore code from backup (optional)"""
        try:
            # This is optional and should be done carefully
            # Only restore specific files, not the entire codebase
            
            logger.info("Code restore skipped for safety")
            return True
            
        except Exception as e:
            logger.error(f"Code restore error: {str(e)}")
            return False
    
    def restore_full_backup(self, backup_path):
        """Restore full system from backup"""
        try:
            logger.info(f"Starting full restore from: {backup_path}")
            
            # Extract backup
            if not self.extract_backup(backup_path):
                return False
            
            # Find backup components
            db_backup = os.path.join(self.temp_dir, 'database.sql')
            media_backup = os.path.join(self.temp_dir, 'media.zip')
            code_backup = os.path.join(self.temp_dir, 'code.zip')
            
            success = True
            
            # Restore database
            if os.path.exists(db_backup):
                if not self.restore_database(db_backup):
                    success = False
            else:
                logger.warning("No database backup found")
            
            # Restore media
            if os.path.exists(media_backup):
                if not self.restore_media(media_backup):
                    success = False
            else:
                logger.warning("No media backup found")
            
            # Restore code (optional)
            if os.path.exists(code_backup):
                if not self.restore_code(code_backup):
                    success = False
            else:
                logger.warning("No code backup found")
            
            # Clean up
            self.cleanup_temp_dir()
            
            if success:
                logger.info("Full restore completed successfully")
                return True
            else:
                logger.error("Full restore completed with errors")
                return False
                
        except Exception as e:
            logger.error(f"Full restore error: {str(e)}")
            self.cleanup_temp_dir()
            return False
    
    def restore_database_only(self, backup_path):
        """Restore only database from backup"""
        try:
            logger.info(f"Starting database restore from: {backup_path}")
            
            if backup_path.endswith('.zip'):
                # Extract database.sql from zip
                if not self.extract_backup(backup_path):
                    return False
                
                db_backup = os.path.join(self.temp_dir, 'database.sql')
                if not os.path.exists(db_backup):
                    logger.error("No database.sql found in backup")
                    return False
            else:
                db_backup = backup_path
            
            success = self.restore_database(db_backup)
            
            if backup_path.endswith('.zip'):
                self.cleanup_temp_dir()
            
            return success
            
        except Exception as e:
            logger.error(f"Database restore error: {str(e)}")
            self.cleanup_temp_dir()
            return False
    
    def restore_media_only(self, backup_path):
        """Restore only media files from backup"""
        try:
            logger.info(f"Starting media restore from: {backup_path}")
            
            if backup_path.endswith('.zip'):
                # Extract media.zip from zip
                if not self.extract_backup(backup_path):
                    return False
                
                media_backup = os.path.join(self.temp_dir, 'media.zip')
                if not os.path.exists(media_backup):
                    logger.error("No media.zip found in backup")
                    return False
            else:
                media_backup = backup_path
            
            success = self.restore_media(media_backup)
            
            if backup_path.endswith('.zip'):
                self.cleanup_temp_dir()
            
            return success
            
        except Exception as e:
            logger.error(f"Media restore error: {str(e)}")
            self.cleanup_temp_dir()
            return False
    
    def verify_backup(self, backup_path):
        """Verify backup integrity"""
        try:
            if not os.path.exists(backup_path):
                return False, "Backup file not found"
            
            if not backup_path.endswith('.zip'):
                return False, "Invalid backup format"
            
            # Check if zip file is valid
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                file_list = zipf.namelist()
                
                required_files = ['database.sql', 'backup_info.txt']
                missing_files = [f for f in required_files if f not in file_list]
                
                if missing_files:
                    return False, f"Missing required files: {missing_files}"
            
            return True, "Backup is valid"
            
        except Exception as e:
            return False, f"Backup verification error: {str(e)}"
    
    def get_backup_info(self, backup_path):
        """Get information about backup"""
        try:
            if not os.path.exists(backup_path):
                return None
            
            info = {
                'filename': os.path.basename(backup_path),
                'size': os.path.getsize(backup_path),
                'created_at': datetime.fromtimestamp(os.path.getctime(backup_path)).isoformat(),
                'path': backup_path
            }
            
            if backup_path.endswith('.zip'):
                # Extract backup info
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    if 'backup_info.txt' in zipf.namelist():
                        with zipf.open('backup_info.txt') as f:
                            info['backup_details'] = f.read().decode('utf-8')
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting backup info: {str(e)}")
            return None