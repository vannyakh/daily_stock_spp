"""
Logging Helpers
Utilities for structured logging, log rotation, and log analysis
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import sys

class LoggerManager:
    """Main logging manager utility class"""
    
    def __init__(self, name: str = "stock_scraper", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.loggers = {}
        self.setup_default_logger()
    
    def setup_default_logger(self):
        """Setup default logger with file and console handlers"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{self.name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Store logger
        self.loggers['default'] = logger
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    def create_logger(self, name: str, level: str = "INFO", 
                     log_to_file: bool = True, log_to_console: bool = True) -> logging.Logger:
        """Create a new logger with specified configuration"""
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(f"{self.name}.{name}")
        logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        if log_to_file:
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / f"{name}.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=3
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, level.upper()))
            console_handler.setFormatter(simple_formatter)
            logger.addHandler(console_handler)
        
        # Store logger
        self.loggers[name] = logger
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        return logger
    
    def get_logger(self, name: str = "default") -> logging.Logger:
        """Get existing logger by name"""
        return self.loggers.get(name, self.loggers.get('default'))
    
    def set_log_level(self, name: str, level: str):
        """Set log level for a specific logger"""
        logger = self.get_logger(name)
        if logger:
            logger.setLevel(getattr(logging, level.upper()))
    
    def add_file_handler(self, name: str, filename: str, level: str = "DEBUG"):
        """Add a file handler to an existing logger"""
        logger = self.get_logger(name)
        if not logger:
            return
        
        file_handler = logging.FileHandler(self.log_dir / filename)
        file_handler.setLevel(getattr(logging, level.upper()))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)

