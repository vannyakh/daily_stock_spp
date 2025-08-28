"""
Cloudflare Storage Integration
Handles data storage across Cloudflare R2, KV, and D1 services
"""

import boto3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import logging
from cloudflare import CloudFlare
from cloudflare_config import CloudflareConfig

logger = logging.getLogger(__name__)

class CloudflareStorage:
    """Main class for Cloudflare storage operations"""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.setup_services()
    
    def setup_services(self):
        """Initialize all Cloudflare services"""
        try:
            # Setup R2 (S3-compatible)
            self.r2_client = boto3.client(
                's3',
                endpoint_url=self.config.r2_endpoint_url,
                aws_access_key_id=self.config.r2_access_key_id,
                aws_secret_access_key=self.config.r2_secret_access_key,
                region_name='auto'
            )
            
            # Setup Cloudflare API client
            self.cf = CloudFlare(token=self.config.api_token)
            
            logger.info("✅ Cloudflare services initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cloudflare services: {e}")
            raise
    
    def upload_stock_data(self, ticker: str, data: Dict, data_type: str = "comprehensive") -> bool:
        """Upload stock data to R2 storage"""
        try:
            # Create file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{ticker}_{data_type}_{timestamp}.json"
            file_path = f"stock_data/{data_type}/{filename}"
            
            # Convert data to JSON
            json_data = json.dumps(data, indent=2, default=str)
            
            # Upload to R2
            self.r2_client.put_object(
                Bucket=self.config.r2_bucket_name,
                Key=file_path,
                Body=json_data.encode('utf-8'),
                ContentType='application/json',
                Metadata={
                    'ticker': ticker,
                    'data_type': data_type,
                    'timestamp': timestamp,
                    'upload_date': datetime.now().isoformat()
                }
            )
            
            logger.info(f"✅ Uploaded {ticker} {data_type} data to R2: {file_path}")
            
            # Store metadata in KV if available
            if self.config.kv_namespace_id:
                self.store_metadata_in_kv(ticker, file_path, data_type, timestamp)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to upload {ticker} data: {e}")
            return False
    
    def upload_csv_data(self, ticker: str, csv_content: str, data_type: str = "intraday") -> bool:
        """Upload CSV data to R2 storage"""
        try:
            # Create file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{ticker}_{data_type}_{timestamp}.csv"
            file_path = f"csv_data/{data_type}/{filename}"
            
            # Upload to R2
            self.r2_client.put_object(
                Bucket=self.config.r2_bucket_name,
                Key=file_path,
                Body=csv_content.encode('utf-8'),
                ContentType='text/csv',
                Metadata={
                    'ticker': ticker,
                    'data_type': data_type,
                    'timestamp': timestamp,
                    'upload_date': datetime.now().isoformat()
                }
            )
            
            logger.info(f"✅ Uploaded {ticker} {data_type} CSV to R2: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to upload {ticker} CSV: {e}")
            return False
    
    def store_metadata_in_kv(self, ticker: str, file_path: str, data_type: str, timestamp: str):
        """Store metadata in Cloudflare KV"""
        try:
            if not self.config.kv_namespace_id:
                return
            
            metadata = {
                'ticker': ticker,
                'file_path': file_path,
                'data_type': data_type,
                'timestamp': timestamp,
                'upload_date': datetime.now().isoformat(),
                'bucket': self.config.r2_bucket_name
            }
            
            # Store in KV using Cloudflare API
            key = f"stock_metadata:{ticker}:{timestamp}"
            self.cf.kv.namespaces.values.put(
                self.config.account_id,
                self.config.kv_namespace_id,
                key,
                json.dumps(metadata)
            )
            
            logger.info(f"✅ Stored metadata in KV: {key}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to store metadata in KV: {e}")
    
    def get_stock_data(self, ticker: str, data_type: str = "comprehensive", limit: int = 10) -> List[Dict]:
        """Retrieve stock data from R2 storage"""
        try:
            # List objects with prefix
            prefix = f"stock_data/{data_type}/{ticker}_"
            
            response = self.r2_client.list_objects_v2(
                Bucket=self.config.r2_bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )
            
            data_files = []
            for obj in response.get('Contents', []):
                # Get object content
                obj_response = self.r2_client.get_object(
                    Bucket=self.config.r2_bucket_name,
                    Key=obj['Key']
                )
                
                content = obj_response['Body'].read().decode('utf-8')
                data = json.loads(content)
                
                data_files.append({
                    'key': obj['Key'],
                    'last_modified': obj['LastModified'],
                    'size': obj['Size'],
                    'data': data,
                    'metadata': obj_response.get('Metadata', {})
                })
            
            logger.info(f"✅ Retrieved {len(data_files)} {data_type} files for {ticker}")
            return data_files
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve {ticker} data: {e}")
            return []
    
    def get_latest_stock_data(self, ticker: str, data_type: str = "comprehensive") -> Optional[Dict]:
        """Get the most recent stock data for a ticker"""
        try:
            data_files = self.get_stock_data(ticker, data_type, limit=1)
            if data_files:
                return data_files[0]['data']
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get latest data for {ticker}: {e}")
            return None
    
    def delete_old_data(self, days_old: int = 30) -> int:
        """Delete data older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            deleted_count = 0
            
            # List all objects
            response = self.r2_client.list_objects_v2(
                Bucket=self.config.r2_bucket_name
            )
            
            for obj in response.get('Contents', []):
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                    # Delete old object
                    self.r2_client.delete_object(
                        Bucket=self.config.r2_bucket_name,
                        Key=obj['Key']
                    )
                    deleted_count += 1
            
            logger.info(f"✅ Deleted {deleted_count} old files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Failed to delete old data: {e}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            response = self.r2_client.list_objects_v2(
                Bucket=self.config.r2_bucket_name
            )
            
            total_size = sum(obj['Size'] for obj in response.get('Contents', []))
            total_files = len(response.get('Contents', []))
            
            # Group by data type
            data_types = {}
            for obj in response.get('Contents', []):
                key_parts = obj['Key'].split('/')
                if len(key_parts) >= 2:
                    data_type = key_parts[1]
                    if data_type not in data_types:
                        data_types[data_type] = {'count': 0, 'size': 0}
                    data_types[data_type]['count'] += 1
                    data_types[data_type]['size'] += obj['Size']
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'data_types': data_types,
                'bucket_name': self.config.r2_bucket_name
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get storage stats: {e}")
            return {}
    
    def backup_to_local(self, local_path: str = "cloudflare_backup") -> bool:
        """Create a local backup of all data"""
        try:
            os.makedirs(local_path, exist_ok=True)
            
            response = self.r2_client.list_objects_v2(
                Bucket=self.config.r2_bucket_name
            )
            
            for obj in response.get('Contents', []):
                # Create local directory structure
                local_file_path = os.path.join(local_path, obj['Key'])
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                
                # Download file
                obj_response = self.r2_client.get_object(
                    Bucket=self.config.r2_bucket_name,
                    Key=obj['Key']
                )
                
                with open(local_file_path, 'wb') as f:
                    f.write(obj_response['Body'].read())
            
            logger.info(f"✅ Local backup created at: {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create local backup: {e}")
            return False

class CloudflareDataProcessor:
    """Data processing utilities for Cloudflare storage"""
    
    def __init__(self, storage: CloudflareStorage):
        self.storage = storage
    
    def process_and_store_stock_data(self, ticker: str, raw_data: Dict) -> bool:
        """Process raw stock data and store in Cloudflare"""
        try:
            # Process the data
            processed_data = self._process_stock_data(raw_data)
            
            # Store in R2
            success = self.storage.upload_stock_data(ticker, processed_data)
            
            if success:
                logger.info(f"✅ Successfully processed and stored {ticker} data")
                return True
            else:
                logger.error(f"❌ Failed to store processed {ticker} data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to process {ticker} data: {e}")
            return False
    
    def _process_stock_data(self, raw_data: Dict) -> Dict:
        """Process raw stock data for storage"""
        processed_data = {
            'processed_at': datetime.now().isoformat(),
            'data_version': '2.0',
            'raw_data': raw_data,
            'summary': self._create_summary(raw_data)
        }
        return processed_data
    
    def _create_summary(self, data: Dict) -> Dict:
        """Create a summary of the stock data"""
        summary = {
            'ticker': data.get('ticker', ''),
            'company_name': data.get('info', {}).get('longName', ''),
            'current_price': data.get('current_price', 0),
            'market_cap': data.get('info', {}).get('marketCap', 0),
            'volume': data.get('volume', 0),
            'data_points': len(data.get('intraday_data', []))
        }
        return summary

# Utility functions
def create_cloudflare_storage(config_path: str = 'cloudflare_config.json') -> CloudflareStorage:
    """Create Cloudflare storage instance from config file"""
    try:
        config = CloudflareConfig.from_file(config_path)
        if not config.validate():
            raise ValueError("Invalid Cloudflare configuration")
        
        return CloudflareStorage(config)
        
    except Exception as e:
        logger.error(f"❌ Failed to create Cloudflare storage: {e}")
        raise

def test_cloudflare_connection(storage: CloudflareStorage) -> bool:
    """Test Cloudflare connection and permissions"""
    try:
        # Test R2 access
        storage.r2_client.list_objects_v2(
            Bucket=storage.config.r2_bucket_name,
            MaxKeys=1
        )
        
        # Test Cloudflare API access
        storage.cf.user.tokens.verify()
        
        logger.info("✅ Cloudflare connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Cloudflare connection test failed: {e}")
        return False
