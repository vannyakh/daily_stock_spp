#!/usr/bin/env python3
"""
Enhanced Stock Scraper System Startup Script

This script provides an easy way to start different components of the system.
Supports both v1 (Basic) and v2 (Enhanced) versions.
"""

import os
import sys
import subprocess
import time
import json
import re
from pathlib import Path

def print_banner():
    """Print system banner"""
    print("🚀 Enhanced Stock Scraper System")
    print("=" * 50)
    print("Choose an option to get started:\n")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['yfinance', 'fastapi', 'uvicorn', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n💡 Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def repair_json_files():
    """Repair malformed JSON files in json_stock_data directory"""
    print("🔧 Repairing malformed JSON files...")
    
    json_data_path = Path("json_stock_data")
    if not json_data_path.exists():
        print("❌ No json_stock_data directory found")
        return
    
    json_files = list(json_data_path.glob("*_comprehensive.json"))
    if not json_files:
        print("❌ No comprehensive JSON files found")
        return
    
    print(f"📁 Found {len(json_files)} JSON files to check...")
    
    repaired_count = 0
    error_count = 0
    
    for json_file in json_files:
        try:
            # Try to read the file normally first
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
                json.loads(content)  # Test if valid JSON
            print(f"✅ {json_file.name} - Valid JSON")
        except json.JSONDecodeError as e:
            print(f"🔧 {json_file.name} - Malformed JSON, attempting repair...")
            try:
                # Attempt to repair common JSON issues
                repaired_content = repair_json_content(content)
                
                # Test the repaired content
                json.loads(repaired_content)
                
                # Write the repaired content back
                with open(json_file, 'w', encoding='utf-8') as f:
                    f.write(repaired_content)
                
                print(f"✅ {json_file.name} - Successfully repaired")
                repaired_count += 1
                
            except Exception as repair_error:
                print(f"❌ {json_file.name} - Repair failed: {repair_error}")
                error_count += 1
    
    print(f"\n📊 JSON Repair Summary:")
    print(f"   ✅ Successfully repaired: {repaired_count}")
    print(f"   ❌ Failed to repair: {error_count}")
    print(f"   📁 Total files processed: {len(json_files)}")

def repair_json_content(content):
    """Repair common JSON formatting issues"""
    # Fix missing quotes around property names
    # Pattern: {property: value} -> {"property": value}
    content = re.sub(r'(\s*)(\w+)(\s*):(\s*)', r'\1"\2"\3:\4', content)
    
    # Fix missing quotes around string values
    # Pattern: property: value, -> property: "value",
    content = re.sub(r':(\s*)([^"\d\[\]{},]+?)(\s*)([,}\]])', r':\1"\2"\3\4', content)
    
    # Fix trailing commas
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    
    # Fix single quotes to double quotes
    content = content.replace("'", '"')
    
    return content

def run_v1_scraper():
    """Run the v1 basic stock scraper"""
    print("📈 Starting V1 Basic Stock Scraper...")
    print("📊 This will collect intraday data for all stocks")
    print("📍 Using: v1/yf_scraper.py")
    
    try:
        subprocess.run([sys.executable, "v1/yf_scraper.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ V1 scraper failed with error: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  V1 scraper interrupted by user")

def run_v2_scraper():
    """Run the v2 enhanced stock scraper"""
    print("🚀 Starting V2 Enhanced Stock Scraper...")
    print("📊 This will collect comprehensive data for all stocks")
    print("📍 Using: v2/stock_scraper.py")
    print("⏱️  This may take several minutes depending on the number of stocks")
    
    try:
        subprocess.run([sys.executable, "v2/stock_scraper.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ V2 scraper failed with error: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  V2 scraper interrupted by user")

def run_v1_api_server():
    """Run the v1 API server"""
    print("🌐 Starting V1 Stock Data API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("📍 Using: v1/stock_api.py")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, "v1/stock_api.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ V1 API server failed with error: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  V1 API server stopped by user")

def run_v2_api_server():
    """Run the v2 API server"""
    print("🌐 Starting V2 Enhanced Stock Data API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("📍 Using: v2/stock_api_server.py")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, "v2/stock_api_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ V2 API server failed with error: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  V2 API server stopped by user")

def run_api_client():
    """Run the API client example"""
    print("📱 Running API Client Example...")
    print("🔍 This will demonstrate all available API endpoints")
    
    try:
        subprocess.run([sys.executable, "example/api_client_example.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ API client failed with error: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  API client interrupted by user")

def check_data_status():
    """Check the status of collected data"""
    print("📊 Checking Data Status...")
    
    # Check v1 data
    stock_data_path = Path("stock_data")
    if stock_data_path.exists():
        csv_files = list(stock_data_path.glob("*_intraday.csv"))
        print(f"📈 V1 Basic data: {len(csv_files)} stocks")
    else:
        print("❌ No V1 basic data found")
    
    # Check v2 data
    enhanced_data_path = Path("json_stock_data")
    if enhanced_data_path.exists():
        enhanced_files = list(enhanced_data_path.glob("*_comprehensive.json"))
        market_files = list(enhanced_data_path.glob("market_overview.json"))
        print(f"✅ V2 Enhanced data: {len(enhanced_files)} stocks")
        print(f"🌍 V2 Market data: {len(market_files)} files")
        
        # Check for JSON errors
        if enhanced_files:
            print("\n🔍 Checking JSON file integrity...")
            error_files = []
            for json_file in enhanced_files[:5]:  # Check first 5 files
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    error_files.append(json_file.name)
            
            if error_files:
                print(f"⚠️  Found {len(error_files)} files with JSON errors")
                print("💡 Use option 7 to repair JSON files")
            else:
                print("✅ All checked JSON files are valid")
    else:
        print("❌ No V2 enhanced data found")

def show_version_menu():
    """Show version selection menu"""
    print("\n" + "="*50)
    print("🔀 VERSION SELECTION")
    print("="*50)
    print("1. 📈 V1 - Basic Stock Scraper & API")
    print("   • Simple intraday data collection")
    print("   • Basic REST API endpoints")
    print("   • CSV data storage")
    print()
    print("2. 🚀 V2 - Enhanced Stock Scraper & API")
    print("   • Comprehensive data collection")
    print("   • Advanced REST API with screening")
    print("   • JSON data storage + market overview")
    print()
    print("3. 🔄 Back to Main Menu")
    print("="*50)
    
    choice = input("\nSelect version (1-3): ").strip()
    return choice

def show_v1_menu():
    """Show V1 system menu"""
    while True:
        print("\n" + "="*50)
        print("📈 V1 - BASIC STOCK SCRAPER & API")
        print("="*50)
        print("1. 📊 Run Basic Scraper (Intraday Data)")
        print("2. 🌐 Start Basic API Server")
        print("3. 📱 Run API Client Example")
        print("4. 📊 Check Data Status")
        print("5. 🔄 Run Full V1 System (Scraper + API)")
        print("6. 🔙 Back to Version Selection")
        print("="*50)
        
        choice = input("\nSelect an option (1-6): ").strip()
        
        if choice == "1":
            run_v1_scraper()
        elif choice == "2":
            run_v1_api_server()
        elif choice == "3":
            run_api_client()
        elif choice == "4":
            check_data_status()
        elif choice == "5":
            print("🔄 Running Full V1 System...")
            print("1️⃣  First, running basic scraper...")
            run_v1_scraper()
            print("\n2️⃣  Now starting API server...")
            print("⏳ Waiting 5 seconds for data to settle...")
            time.sleep(5)
            run_v1_api_server()
        elif choice == "6":
            break
        else:
            print("❌ Invalid option. Please choose 1-6.")
        
        input("\nPress Enter to continue...")

def show_v2_menu():
    """Show V2 system menu"""
    while True:
        print("\n" + "="*50)
        print("🚀 V2 - ENHANCED STOCK SCRAPER & API")
        print("="*50)
        print("1. 🚀 Run Enhanced Scraper (Comprehensive Data)")
        print("2. 🌐 Start Enhanced API Server")
        print("3. 📱 Run API Client Example")
        print("4. 📊 Check Data Status")
        print("5. 🔄 Run Full V2 System (Scraper + API)")
        print("6. 🔙 Back to Version Selection")
        print("="*50)
        
        choice = input("\nSelect an option (1-6): ").strip()
        
        if choice == "1":
            run_v2_scraper()
        elif choice == "2":
            run_v2_api_server()
        elif choice == "3":
            run_api_client()
        elif choice == "4":
            check_data_status()
        elif choice == "5":
            print("🔄 Running Full V2 System...")
            print("1️⃣  First, running enhanced scraper...")
            run_v2_scraper()
            print("\n2️⃣  Now starting API server...")
            print("⏳ Waiting 5 seconds for data to settle...")
            time.sleep(5)
            run_v2_api_server()
        elif choice == "6":
            break
        else:
            print("❌ Invalid option. Please choose 1-6.")
        
        input("\nPress Enter to continue...")

def show_menu():
    """Show the main menu"""
    while True:
        print("\n" + "="*50)
        print("📋 MAIN MENU")
        print("="*50)
        print("1. 🔀 Select Version & Run System")
        print("2. 📊 Check Data Status")
        print("3. 📱 Run API Client Example")
        print("4. 🔧 Repair JSON Files (Fix V2 API errors)")
        print("5. ❌ Exit")
        print("="*50)
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == "1":
            while True:
                version_choice = show_version_menu()
                if version_choice == "1":
                    show_v1_menu()
                    break
                elif version_choice == "2":
                    show_v2_menu()
                    break
                elif version_choice == "3":
                    break
                else:
                    print("❌ Invalid option. Please choose 1-3.")
        elif choice == "2":
            check_data_status()
        elif choice == "3":
            run_api_client()
        elif choice == "4":
            repair_json_files()
        elif choice == "5":
            print("👋 Goodbye! Happy trading! 📈💰")
            break
        else:
            print("❌ Invalid option. Please choose 1-5.")
        
        input("\nPress Enter to continue...")

def main():
    """Main function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Cannot start system without required dependencies.")
        return
    
    # Check if data directories exist
    os.makedirs("stock_data", exist_ok=True)
    os.makedirs("json_stock_data", exist_ok=True)
    
    # Show menu
    show_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  System startup interrupted by user")
    except Exception as e:
        print(f"\n\n❌ System startup failed with error: {e}")
        print("💡 Check the error message above and try again")