class StructuredLogger:
    """Helper class for structured logging with JSON format"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_event(self, event_type: str, message: str, **kwargs):
        """Log a structured event"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'message': message,
            **kwargs
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_error(self, error: Exception, context: Dict = None):
        """Log an error with context"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        self.logger.error(json.dumps(error_data))
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        perf_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'performance',
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            **kwargs
        }
        
        self.logger.info(json.dumps(perf_data))
    
    def log_data_operation(self, operation: str, data_type: str, count: int, **kwargs):
        """Log data operation metrics"""
        data_op_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'data_operation',
            'operation': operation,
            'data_type': data_type,
            'count': count,
            **kwargs
        }
        
        self.logger.info(json.dumps(data_op_data))

class LogAnalyzer:
    """Helper class for analyzing log files"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
    
    def get_log_files(self) -> List[Path]:
        """Get all log files in the log directory"""
        if not self.log_dir.exists():
            return []
        
        return list(self.log_dir.glob("*.log"))
    
    def analyze_log_file(self, log_file: Path) -> Dict[str, Any]:
        """Analyze a single log file"""
        try:
            stats = {
                'filename': log_file.name,
                'size_bytes': log_file.stat().st_size,
                'size_mb': round(log_file.stat().st_size / (1024 * 1024), 2),
                'last_modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat(),
                'total_lines': 0,
                'error_count': 0,
                'warning_count': 0,
                'info_count': 0,
                'debug_count': 0,
                'level_distribution': {},
                'error_types': {},
                'time_distribution': {}
            }
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    stats['total_lines'] = line_num
                    
                    # Count log levels
                    if 'ERROR' in line:
                        stats['error_count'] += 1
                    elif 'WARNING' in line:
                        stats['warning_count'] += 1
                    elif 'INFO' in line:
                        stats['info_count'] += 1
                    elif 'DEBUG' in line:
                        stats['debug_count'] += 1
                    
                    # Extract error types
                    if 'ERROR' in line:
                        # Try to extract error type from structured logs
                        try:
                            if line.strip().startswith('{'):
                                log_data = json.loads(line.strip())
                                error_type = log_data.get('error_type', 'Unknown')
                                stats['error_types'][error_type] = stats['error_types'].get(error_type, 0) + 1
                        except:
                            pass
                    
                    # Extract timestamp for time distribution
                    try:
                        if line.strip().startswith('{'):
                            log_data = json.loads(line.strip())
                            timestamp = log_data.get('timestamp', '')
                            if timestamp:
                                hour = datetime.fromisoformat(timestamp).hour
                                stats['time_distribution'][hour] = stats['time_distribution'].get(hour, 0) + 1
                    except:
                        pass
            
            # Calculate level distribution percentages
            total_logs = stats['error_count'] + stats['warning_count'] + stats['info_count'] + stats['debug_count']
            if total_logs > 0:
                stats['level_distribution'] = {
                    'ERROR': round(stats['error_count'] / total_logs * 100, 2),
                    'WARNING': round(stats['warning_count'] / total_logs * 100, 2),
                    'INFO': round(stats['info_count'] / total_logs * 100, 2),
                    'DEBUG': round(stats['debug_count'] / total_logs * 100, 2)
                }
            
            return stats
            
        except Exception as e:
            return {
                'filename': log_file.name,
                'error': str(e)
            }
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Get summary of all log files"""
        log_files = self.get_log_files()
        
        summary = {
            'total_files': len(log_files),
            'total_size_mb': 0,
            'total_lines': 0,
            'total_errors': 0,
            'total_warnings': 0,
            'files': []
        }
        
        for log_file in log_files:
            file_stats = self.analyze_log_file(log_file)
            summary['files'].append(file_stats)
            
            if 'size_mb' in file_stats:
                summary['total_size_mb'] += file_stats['size_mb']
            if 'total_lines' in file_stats:
                summary['total_lines'] += file_stats['total_lines']
            if 'error_count' in file_stats:
                summary['total_errors'] += file_stats['error_count']
            if 'warning_count' in file_stats:
                summary['total_warnings'] += file_stats['warning_count']
        
        return summary
    
    def search_logs(self, search_term: str, log_files: List[Path] = None) -> List[Dict]:
        """Search for specific terms in log files"""
        if log_files is None:
            log_files = self.get_log_files()
        
        results = []
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if search_term.lower() in line.lower():
                            results.append({
                                'file': log_file.name,
                                'line_number': line_num,
                                'line': line.strip(),
                                'timestamp': self.extract_timestamp(line)
                            })
            except Exception as e:
                results.append({
                    'file': log_file.name,
                    'error': str(e)
                })
        
        return results
    
    def extract_timestamp(self, line: str) -> str:
        """Extract timestamp from log line"""
        try:
            if line.strip().startswith('{'):
                log_data = json.loads(line.strip())
                return log_data.get('timestamp', '')
            else:
                # Try to extract from standard log format
                parts = line.split(' - ')
                if len(parts) >= 2:
                    return parts[0]
        except:
            pass
        return ''

class LogRotator:
    """Helper class for log rotation and cleanup"""
    
    def __init__(self, log_dir: str = "logs", max_size_mb: int = 100, max_age_days: int = 30):
        self.log_dir = Path(log_dir)
        self.max_size_mb = max_size_mb
        self.max_age_days = max_age_days
    
    def rotate_logs(self) -> Dict[str, Any]:
        """Rotate logs based on size and age"""
        if not self.log_dir.exists():
            return {'rotated': 0, 'deleted': 0, 'errors': []}
        
        results = {
            'rotated': 0,
            'deleted': 0,
            'errors': []
        }
        
        current_time = datetime.now()
        
        for log_file in self.log_dir.glob("*.log"):
            try:
                file_size_mb = log_file.stat().st_size / (1024 * 1024)
                file_age = current_time - datetime.fromtimestamp(log_file.stat().st_mtime)
                
                # Check if file needs rotation
                if file_size_mb > self.max_size_mb:
                    self._rotate_log_file(log_file)
                    results['rotated'] += 1
                
                # Check if file is too old
                if file_age.days > self.max_age_days:
                    log_file.unlink()
                    results['deleted'] += 1
                    
            except Exception as e:
                results['errors'].append(f"Error processing {log_file.name}: {e}")
        
        return results
    
    def _rotate_log_file(self, log_file: Path):
        """Rotate a single log file"""
        try:
            # Create backup with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
            backup_path = log_file.parent / backup_name
            
            # Move current file to backup
            log_file.rename(backup_path)
            
            # Create new empty log file
            log_file.touch()
            
        except Exception as e:
            raise Exception(f"Failed to rotate log file {log_file.name}: {e}")
    
    def cleanup_old_backups(self) -> int:
        """Clean up old backup files"""
        if not self.log_dir.exists():
            return 0
        
        deleted_count = 0
        current_time = datetime.now()
        
        for backup_file in self.log_dir.glob("*_*.log"):
            try:
                file_age = current_time - datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                if file_age.days > self.max_age_days:
                    backup_file.unlink()
                    deleted_count += 1
                    
            except Exception as e:
                pass
        
        return deleted_count

# Utility functions
def setup_logging(name: str = "stock_scraper", level: str = "INFO", log_dir: str = "logs") -> LoggerManager:
    """Quick setup for logging"""
    manager = LoggerManager(name, log_dir)
    manager.set_log_level('default', level)
    return manager

def get_logger(name: str = "default") -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)

def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.info(f"Calling function: {func.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed with error: {e}")
            raise
    return wrapper

def log_performance(func):
    """Decorator to log function performance"""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Function {func.__name__} completed in {duration:.3f} seconds")
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Function {func.__name__} failed after {duration:.3f} seconds with error: {e}")
            raise
    return wrapper
