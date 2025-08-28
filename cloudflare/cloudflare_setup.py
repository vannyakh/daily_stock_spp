#!/usr/bin/env python3
"""
Cloudflare Setup Script
Automates the setup of Cloudflare services for stock data storage
"""

import os
import json
import subprocess
import sys
from typing import Dict, List, Optional
import requests
from cloudflare_config import CloudflareConfig, create_sample_config

class CloudflareSetup:
    """Handles Cloudflare service setup and configuration"""
    
    def __init__(self):
        self.config = None
        self.setup_log = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log setup messages"""
        timestamp = self.get_timestamp()
        log_entry = f"[{timestamp}] {level}: {message}"
        self.setup_log.append(log_entry)
        print(log_entry)
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def check_prerequisites(self) -> bool:
        """Check if required tools are installed"""
        self.log("🔍 Checking prerequisites...")
        
        # Check if Wrangler is installed
        try:
            result = subprocess.run(['wrangler', '--version'], 
                                  capture_output=True, text=True, check=True)
            self.log(f"✅ Wrangler version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("❌ Wrangler not found. Please install with: npm install -g wrangler", "ERROR")
            return False
        
        # Check if Node.js is installed
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, check=True)
            self.log(f"✅ Node.js version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("❌ Node.js not found. Please install Node.js first", "ERROR")
            return False
        
        # Check if npm is installed
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True, check=True)
            self.log(f"✅ npm version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("❌ npm not found. Please install npm first", "ERROR")
            return False
        
        return True
    
    def create_configuration(self) -> bool:
        """Create and validate configuration"""
        self.log("⚙️ Setting up configuration...")
        
        # Check if config file exists
        if os.path.exists('cloudflare_config.json'):
            try:
                self.config = CloudflareConfig.from_file('cloudflare_config.json')
                self.log("✅ Configuration loaded from file")
            except Exception as e:
                self.log(f"❌ Failed to load config: {e}", "ERROR")
                return False
        else:
            # Create sample config
            create_sample_config()
            self.log("📝 Sample configuration created. Please edit cloudflare_config.json with your values")
            self.log("💡 After editing, run this script again")
            return False
        
        # Validate configuration
        if not self.config.validate():
            self.log("❌ Configuration validation failed", "ERROR")
            return False
        
        self.log("✅ Configuration validated successfully")
        return True
    
    def setup_r2_bucket(self) -> bool:
        """Set up R2 bucket for object storage"""
        self.log("🪣 Setting up R2 bucket...")
        
        try:
            # Create R2 bucket using Wrangler
            cmd = [
                'wrangler', 'r2', 'bucket', 'create',
                self.config.r2_bucket_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.log(f"✅ R2 bucket created: {self.config.r2_bucket_name}")
            
            # Create R2 API token
            self.create_r2_api_token()
            
            return True
            
        except subprocess.CalledProcessError as e:
            if "already exists" in e.stderr:
                self.log(f"ℹ️ R2 bucket already exists: {self.config.r2_bucket_name}")
                return True
            else:
                self.log(f"❌ Failed to create R2 bucket: {e.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ R2 setup error: {e}", "ERROR")
            return False
    
    def create_r2_api_token(self) -> bool:
        """Create R2 API token"""
        self.log("🔑 Creating R2 API token...")
        
        try:
            # This would typically be done through Cloudflare dashboard
            # For now, we'll provide instructions
            self.log("📋 Please create R2 API token manually:")
            self.log("   1. Go to Cloudflare Dashboard > R2 Object Storage")
            self.log("   2. Click 'Manage R2 API tokens'")
            self.log("   3. Create new token with R2 permissions")
            self.log("   4. Update cloudflare_config.json with the token details")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to create R2 API token: {e}", "ERROR")
            return False
    
    def setup_kv_namespace(self) -> bool:
        """Set up KV namespace for metadata"""
        self.log("🗄️ Setting up KV namespace...")
        
        try:
            # Create KV namespace using Wrangler
            cmd = [
                'wrangler', 'kv:namespace', 'create',
                'stock_metadata'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Extract namespace ID from output
            output = result.stdout
            if "id = " in output:
                namespace_id = output.split("id = ")[1].split("\n")[0].strip()
                self.log(f"✅ KV namespace created with ID: {namespace_id}")
                
                # Update config with namespace ID
                self.config.kv_namespace_id = namespace_id
                self.config.save_to_file()
                
                return True
            else:
                self.log("❌ Failed to extract namespace ID", "ERROR")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Failed to create KV namespace: {e.stderr}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ KV setup error: {e}", "ERROR")
            return False
    
    def setup_d1_database(self) -> bool:
        """Set up D1 database for structured data"""
        self.log("🗃️ Setting up D1 database...")
        
        try:
            # Create D1 database using Wrangler
            cmd = [
                'wrangler', 'd1', 'create',
                'stock_data_db'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Extract database ID from output
            output = result.stdout
            if "Created database" in output:
                # Parse the output to get database ID
                lines = output.split('\n')
                for line in lines:
                    if 'Created database' in line:
                        db_info = line.split('Created database')[1].strip()
                        self.log(f"✅ D1 database created: {db_info}")
                        
                        # Extract ID if possible
                        if 'id=' in db_info:
                            db_id = db_info.split('id=')[1].split()[0]
                            self.config.d1_database_id = db_id
                            self.config.save_to_file()
                        
                        break
                
                # Create database schema
                self.create_d1_schema()
                return True
            else:
                self.log("❌ Failed to create D1 database", "ERROR")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Failed to create D1 database: {e.stderr}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ D1 setup error: {e}", "ERROR")
            return False
    
    def create_d1_schema(self) -> bool:
        """Create D1 database schema"""
        self.log("📋 Creating D1 database schema...")
        
        schema_sql = """
        -- Stock data table
        CREATE TABLE IF NOT EXISTS stock_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            data_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            upload_date DATETIME NOT NULL,
            file_size INTEGER,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Market overview table
        CREATE TABLE IF NOT EXISTS market_overview (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            data TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_stock_data_ticker ON stock_data(ticker);
        CREATE INDEX IF NOT EXISTS idx_stock_data_date ON stock_data(upload_date);
        CREATE INDEX IF NOT EXISTS idx_market_overview_date ON market_overview(date);
        """
        
        try:
            # Write schema to file
            with open('d1_schema.sql', 'w') as f:
                f.write(schema_sql)
            
            # Apply schema to D1 database
            cmd = [
                'wrangler', 'd1', 'execute', 'stock_data_db',
                '--file', 'd1_schema.sql'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.log("✅ D1 database schema created")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Failed to create D1 schema: {e.stderr}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Schema creation error: {e}", "ERROR")
            return False
    
    def deploy_worker(self) -> bool:
        """Deploy Cloudflare Worker"""
        self.log("🚀 Deploying Cloudflare Worker...")
        
        try:
            # Deploy worker using Wrangler
            cmd = ['wrangler', 'deploy']
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if "Deployed" in result.stdout:
                self.log("✅ Worker deployed successfully")
                return True
            else:
                self.log("❌ Worker deployment failed", "ERROR")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Failed to deploy worker: {e.stderr}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Worker deployment error: {e}", "ERROR")
            return False
    
    def test_services(self) -> bool:
        """Test all Cloudflare services"""
        self.log("🧪 Testing Cloudflare services...")
        
        try:
            # Test R2 access
            self.log("Testing R2 access...")
            cmd = ['wrangler', 'r2', 'bucket', 'list']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.log("✅ R2 access test passed")
            
            # Test KV access
            self.log("Testing KV access...")
            cmd = ['wrangler', 'kv:key', 'list', '--namespace-id', self.config.kv_namespace_id]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.log("✅ KV access test passed")
            
            # Test D1 access
            self.log("Testing D1 access...")
            cmd = ['wrangler', 'd1', 'execute', 'stock_data_db', '--command', 'SELECT 1']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.log("✅ D1 access test passed")
            
            self.log("✅ All service tests passed")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Service test failed: {e.stderr}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Service test error: {e}", "ERROR")
            return False
    
    def run_setup(self) -> bool:
        """Run complete setup process"""
        self.log("🚀 Starting Cloudflare setup...")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Create configuration
        if not self.create_configuration():
            return False
        
        # Setup services
        if not self.setup_r2_bucket():
            return False
        
        if not self.setup_kv_namespace():
            return False
        
        if not self.setup_d1_database():
            return False
        
        # Deploy worker
        if not self.deploy_worker():
            return False
        
        # Test services
        if not self.test_services():
            return False
        
        self.log("🎉 Cloudflare setup completed successfully!")
        return True
    
    def save_setup_log(self, filename: str = "cloudflare_setup.log"):
        """Save setup log to file"""
        try:
            with open(filename, 'w') as f:
                for entry in self.setup_log:
                    f.write(entry + '\n')
            self.log(f"📝 Setup log saved to: {filename}")
        except Exception as e:
            self.log(f"❌ Failed to save setup log: {e}", "ERROR")

def main():
    """Main setup function"""
    print("🌐 Cloudflare Stock Data Storage Setup")
    print("=" * 50)
    
    setup = CloudflareSetup()
    
    try:
        success = setup.run_setup()
        
        if success:
            print("\n🎉 Setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Update your GitHub Actions workflows to use Cloudflare storage")
            print("2. Test the API endpoints")
            print("3. Monitor your Cloudflare dashboard for usage")
        else:
            print("\n❌ Setup failed. Check the logs above for details.")
        
        # Save setup log
        setup.save_setup_log()
        
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        setup.save_setup_log()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        setup.save_setup_log()
        sys.exit(1)

if __name__ == "__main__":
    main()
