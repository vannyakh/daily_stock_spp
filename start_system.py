#!/usr/bin/env python3
"""
Enhanced Stock Scraper System Startup Script

This script provides an easy way to start different components of the system.
"""

import os
import sys
import subprocess
import time
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

def run_enhanced_scraper():
    """Run the enhanced stock scraper"""
    print("🔄 Starting Enhanced Stock Scraper...")
    print("📊 This will collect comprehensive data for all stocks")
    print("⏱️  This may take several minutes depending on the number of stocks")
    
    try:
        subprocess.run([sys.executable, "enhanced_stock_scraper.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Scraper failed with error: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  Scraper interrupted by user")

def run_api_server():
    """Run the API server"""
    print("🌐 Starting Enhanced Stock Data API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, "stock_api_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ API server failed with error: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  API server stopped by user")

def run_api_client():
    """Run the API client example"""
    print("📱 Running API Client Example...")
    print("🔍 This will demonstrate all available API endpoints")
    
    try:
        subprocess.run([sys.executable, "api_client_example.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ API client failed with error: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  API client interrupted by user")

def run_basic_scraper():
    """Run the basic stock scraper"""
    print("📈 Starting Basic Stock Scraper...")
    print("📊 This will collect intraday data for all stocks")
    
    try:
        subprocess.run([sys.executable, "yf_scraper.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Basic scraper failed with error: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  Basic scraper interrupted by user")

def check_data_status():
    """Check the status of collected data"""
    print("📊 Checking Data Status...")
    
    enhanced_data_path = Path("json_stock_data")
    stock_data_path = Path("stock_data")
    
    if enhanced_data_path.exists():
        enhanced_files = list(enhanced_data_path.glob("*_comprehensive.json"))
        market_files = list(enhanced_data_path.glob("market_overview.json"))
        print(f"✅ Enhanced data: {len(enhanced_files)} stocks")
        print(f"🌍 Market data: {len(market_files)} files")
    else:
        print("❌ No enhanced data found")
    
    if stock_data_path.exists():
        csv_files = list(stock_data_path.glob("*_intraday.csv"))
        print(f"📈 Basic data: {len(csv_files)} stocks")
    else:
        print("❌ No basic data found")

def show_menu():
    """Show the main menu"""
    while True:
        print("\n" + "="*50)
        print("📋 MAIN MENU")
        print("="*50)
        print("1. 🚀 Run Enhanced Scraper (Comprehensive Data)")
        print("2. 📈 Run Basic Scraper (Intraday Data Only)")
        print("3. 🌐 Start API Server")
        print("4. 📱 Run API Client Example")
        print("5. 📊 Check Data Status")
        print("6. 🔄 Run Full System (Scraper + API)")
        print("7. ❌ Exit")
        print("="*50)
        
        choice = input("\nSelect an option (1-7): ").strip()
        
        if choice == "1":
            run_enhanced_scraper()
        elif choice == "2":
            run_basic_scraper()
        elif choice == "3":
            run_api_server()
        elif choice == "4":
            run_api_client()
        elif choice == "5":
            check_data_status()
        elif choice == "6":
            print("🔄 Running Full System...")
            print("1️⃣  First, running enhanced scraper...")
            run_enhanced_scraper()
            print("\n2️⃣  Now starting API server...")
            print("⏳ Waiting 5 seconds for data to settle...")
            time.sleep(5)
            run_api_server()
        elif choice == "7":
            print("👋 Goodbye! Happy trading! 📈💰")
            break
        else:
            print("❌ Invalid option. Please choose 1-7.")
        
        input("\nPress Enter to continue...")

def main():
    """Main function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Cannot start system without required dependencies.")
        return
    
    # Check if data directories exist
    os.makedirs("json_stock_data", exist_ok=True)
    os.makedirs("stock_data", exist_ok=True)
    
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
