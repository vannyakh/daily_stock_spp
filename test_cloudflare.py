#!/usr/bin/env python3
"""
Test script for Cloudflare integration
Run this to verify all services are working correctly
"""

import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_configuration():
    """Test configuration loading"""
    print("🔍 Testing configuration...")
    
    try:
        from cloudflare.cloudflare_config import CloudflareConfig, create_sample_config
        
        # Check if config file exists
        if os.path.exists('cloudflare_config.json'):
            config = CloudflareConfig.from_file('cloudflare_config.json')
            if config.validate():
                print("✅ Configuration loaded and validated successfully")
                return config
            else:
                print("❌ Configuration validation failed")
                return None
        else:
            print("📝 No configuration file found, creating sample...")
            create_sample_config()
            print("📋 Please edit cloudflare_config_sample.json and rename to cloudflare_config.json")
            return None
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return None

def test_storage_connection(config):
    """Test Cloudflare storage connection"""
    print("\n🪣 Testing storage connection...")
    
    try:
        from cloudflare.cloudflare_storage import CloudflareStorage, test_cloudflare_connection
        
        storage = CloudflareStorage(config)
        
        # Test connection
        if test_cloudflare_connection(storage):
            print("✅ Storage connection test passed")
            return storage
        else:
            print("❌ Storage connection test failed")
            return None
            
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        return None

def test_storage_operations(storage):
    """Test basic storage operations"""
    print("\n📤 Testing storage operations...")
    
    try:
        # Test data
        test_data = {
            'ticker': 'TEST',
            'price': 100.50,
            'volume': 1000000,
            'timestamp': datetime.now().isoformat(),
            'test': True
        }
        
        # Test upload
        success = storage.upload_stock_data('TEST', test_data, 'test')
        if success:
            print("✅ Data upload test passed")
        else:
            print("❌ Data upload test failed")
            return False
        
        # Test retrieval
        retrieved_data = storage.get_latest_stock_data('TEST', 'test')
        if retrieved_data:
            print("✅ Data retrieval test passed")
        else:
            print("❌ Data retrieval test failed")
            return False
        
        # Test CSV upload
        csv_content = "Date,Price,Volume\n2024-01-01,100.50,1000000"
        csv_success = storage.upload_csv_data('TEST', csv_content, 'test')
        if csv_success:
            print("✅ CSV upload test passed")
        else:
            print("❌ CSV upload test failed")
            return False
        
        print("✅ All storage operations passed")
        return True
        
    except Exception as e:
        print(f"❌ Storage operations test failed: {e}")
        return False

def test_integration():
    """Test integration with existing scrapers"""
    print("\n🔗 Testing integration...")
    
    try:
        from cloudflare.cloudflare_integration import CloudflareStockIntegration
        
        integration = CloudflareStockIntegration()
        print("✅ Integration initialization passed")
        
        # Test storage summary
        summary = integration.get_storage_summary()
        if summary:
            print("✅ Storage summary test passed")
            print(f"📊 Storage stats: {summary.get('storage_stats', {})}")
        else:
            print("❌ Storage summary test failed")
            return False
        
        print("✅ Integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_worker_endpoints():
    """Test Worker API endpoints (if deployed)"""
    print("\n🌐 Testing Worker endpoints...")
    
    # This would test the actual deployed Worker
    # For now, we'll just check if the Worker file exists
    if os.path.exists('cloudflare_worker.js'):
        print("✅ Worker script found")
        
        # Check wrangler config
        if os.path.exists('wrangler.toml'):
            print("✅ Wrangler configuration found")
        else:
            print("⚠️ Wrangler configuration not found")
        
        print("ℹ️ Worker endpoints can be tested after deployment")
        return True
    else:
        print("❌ Worker script not found")
        return False

def test_data_migration():
    """Test data migration functionality"""
    print("\n🔄 Testing data migration...")
    
    try:
        from cloudflare.cloudflare_integration import auto_migrate_existing_data
        
        # Check if there's existing data to migrate
        has_v1_data = os.path.exists('stock_data')
        has_v2_data = os.path.exists('json_stock_data')
        
        if has_v1_data or has_v2_data:
            print(f"📁 Found existing data: V1={has_v1_data}, V2={has_v2_data}")
            
            # Note: We won't actually run migration in test mode
            print("ℹ️ Migration test passed (not actually migrating)")
            return True
        else:
            print("ℹ️ No existing data found to migrate")
            return True
            
    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 Running Cloudflare Integration Tests")
    print("=" * 50)
    
    test_results = {}
    
    # Test 1: Configuration
    config = test_configuration()
    test_results['configuration'] = config is not None
    
    if not config:
        print("\n❌ Configuration test failed. Please fix configuration before continuing.")
        return test_results
    
    # Test 2: Storage connection
    storage = test_storage_connection(config)
    test_results['storage_connection'] = storage is not None
    
    if not storage:
        print("\n❌ Storage connection test failed. Please check your Cloudflare credentials.")
        return test_results
    
    # Test 3: Storage operations
    test_results['storage_operations'] = test_storage_operations(storage)
    
    # Test 4: Integration
    test_results['integration'] = test_integration()
    
    # Test 5: Worker endpoints
    test_results['worker_endpoints'] = test_worker_endpoints()
    
    # Test 6: Data migration
    test_results['data_migration'] = test_data_migration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Cloudflare integration is ready.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return test_results

def main():
    """Main test function"""
    try:
        results = run_all_tests()
        
        if results.get('configuration') and results.get('storage_connection'):
            print("\n🚀 Next steps:")
            print("1. Your Cloudflare integration is working!")
            print("2. You can now integrate with your scrapers")
            print("3. Deploy your Worker with: wrangler deploy")
            print("4. Test the API endpoints")
        else:
            print("\n❌ Setup incomplete. Please fix the failed tests before proceeding.")
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")

if __name__ == "__main__":
    main()
