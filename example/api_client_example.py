#!/usr/bin/env python3
"""
Enhanced Stock Data API Client Example

This script demonstrates how to use the Enhanced Stock Data API
to access comprehensive stock market data collected using yfinance components.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class EnhancedStockAPIClient:
    """Client for the Enhanced Stock Data API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'EnhancedStockAPIClient/2.0.0'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return {"error": str(e)}
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information and available endpoints"""
        return self._make_request("GET", "/")
    
    def get_all_stocks(self) -> List[Dict[str, Any]]:
        """Get list of all available stocks"""
        return self._make_request("GET", "/api/v1/stocks")
    
    def get_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive data for a specific stock"""
        return self._make_request("GET", f"/api/v1/stocks/{ticker}")
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive market overview"""
        return self._make_request("GET", "/api/v1/market/overview")
    
    def get_sector_performance(self) -> Dict[str, Any]:
        """Get sector performance data"""
        return self._make_request("GET", "/api/v1/market/sectors")
    
    def get_market_indices(self) -> Dict[str, Any]:
        """Get major market indices data"""
        return self._make_request("GET", "/api/v1/market/indices")
    
    def get_global_markets(self) -> Dict[str, Any]:
        """Get global market data"""
        return self._make_request("GET", "/api/v1/market/global")
    
    def search_stocks(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for stocks based on query"""
        data = {"query": query, "limit": limit}
        return self._make_request("POST", "/api/v1/stocks/search", json=data)
    
    def screen_stocks(self, **criteria) -> Dict[str, Any]:
        """Screen stocks based on criteria"""
        return self._make_request("POST", "/api/v1/stocks/screener", json=criteria)
    
    def get_stock_financials(self, ticker: str) -> Dict[str, Any]:
        """Get financial statements for a specific stock"""
        return self._make_request("GET", f"/api/v1/stocks/{ticker}/financials")
    
    def get_stock_news(self, ticker: str) -> Dict[str, Any]:
        """Get news and recommendations for a specific stock"""
        return self._make_request("GET", f"/api/v1/stocks/{ticker}/news")
    
    def get_stock_options(self, ticker: str) -> Dict[str, Any]:
        """Get options data for a specific stock"""
        return self._make_request("GET", f"/api/v1/stocks/{ticker}/options")
    
    def get_api_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return self._make_request("GET", "/api/v1/stats")
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return self._make_request("GET", "/api/v1/health")

def print_section_header(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_stock_summary(stock: Dict[str, Any]):
    """Print a formatted stock summary"""
    print(f"📈 {stock['ticker']}: {stock['status']}")
    print(f"   📊 Data points: {stock['data_points']}")
    print(f"   🕒 Last updated: {stock['timestamp']}")
    print(f"   💬 {stock['message']}")

def print_market_data(market_data: Dict[str, Any], title: str):
    """Print formatted market data"""
    print(f"\n🌍 {title}")
    print(f"{'─'*40}")
    
    if 'error' in market_data:
        print(f"❌ Error: {market_data['error']}")
        return
    
    for key, value in market_data.items():
        if isinstance(value, dict):
            print(f"\n📊 {key.replace('_', ' ').title()}:")
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, dict) and 'error' not in sub_value:
                    print(f"   {sub_key}: {sub_value}")
                elif 'error' not in str(sub_value):
                    print(f"   {sub_key}: {sub_value}")

