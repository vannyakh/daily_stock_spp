"""
Configuration Utilities
Utilities for managing settings, environment variables, and configuration files
"""

import os
import json
import yaml
import configparser
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Main configuration management utility class"""
    
    def __init__(self, config_file: str = None, env_prefix: str = "STOCK_SCRAPER"):
        self.config_file = config_file
        self.env_prefix = env_prefix
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file and environment variables"""
        # Load from file if specified
        if self.config_file and os.path.exists(self.config_file):
            self._load_from_file()
        
        # Load from environment variables
        self._load_from_env()
        
        # Set defaults
        self._set_defaults()
    
    def _load_from_file(self):
        """Load configuration from file"""
        try:
            file_path = Path(self.config_file)
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.json':
                with open(file_path, 'r') as f:
                    file_config = json.load(f)
            elif file_extension in ['.yaml', '.yml']:
                with open(file_path, 'r') as f:
                    file_config = yaml.safe_load(f)
            elif file_extension == '.ini':
                config_parser = configparser.ConfigParser()
                config_parser.read(file_path)
                file_config = self._parse_ini_config(config_parser)
            else:
                logger.warning(f"Unsupported config file format: {file_extension}")
                return
            
            self.config.update(file_config)
            logger.info(f"Configuration loaded from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error loading configuration file {self.config_file}: {e}")
    
    def _parse_ini_config(self, config_parser: configparser.ConfigParser) -> Dict:
        """Parse INI configuration to dictionary"""
        config = {}
        
        for section in config_parser.sections():
            config[section] = {}
            for key, value in config_parser.items(section):
                # Try to convert value to appropriate type
                config[section][key] = self._convert_value(value)
        
        return config
    
    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate type"""
        # Try to convert to boolean
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # Try to convert to integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try to convert to float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # Remove prefix and convert to lowercase
                config_key = key[len(self.env_prefix) + 1:].lower()
                
                # Convert value to appropriate type
                converted_value = self._convert_value(value)
                
                # Handle nested keys (e.g., DATABASE_HOST -> database.host)
                self._set_nested_config(config_key, converted_value)
    
    def _set_nested_config(self, key: str, value: Any):
        """Set nested configuration value"""
        keys = key.split('_')
        current = self.config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def _set_defaults(self):
        """Set default configuration values"""
        defaults = {
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'file': 'logs/stock_scraper.log'
            },
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'stock_data',
                'user': 'postgres',
                'password': ''
            },
            'api': {
                'host': '0.0.0.0',
                'port': 8000,
                'debug': False,
                'workers': 4
            },
            'scraping': {
                'max_workers': 4,
                'timeout': 30,
                'retry_attempts': 3,
                'delay_between_requests': 1.0
            },
            'storage': {
                'type': 'local',
                'path': 'data',
                'backup_enabled': True,
                'backup_retention_days': 30
            }
        }
        
        # Only set defaults for missing keys
        for section, section_config in defaults.items():
            if section not in self.config:
                self.config[section] = {}
            
            for key, value in section_config.items():
                if key not in self.config[section]:
                    self.config[section][key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports nested keys)"""
        try:
            keys = key.split('.')
            current = self.config
            
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return default
            
            return current
            
        except Exception as e:
            logger.error(f"Error getting config key {key}: {e}")
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value by key (supports nested keys)"""
        try:
            keys = key.split('.')
            current = self.config
            
            # Navigate to parent of target key
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # Set the value
            current[keys[-1]] = value
            
        except Exception as e:
            logger.error(f"Error setting config key {key}: {e}")
    
    def has(self, key: str) -> bool:
        """Check if configuration key exists"""
        return self.get(key) is not None
    
    def get_section(self, section: str) -> Dict:
        """Get entire configuration section"""
        return self.config.get(section, {})
    
    def save_config(self, file_path: str = None):
        """Save configuration to file"""
        try:
            if not file_path:
                file_path = self.config_file
            
            if not file_path:
                logger.error("No file path specified for saving configuration")
                return False
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.json':
                with open(file_path, 'w') as f:
                    json.dump(self.config, f, indent=2, default=str)
            elif file_extension in ['.yaml', '.yml']:
                with open(file_path, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            elif file_extension == '.ini':
                self._save_to_ini(file_path)
            else:
                logger.error(f"Unsupported file format for saving: {file_extension}")
                return False
            
            logger.info(f"Configuration saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def _save_to_ini(self, file_path: Path):
        """Save configuration to INI format"""
        config_parser = configparser.ConfigParser()
        
        for section, section_config in self.config.items():
            if not config_parser.has_section(section):
                config_parser.add_section(section)
            
            for key, value in section_config.items():
                if isinstance(value, dict):
                    # Handle nested dictionaries
                    for nested_key, nested_value in value.items():
                        config_parser.set(section, f"{key}_{nested_key}", str(nested_value))
                else:
                    config_parser.set(section, key, str(value))
        
        with open(file_path, 'w') as f:
            config_parser.write(f)
    
    def reload(self):
        """Reload configuration from file and environment"""
        self.config = {}
        self.load_config()
    
    def export_env(self, file_path: str = None):
        """Export configuration as environment variables"""
        try:
            if not file_path:
                file_path = f"{self.env_prefix.lower()}.env"
            
            with open(file_path, 'w') as f:
                f.write(f"# {self.env_prefix} Configuration\n")
                f.write(f"# Generated on {os.path.getenv('USER', 'unknown')}\n\n")
                
                self._write_env_section(f, self.config, "")
            
            logger.info(f"Environment variables exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting environment variables: {e}")
            return False
    
    def _write_env_section(self, file, config: Dict, prefix: str):
        """Recursively write environment variables"""
        for key, value in config.items():
            if isinstance(value, dict):
                self._write_env_section(file, value, f"{prefix}_{key}" if prefix else key)
            else:
                env_key = f"{self.env_prefix}_{prefix}_{key}".upper() if prefix else f"{self.env_prefix}_{key}".upper()
                file.write(f"{env_key}={value}\n")
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'missing_required': []
        }
        
        # Check required fields
        required_fields = [
            'logging.level',
            'api.host',
            'api.port',
            'scraping.max_workers'
        ]
        
        for field in required_fields:
            if not self.has(field):
                validation_result['missing_required'].append(field)
                validation_result['is_valid'] = False
        
        # Validate specific fields
        if self.has('api.port'):
            port = self.get('api.port')
            if not isinstance(port, int) or port < 1 or port > 65535:
                validation_result['errors'].append(f"Invalid API port: {port}")
                validation_result['is_valid'] = False
        
        if self.has('scraping.max_workers'):
            workers = self.get('scraping.max_workers')
            if not isinstance(workers, int) or workers < 1:
                validation_result['errors'].append(f"Invalid max workers: {workers}")
                validation_result['is_valid'] = False
        
        if self.has('logging.level'):
            level = self.get('logging.level')
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if level.upper() not in valid_levels:
                validation_result['errors'].append(f"Invalid logging level: {level}")
                validation_result['is_valid'] = False
        
        return validation_result

class EnvironmentConfig:
    """Helper class for environment-specific configuration"""
    
    @staticmethod
    def get_environment() -> str:
        """Get current environment"""
        return os.getenv('ENVIRONMENT', 'development').lower()
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production environment"""
        return EnvironmentConfig.get_environment() == 'production'
    
    @staticmethod
    def is_development() -> bool:
        """Check if running in development environment"""
        return EnvironmentConfig.get_environment() == 'development'
    
    @staticmethod
    def is_testing() -> bool:
        """Check if running in testing environment"""
        return EnvironmentConfig.get_environment() == 'testing'
    
    @staticmethod
    def get_config_file(env: str = None) -> str:
        """Get configuration file for environment"""
        if not env:
            env = EnvironmentConfig.get_environment()
        
        config_files = {
            'development': 'config/dev.json',
            'production': 'config/prod.json',
            'testing': 'config/test.json'
        }
        
        return config_files.get(env, 'config/config.json')

