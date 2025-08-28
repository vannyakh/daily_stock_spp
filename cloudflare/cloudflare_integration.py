"""
Cloudflare Integration for Stock Scrapers
Integrates Cloudflare storage with existing V1 and V2 scrapers
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd

# Import Cloudflare storage
from cloudflare_storage import CloudflareStorage, CloudflareDataProcessor
from cloudflare_config import CloudflareConfig

logger = logging.getLogger(__name__)

class CloudflareStockIntegration:
    """Integrates Cloudflare storage with stock scrapers"""
    
    def __init__(self, config_path: str = 'cloudflare_config.json'):
        self.config = CloudflareConfig.from_file(config_path)
        self.storage = CloudflareStorage(self.config)
        self.processor = CloudflareDataProcessor(self.storage)
        
        logger.info("✅ Cloudflare integration initialized")
    
    def store_v1_stock_data(self, ticker: str, csv_data: pd.DataFrame, 
                           additional_info: Dict = None) -> bool:
        """Store V1 stock data in Cloudflare"""
        try:
            logger.info(f"🔄 Storing V1 data for {ticker} in Cloudflare...")
            
            # Convert CSV data to string
            csv_content = csv_data.to_csv(index=False)
            
            # Store CSV in R2
            csv_success = self.storage.upload_csv_data(ticker, csv_content, "intraday")
            
            if not csv_success:
                logger.error(f"❌ Failed to store CSV for {ticker}")
                return False
            
            # Create comprehensive data structure for V1
            v1_data = {
                'ticker': ticker,
                'data_type': 'v1_basic',
                'intraday_data': csv_data.to_dict('records'),
                'additional_info': additional_info or {},
                'scraped_at': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Store comprehensive data
            comprehensive_success = self.storage.upload_stock_data(ticker, v1_data, "v1_comprehensive")
            
            if comprehensive_success:
                logger.info(f"✅ V1 data for {ticker} stored successfully in Cloudflare")
                return True
            else:
                logger.error(f"❌ Failed to store comprehensive V1 data for {ticker}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error storing V1 data for {ticker}: {e}")
            return False
    
    def store_v2_stock_data(self, ticker: str, comprehensive_data: Dict) -> bool:
        """Store V2 stock data in Cloudflare"""
        try:
            logger.info(f"🔄 Storing V2 data for {ticker} in Cloudflare...")
            
            # Process and store the data
            success = self.processor.process_and_store_stock_data(ticker, comprehensive_data)
            
            if success:
                logger.info(f"✅ V2 data for {ticker} stored successfully in Cloudflare")
                return True
            else:
                logger.error(f"❌ Failed to store V2 data for {ticker}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error storing V2 data for {ticker}: {e}")
            return False
    
    def store_market_data(self, market_data: Dict) -> bool:
        """Store market overview data in Cloudflare"""
        try:
            logger.info("🔄 Storing market data in Cloudflare...")
            
            # Create market data structure
            market_structure = {
                'data_type': 'market_overview',
                'market_data': market_data,
                'generated_at': datetime.now().isoformat(),
                'version': '2.0'
            }
            
            # Store in R2
            success = self.storage.upload_stock_data(
                'MARKET_OVERVIEW', 
                market_structure, 
                "market_data"
            )
            
            if success:
                logger.info("✅ Market data stored successfully in Cloudflare")
                return True
            else:
                logger.error("❌ Failed to store market data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error storing market data: {e}")
            return False
    
    def migrate_existing_data(self, source_path: str, data_type: str = "v2") -> Dict[str, Any]:
        """Migrate existing local data to Cloudflare"""
        try:
            logger.info(f"🔄 Migrating existing {data_type} data to Cloudflare...")
            
            migration_stats = {
                'total_files': 0,
                'successful_uploads': 0,
                'failed_uploads': 0,
                'errors': []
            }
            
            if not os.path.exists(source_path):
                logger.error(f"❌ Source path does not exist: {source_path}")
                return migration_stats
            
            # Process files based on data type
            if data_type == "v1":
                migration_stats = self._migrate_v1_data(source_path)
            elif data_type == "v2":
                migration_stats = self._migrate_v2_data(source_path)
            else:
                logger.error(f"❌ Unknown data type: {data_type}")
                return migration_stats
            
            logger.info(f"✅ Migration completed. {migration_stats['successful_uploads']}/{migration_stats['total_files']} files uploaded")
            return migration_stats
            
        except Exception as e:
            logger.error(f"❌ Migration error: {e}")
            return {'error': str(e)}
    
    def _migrate_v1_data(self, source_path: str) -> Dict[str, Any]:
        """Migrate V1 CSV data"""
        stats = {
            'total_files': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'errors': []
        }
        
        try:
            # Find all CSV files
            csv_files = [f for f in os.listdir(source_path) if f.endswith('_intraday.csv')]
            stats['total_files'] = len(csv_files)
            
            for csv_file in csv_files:
                try:
                    file_path = os.path.join(source_path, csv_file)
                    ticker = csv_file.split('_')[0]
                    
                    # Read CSV data
                    csv_data = pd.read_csv(file_path)
                    
                    # Store in Cloudflare
                    success = self.store_v1_stock_data(ticker, csv_data)
                    
                    if success:
                        stats['successful_uploads'] += 1
                    else:
                        stats['failed_uploads'] += 1
                        stats['errors'].append(f"Failed to upload {csv_file}")
                        
                except Exception as e:
                    stats['failed_uploads'] += 1
                    stats['errors'].append(f"Error processing {csv_file}: {e}")
            
        except Exception as e:
            stats['errors'].append(f"Migration error: {e}")
        
        return stats
    
    def _migrate_v2_data(self, source_path: str) -> Dict[str, Any]:
        """Migrate V2 JSON data"""
        stats = {
            'total_files': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'errors': []
        }
        
        try:
            # Find all JSON files
            json_files = [f for f in os.listdir(source_path) if f.endswith('_comprehensive.json')]
            stats['total_files'] = len(json_files)
            
            for json_file in json_files:
                try:
                    file_path = os.path.join(source_path, json_file)
                    ticker = json_file.split('_')[0]
                    
                    # Read JSON data
                    with open(file_path, 'r') as f:
                        json_data = json.load(f)
                    
                    # Store in Cloudflare
                    success = self.store_v2_stock_data(ticker, json_data)
                    
                    if success:
                        stats['successful_uploads'] += 1
                    else:
                        stats['failed_uploads'] += 1
                        stats['errors'].append(f"Failed to upload {json_file}")
                        
                except Exception as e:
                    stats['failed_uploads'] += 1
                    stats['errors'].append(f"Error processing {json_file}: {e}")
            
        except Exception as e:
            stats['errors'].append(f"Migration error: {e}")
        
        return stats
    
    def get_storage_summary(self) -> Dict[str, Any]:
        """Get summary of stored data"""
        try:
            stats = self.storage.get_storage_stats()
            
            # Get recent uploads
            recent_uploads = []
            try:
                # This would require KV access to get recent metadata
                # For now, we'll return basic stats
                pass
            except Exception as e:
                logger.warning(f"⚠️ Could not get recent uploads: {e}")
            
            summary = {
                'storage_stats': stats,
                'recent_uploads': recent_uploads,
                'timestamp': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting storage summary: {e}")
            return {'error': str(e)}
    
    def cleanup_old_data(self, days_old: int = 30) -> int:
        """Clean up old data from Cloudflare storage"""
        try:
            logger.info(f"🧹 Cleaning up data older than {days_old} days...")
            
            deleted_count = self.storage.delete_old_data(days_old)
            
            logger.info(f"✅ Cleaned up {deleted_count} old files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return 0
    
    def create_backup(self, local_path: str = "cloudflare_backup") -> bool:
        """Create local backup of Cloudflare data"""
        try:
            logger.info(f"💾 Creating backup at {local_path}...")
            
            success = self.storage.backup_to_local(local_path)
            
            if success:
                logger.info(f"✅ Backup created successfully at {local_path}")
            else:
                logger.error("❌ Backup creation failed")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error creating backup: {e}")
            return False

# Integration functions for existing scrapers
def integrate_with_v1_scraper(scraper_instance, config_path: str = 'cloudflare_config.json'):
    """Integrate Cloudflare storage with V1 scraper"""
    try:
        integration = CloudflareStockIntegration(config_path)
        
        # Store the integration instance in the scraper
        scraper_instance.cloudflare_integration = integration
        
        logger.info("✅ Cloudflare integration added to V1 scraper")
        return integration
        
    except Exception as e:
        logger.error(f"❌ Failed to integrate Cloudflare with V1 scraper: {e}")
        return None

def integrate_with_v2_scraper(scraper_instance, config_path: str = 'cloudflare_config.json'):
    """Integrate Cloudflare storage with V2 scraper"""
    try:
        integration = CloudflareStockIntegration(config_path)
        
        # Store the integration instance in the scraper
        scraper_instance.cloudflare_integration = integration
        
        logger.info("✅ Cloudflare integration added to V2 scraper")
        return integration
        
    except Exception as e:
        logger.error(f"❌ Failed to integrate Cloudflare with V2 scraper: {e}")
        return None

def auto_migrate_existing_data(config_path: str = 'cloudflare_config.json'):
    """Automatically migrate existing data to Cloudflare"""
    try:
        integration = CloudflareStockIntegration(config_path)
        
        migration_results = {}
        
        # Migrate V1 data if it exists
        if os.path.exists('stock_data'):
            logger.info("🔄 Migrating V1 data...")
            v1_stats = integration.migrate_existing_data('stock_data', 'v1')
            migration_results['v1'] = v1_stats
        
        # Migrate V2 data if it exists
        if os.path.exists('json_stock_data'):
            logger.info("🔄 Migrating V2 data...")
            v2_stats = integration.migrate_existing_data('json_stock_data', 'v2')
            migration_results['v2'] = v2_stats
        
        logger.info("✅ Auto-migration completed")
        return migration_results
        
    except Exception as e:
        logger.error(f"❌ Auto-migration failed: {e}")
        return {'error': str(e)}

# Example usage
if __name__ == "__main__":
    # Test the integration
    try:
        integration = CloudflareStockIntegration()
        
        # Get storage summary
        summary = integration.get_storage_summary()
        print("Storage Summary:", json.dumps(summary, indent=2))
        
        # Test auto-migration
        migration_results = auto_migrate_existing_data()
        print("Migration Results:", json.dumps(migration_results, indent=2))
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