def main():
    """Main demonstration function"""
    print("🚀 Enhanced Stock Data API Client Demo")
    print("=" * 50)
    
    # Initialize client
    client = EnhancedStockAPIClient()
    
    # Check API health
    print_section_header("API Health Check")
    health = client.health_check()
    if 'error' not in health:
        print(f"✅ API Status: {health['status']}")
        print(f"🕒 Timestamp: {health['timestamp']}")
        print(f"📦 Version: {health['version']}")
    else:
        print("❌ API is not accessible. Make sure the server is running.")
        return
    
    # Get API information
    print_section_header("API Information")
    api_info = client.get_api_info()
    if 'error' not in api_info:
        print(f"📋 {api_info['message']}")
        print(f"🔢 Version: {api_info['version']}")
        print(f"📝 Description: {api_info['description']}")
        print("\n📡 Available Endpoints:")
        for name, endpoint in api_info['endpoints'].items():
            print(f"   • {name}: {endpoint}")
    
    # Get API statistics
    print_section_header("API Statistics")
    stats = client.get_api_stats()
    if 'error' not in stats:
        print(f"📊 Enhanced stocks: {stats['enhanced_stocks']}")
        print(f"📈 Basic stocks: {stats['basic_stocks']}")
        print(f"🌍 Market data: {stats['market_data']}")
        print(f"🔢 Total data sources: {stats['total_data_sources']}")
    
    # Get all available stocks
    print_section_header("Available Stocks")
    stocks = client.get_all_stocks()
    if 'error' not in stocks:
        print(f"📋 Found {len(stocks)} stocks:")
        for stock in stocks[:10]:  # Show first 10
            print_stock_summary(stock)
        if len(stocks) > 10:
            print(f"   ... and {len(stocks) - 10} more stocks")
    
    # Get market overview
    print_section_header("Market Overview")
    market_overview = client.get_market_overview()
    if 'error' not in market_overview:
        print_market_data(market_overview['indices'], "Market Indices")
        print_market_data(market_overview['sectors'], "Sector Performance")
        print_market_data(market_overview['global'], "Global Markets")
    
    # Get sector performance
    print_section_header("Sector Performance")
    sectors = client.get_sector_performance()
    if 'error' not in sectors:
        print(f"📊 Total sectors: {sectors['total_sectors']}")
        for sector_name, sector_data in sectors['sectors'].items():
            if isinstance(sector_data, dict) and 'error' not in sector_data:
                change_pct = sector_data.get('change_pct', 0)
                emoji = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
                print(f"{emoji} {sector_name}: {change_pct:.2f}%")
    
    # Search for stocks
    print_section_header("Stock Search Example")
    search_results = client.search_stocks("AI", limit=5)
    if 'error' not in search_results:
        print(f"🔍 Search query: '{search_results['query']}'")
        print(f"📊 Found: {search_results['total_found']} stocks")
        for result in search_results['results']:
            print(f"   • {result['ticker']} ({result['name']})")
            print(f"     Sector: {result['sector']}")
            print(f"     Industry: {result['industry']}")
    
    # Stock screening example
    print_section_header("Stock Screening Example")
    screen_results = client.screen_stocks(
        sector="Technology",
        market_cap_min=1000000000,  # $1B minimum
        limit=5
    )
    if 'error' not in screen_results:
        print(f"🔍 Screening criteria: {screen_results['criteria']}")
        print(f"📊 Found: {screen_results['total_found']} stocks")
        for result in screen_results['results']:
            print(f"   • {result['ticker']} ({result['name']})")
            print(f"     Market Cap: ${result['market_cap']:,}" if result['market_cap'] else "     Market Cap: N/A")
            print(f"     P/E Ratio: {result['pe_ratio']:.2f}" if result['pe_ratio'] else "     P/E Ratio: N/A")
    
    # Get detailed data for a specific stock (if available)
    print_section_header("Detailed Stock Data Example")
    if 'error' not in stocks and len(stocks) > 0:
        sample_ticker = stocks[0]['ticker']
        print(f"📊 Getting detailed data for {sample_ticker}...")
        
        stock_data = client.get_stock_data(sample_ticker)
        if 'error' not in stock_data:
            print(f"✅ Data type: {stock_data['data_type']}")
            print(f"📊 Source: {stock_data['source']}")
            
            if stock_data['data_type'] == 'comprehensive':
                data = stock_data['data']
                print(f"📈 Stock info: {len(data.get('stock_info', {}))} fields")
                print(f"💰 Financials: {len(data.get('financials', {}))} statements")
                print(f"📰 News: {len(data.get('news_data', {}))} sources")
                print(f"📊 Options: {len(data.get('options_data', {}))} data points")
                print(f"👥 Holders: {len(data.get('holders_data', {}))} categories")
                print(f"📅 Earnings: {len(data.get('earnings_data', {}))} data points")
    
    print_section_header("Demo Complete")
    print("🎉 Successfully demonstrated the Enhanced Stock Data API!")
    print("📚 Check the API documentation at http://localhost:8000/docs")
    print("🔧 Use the client methods to integrate with your applications")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        print("💡 Make sure the API server is running at http://localhost:8000")