class SecretManager:
    """Helper class for managing secrets and sensitive configuration"""
    
    def __init__(self, secrets_file: str = None):
        self.secrets_file = secrets_file or '.secrets'
        self.secrets = {}
        self.load_secrets()
    
    def load_secrets(self):
        """Load secrets from file"""
        try:
            if os.path.exists(self.secrets_file):
                with open(self.secrets_file, 'r') as f:
                    self.secrets = json.load(f)
                logger.info("Secrets loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load secrets: {e}")
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """Get secret value"""
        return self.secrets.get(key, default)
    
    def set_secret(self, key: str, value: Any):
        """Set secret value"""
        self.secrets[key] = value
    
    def save_secrets(self):
        """Save secrets to file"""
        try:
            with open(self.secrets_file, 'w') as f:
                json.dump(self.secrets, f, indent=2)
            logger.info("Secrets saved successfully")
        except Exception as e:
            logger.error(f"Error saving secrets: {e}")

# Utility functions
def load_config(config_file: str = None) -> ConfigManager:
    """Quick function to load configuration"""
    return ConfigManager(config_file)

def get_config_value(key: str, default: Any = None) -> Any:
    """Quick function to get configuration value"""
    config = ConfigManager()
    return config.get(key, default)

def is_production() -> bool:
    """Quick function to check if in production"""
    return EnvironmentConfig.is_production()

def get_secret(key: str, default: Any = None) -> Any:
    """Quick function to get secret"""
    secrets = SecretManager()
    return secrets.get_secret(key, default)
