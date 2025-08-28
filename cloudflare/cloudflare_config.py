"""
Cloudflare Configuration and Setup
This file contains all Cloudflare service configurations for the stock scraper
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import json

@dataclass
class CloudflareConfig:
    """Configuration class for Cloudflare services"""
    
    # API Configuration
    api_token: str
    account_id: str
    zone_id: str
    
    # R2 Object Storage Configuration
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_endpoint_url: str
    r2_bucket_name: str
    
    # Workers Configuration
    workers_script_name: str = "stock-data-processor"
    
    # KV Namespace Configuration
    kv_namespace_id: Optional[str] = None
    
    # D1 Database Configuration
    d1_database_id: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'CloudflareConfig':
        """Create configuration from environment variables"""
        return cls(
            api_token=os.getenv('CLOUDFLARE_API_TOKEN', ''),
            account_id=os.getenv('CLOUDFLARE_ACCOUNT_ID', ''),
            zone_id=os.getenv('CLOUDFLARE_ZONE_ID', ''),
            r2_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID', ''),
            r2_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY', ''),
            r2_endpoint_url=os.getenv('CLOUDFLARE_R2_ENDPOINT_URL', ''),
            r2_bucket_name=os.getenv('CLOUDFLARE_R2_BUCKET_NAME', ''),
            workers_script_name=os.getenv('CLOUDFLARE_WORKERS_SCRIPT_NAME', 'stock-data-processor'),
            kv_namespace_id=os.getenv('CLOUDFLARE_KV_NAMESPACE_ID'),
            d1_database_id=os.getenv('CLOUDFLARE_D1_DATABASE_ID')
        )
    
    @classmethod
    def from_file(cls, config_path: str = 'cloudflare_config.json') -> 'CloudflareConfig':
        """Create configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return cls(**config_data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Cloudflare config file not found: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in config file: {config_path}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'api_token': self.api_token,
            'account_id': self.account_id,
            'zone_id': self.zone_id,
            'r2_access_key_id': self.r2_access_key_id,
            'r2_secret_access_key': self.r2_secret_access_key,
            'r2_endpoint_url': self.r2_endpoint_url,
            'r2_bucket_name': self.r2_bucket_name,
            'workers_script_name': self.workers_script_name,
            'kv_namespace_id': self.kv_namespace_id,
            'd1_database_id': self.d1_database_id
        }
    
    def save_to_file(self, config_path: str = 'cloudflare_config.json'):
        """Save configuration to JSON file"""
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def validate(self) -> bool:
        """Validate that all required fields are present"""
        required_fields = [
            'api_token', 'account_id', 'zone_id',
            'r2_access_key_id', 'r2_secret_access_key',
            'r2_endpoint_url', 'r2_bucket_name'
        ]
        
        for field in required_fields:
            if not getattr(self, field):
                return False
        return True

# Default configuration
DEFAULT_CONFIG = CloudflareConfig(
    api_token='',
    account_id='',
    zone_id='',
    r2_access_key_id='',
    r2_secret_access_key='',
    r2_endpoint_url='',
    r2_bucket_name='stock-data-bucket',
    workers_script_name='stock-data-processor'
)

def create_sample_config():
    """Create a sample configuration file"""
    sample_config = {
        "api_token": "your_cloudflare_api_token_here",
        "account_id": "your_cloudflare_account_id_here",
        "zone_id": "your_cloudflare_zone_id_here",
        "r2_access_key_id": "your_r2_access_key_id_here",
        "r2_secret_access_key": "your_r2_secret_access_key_here",
        "r2_endpoint_url": "https://your_account_id.r2.cloudflarestorage.com",
        "r2_bucket_name": "stock-data-bucket",
        "workers_script_name": "stock-data-processor",
        "kv_namespace_id": "your_kv_namespace_id_here",
        "d1_database_id": "your_d1_database_id_here"
    }
    
    with open('cloudflare_config_sample.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("✅ Sample configuration file created: cloudflare_config_sample.json")
    print("📝 Please copy this file to cloudflare_config.json and fill in your actual values")

if __name__ == "__main__":
    create_sample_config()
