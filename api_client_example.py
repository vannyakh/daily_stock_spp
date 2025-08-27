#!/usr/bin/env python3
"""
Stock Data API Client Example
Demonstrates how to use the Stock Data API endpoints
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class StockDataAPIClient:
    """Client for the Stock Data API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_api_info(self) -> Dict:
        """Get API information"""
        response = self.session.get(f"{self.base_url}/")
        return response.json()
    
    def get_health(self) -> Dict:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/api/health")
        return response.json()
    
    def get_stocks(self, limit: Optional[int] = None, offset: int = 0) -> Dict:
        """Get list of available stocks"""
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        
        response = self.session.get(f"{self.base_url}/api/stocks", params=params)
        return response.json()
    
    def get_stock_data(self, ticker: str, limit: int = 100, 
                       start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> Dict:
        """Get stock data for a specific ticker"""
        params = {'limit': limit}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        response = self.session.get(f"{self.base_url}/api/stocks/{ticker}", params=params)
        return response.json()
    
    def get_stock_summary(self, ticker: str) -> Dict:
        """Get summary statistics for a stock"""
        response = self.session.get(f"{self.base_url}/api/stocks/{ticker}/summary")
        return response.json()
    
    def get_latest_price(self, ticker: str) -> Dict:
        """Get the latest price for a stock"""
        response = self.session.get(f"{self.base_url}/api/stocks/{ticker}/latest")
        return response.json()
    
    def search_stocks(self, query: str, limit: int = 10) -> Dict:
        """Search for stocks"""
        params = {'query': query, 'limit': limit}
        response = self.session.get(f"{self.base_url}/api/search", params=params)
        return response.json()
    
    def get_api_stats(self) -> Dict:
        """Get API statistics"""
        response = self.session.get(f"{self.base_url}/api/stats")
        return response.json()

def print_response(title: str, response: Dict):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print(f"{'='*60}")
    
    if response.get('success'):
        print(f"✅ {response.get('message', 'Success')}")
        if 'data' in response:
            print(f"📈 Data: {json.dumps(response['data'], indent=2)}")
        if 'count' in response and response['count'] is not None:
            print(f"🔢 Count: {response['count']}")
    else:
        print(f"❌ {response.get('message', 'Error')}")
        if 'data' in response:
            print(f"🚨 Error Details: {json.dumps(response['data'], indent=2)}")
    
    print(f"⏰ Timestamp: {response.get('timestamp', 'N/A')}")

def main():
    """Main function demonstrating API usage"""
    print("🚀 Stock Data API Client Example")
    print("=" * 60)
    
    # Initialize client
    client = StockDataAPIClient()
    
    try:
        # Test API health
        print_response("API Health Check", client.get_health())
        
        # Get API info
        print_response("API Information", client.get_api_info())
        
        # Get available stocks
        print_response("Available Stocks (First 10)", client.get_stocks(limit=10))
        
        # Get stock summary for AAPL
        print_response("AAPL Stock Summary", client.get_stock_summary("aapl"))
        
        # Get latest price for AAPL
        print_response("AAPL Latest Price", client.get_latest_price("aapl"))
        
        # Get recent stock data for AAPL
        print_response("AAPL Recent Data (Last 3 points)", client.get_stock_data("aapl", limit=3))
        
        # Search for stocks
        print_response("Search for 'MSFT'", client.search_stocks("msft"))
        
        # Get API statistics
        print_response("API Statistics", client.get_api_stats())
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("💡 Make sure the server is running at http://localhost:8000")
        print("🚀 Start it with: python3 stock_api.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
