"""
File Management Helpers
Utilities for file operations, backups, and data persistence
"""

import os
import json
import csv
import pickle
import shutil
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FileManager:
    """Main file management utility class"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure all necessary directories exist"""
        directories = [
            'data',
            'logs',
            'backups',
            'exports',
            'temp',
            'cache'
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(exist_ok=True)
    
    def save_json(self, data: Any, filename: str, directory: str = "data") -> bool:
        """Save data as JSON file"""
        try:
            file_path = self.base_path / directory / f"{filename}.json"
            file_path.parent.mkdir(exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            
            logger.info(f"✅ JSON data saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving JSON file {filename}: {e}")
            return False
    
    def load_json(self, filename: str, directory: str = "data") -> Optional[Any]:
        """Load data from JSON file"""
        try:
            file_path = self.base_path / directory / f"{filename}.json"
            
            if not file_path.exists():
                logger.warning(f"⚠️ JSON file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"✅ JSON data loaded from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error loading JSON file {filename}: {e}")
            return None
    
    def save_csv(self, data: List[Dict], filename: str, directory: str = "data") -> bool:
        """Save data as CSV file"""
        try:
            if not data:
                logger.warning("⚠️ No data to save to CSV")
                return False
            
            file_path = self.base_path / directory / f"{filename}.csv"
            file_path.parent.mkdir(exist_ok=True)
            
            # Get fieldnames from first row
            fieldnames = list(data[0].keys())
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"✅ CSV data saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving CSV file {filename}: {e}")
            return False
    
    def load_csv(self, filename: str, directory: str = "data") -> Optional[List[Dict]]:
        """Load data from CSV file"""
        try:
            file_path = self.base_path / directory / f"{filename}.csv"
            
            if not file_path.exists():
                logger.warning(f"⚠️ CSV file not found: {file_path}")
                return None
            
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            
            logger.info(f"✅ CSV data loaded from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error loading CSV file {filename}: {e}")
            return None
    
    def save_pickle(self, data: Any, filename: str, directory: str = "data") -> bool:
        """Save data as pickle file"""
        try:
            file_path = self.base_path / directory / f"{filename}.pkl"
            file_path.parent.mkdir(exist_ok=True)
            
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"✅ Pickle data saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving pickle file {filename}: {e}")
            return False
    
    def load_pickle(self, filename: str, directory: str = "data") -> Optional[Any]:
        """Load data from pickle file"""
        try:
            file_path = self.base_path / directory / f"{filename}.pkl"
            
            if not file_path.exists():
                logger.warning(f"⚠️ Pickle file not found: {file_path}")
                return None
            
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            logger.info(f"✅ Pickle data loaded from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error loading pickle file {filename}: {e}")
            return None
    
    def backup_file(self, source_path: str, backup_dir: str = "backups") -> bool:
        """Create a backup of a file"""
        try:
            source_path = Path(source_path)
            if not source_path.exists():
                logger.warning(f"⚠️ Source file not found: {source_path}")
                return False
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_path = self.base_path / backup_dir / backup_filename
            
            backup_path.parent.mkdir(exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, backup_path)
            
            logger.info(f"✅ File backed up to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error backing up file {source_path}: {e}")
            return False
    
    def cleanup_old_backups(self, backup_dir: str = "backups", days_old: int = 30) -> int:
        """Clean up old backup files"""
        try:
            backup_path = self.base_path / backup_dir
            if not backup_path.exists():
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            deleted_count = 0
            
            for file_path in backup_path.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
            
            logger.info(f"✅ Cleaned up {deleted_count} old backup files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old backups: {e}")
            return 0
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {}
            
            stat = file_path.stat()
            
            info = {
                'name': file_path.name,
                'path': str(file_path.absolute()),
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'extension': file_path.suffix,
                'is_file': file_path.is_file(),
                'is_dir': file_path.is_dir()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Error getting file info for {file_path}: {e}")
            return {}

class DataExporter:
    """Helper class for exporting data in various formats"""
    
    @staticmethod
    def export_to_excel(data: List[Dict], filename: str, sheet_name: str = "Data") -> bool:
        """Export data to Excel file"""
        try:
            import pandas as pd
            
            df = pd.DataFrame(data)
            file_path = f"{filename}.xlsx"
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"✅ Data exported to Excel: {file_path}")
            return True
            
        except ImportError:
            logger.error("❌ openpyxl not installed. Install with: pip install openpyxl")
            return False
        except Exception as e:
            logger.error(f"❌ Error exporting to Excel: {e}")
            return False
    
    @staticmethod
    def export_to_sqlite(data: List[Dict], filename: str, table_name: str = "stock_data") -> bool:
        """Export data to SQLite database"""
        try:
            import sqlite3
            import pandas as pd
            
            df = pd.DataFrame(data)
            db_path = f"{filename}.db"
            
            conn = sqlite3.connect(db_path)
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.close()
            
            logger.info(f"✅ Data exported to SQLite: {db_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exporting to SQLite: {e}")
            return False
    
    @staticmethod
    def export_to_parquet(data: List[Dict], filename: str) -> bool:
        """Export data to Parquet file"""
        try:
            import pandas as pd
            
            df = pd.DataFrame(data)
            file_path = f"{filename}.parquet"
            
            df.to_parquet(file_path, index=False)
            
            logger.info(f"✅ Data exported to Parquet: {file_path}")
            return True
            
        except ImportError:
            logger.error("❌ pyarrow not installed. Install with: pip install pyarrow")
            return False
        except Exception as e:
            logger.error(f"❌ Error exporting to Parquet: {e}")
            return False

class CacheManager:
    """Helper class for managing data caching"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key"""
        # Create a safe filename from the key
        safe_key = "".join(c for c in key if c.isalnum() or c in ('-', '_')).rstrip()
        return self.cache_dir / f"{safe_key}.cache"
    
    def set_cache(self, key: str, data: Any, expire_hours: int = 24) -> bool:
        """Set cache data with expiration"""
        try:
            cache_data = {
                'data': data,
                'expires': (datetime.now() + timedelta(hours=expire_hours)).isoformat(),
                'created': datetime.now().isoformat()
            }
            
            cache_path = self.get_cache_path(key)
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting cache for key {key}: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Get cache data if not expired"""
        try:
            cache_path = self.get_cache_path(key)
            
            if not cache_path.exists():
                return None
            
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Check expiration
            expires = datetime.fromisoformat(cache_data['expires'])
            if datetime.now() > expires:
                # Cache expired, remove it
                cache_path.unlink()
                return None
            
            return cache_data['data']
            
        except Exception as e:
            logger.error(f"❌ Error getting cache for key {key}: {e}")
            return None
    
    def clear_cache(self, key: str = None) -> bool:
        """Clear cache for specific key or all cache"""
        try:
            if key:
                cache_path = self.get_cache_path(key)
                if cache_path.exists():
                    cache_path.unlink()
                    logger.info(f"✅ Cache cleared for key: {key}")
            else:
                # Clear all cache
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
                logger.info("✅ All cache cleared")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error clearing cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_files = list(self.cache_dir.glob("*.cache"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            stats = {
                'total_files': len(cache_files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_dir': str(self.cache_dir.absolute())
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting cache stats: {e}")
            return {}

# Utility functions
def ensure_file_directory(file_path: str) -> bool:
    """Ensure the directory for a file exists"""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"❌ Error creating directory for {file_path}: {e}")
        return False

def get_file_extension(file_path: str) -> str:
    """Get file extension from file path"""
    return Path(file_path).suffix.lower()

def is_valid_file(file_path: str, allowed_extensions: List[str] = None) -> bool:
    """Check if file is valid based on extension"""
    if allowed_extensions is None:
        allowed_extensions = ['.json', '.csv', '.txt', '.xlsx', '.parquet']
    
    extension = get_file_extension(file_path)
    return extension in allowed_extensions

def create_temp_file(prefix: str = "temp", suffix: str = ".tmp") -> str:
    """Create a temporary file and return its path"""
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, delete=False)
    temp_file.close()
    return temp_file.name
