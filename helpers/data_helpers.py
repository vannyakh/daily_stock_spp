"""
Data Processing Helpers
Utilities for processing, cleaning, and analyzing stock data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """Main data processing utility class"""
    
    @staticmethod
    def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize stock data"""
        try:
            if df.empty:
                return df
            
            # Remove rows with all NaN values
            df = df.dropna(how='all')
            
            # Convert date columns to datetime
            date_columns = ['Date', 'date', 'timestamp', 'time']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Convert numeric columns
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Sort by date if available
            if 'Date' in df.columns:
                df = df.sort_values('Date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning stock data: {e}")
            return df
    
    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate common technical indicators"""
        try:
            if df.empty or 'Close' not in df.columns:
                return df
            
            # Moving averages
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['EMA_12'] = df['Close'].ewm(span=12).mean()
            df['EMA_26'] = df['Close'].ewm(span=26).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            
            # Bollinger Bands
            df['BB_Middle'] = df['Close'].rolling(window=20).mean()
            bb_std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return df
    
    @staticmethod
    def resample_data(df: pd.DataFrame, period: str = '1D') -> pd.DataFrame:
        """Resample data to different time periods"""
        try:
            if df.empty or 'Date' not in df.columns:
                return df
            
            # Set date as index
            df = df.set_index('Date')
            
            # Resample
            resampled = df.resample(period).agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum',
                'Adj Close': 'last'
            })
            
            # Reset index
            resampled = resampled.reset_index()
            
            return resampled
            
        except Exception as e:
            logger.error(f"Error resampling data: {e}")
            return df
    
    @staticmethod
    def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate various return metrics"""
        try:
            if df.empty or 'Close' not in df.columns:
                return df
            
            # Daily returns
            df['Daily_Return'] = df['Close'].pct_change()
            
            # Cumulative returns
            df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod()
            
            # Log returns
            df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
            
            # Volatility (rolling 20-day)
            df['Volatility'] = df['Daily_Return'].rolling(window=20).std() * np.sqrt(252)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating returns: {e}")
            return df

class StockDataHelper:
    """Helper class for stock-specific data operations"""
    
    @staticmethod
    def validate_stock_data(data: Dict) -> bool:
        """Validate stock data structure"""
        required_fields = ['ticker', 'data']
        
        if not isinstance(data, dict):
            return False
        
        for field in required_fields:
            if field not in data:
                return False
        
        return True
    
    @staticmethod
    def extract_stock_info(data: Dict) -> Dict:
        """Extract key stock information"""
        try:
            info = {
                'ticker': data.get('ticker', ''),
                'company_name': data.get('info', {}).get('longName', ''),
                'sector': data.get('info', {}).get('sector', ''),
                'industry': data.get('info', {}).get('industry', ''),
                'market_cap': data.get('info', {}).get('marketCap', 0),
                'pe_ratio': data.get('info', {}).get('trailingPE', 0),
                'dividend_yield': data.get('info', {}).get('dividendYield', 0),
                'beta': data.get('info', {}).get('beta', 0)
            }
            return info
        except Exception as e:
            logger.error(f"Error extracting stock info: {e}")
            return {}
    
    @staticmethod
    def calculate_stock_metrics(df: pd.DataFrame) -> Dict:
        """Calculate comprehensive stock metrics"""
        try:
            if df.empty or 'Close' not in df.columns:
                return {}
            
            metrics = {
                'current_price': df['Close'].iloc[-1],
                'price_change': df['Close'].iloc[-1] - df['Close'].iloc[-2] if len(df) > 1 else 0,
                'price_change_pct': ((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100 if len(df) > 1 else 0,
                'high_52w': df['High'].max(),
                'low_52w': df['Low'].min(),
                'avg_volume': df['Volume'].mean(),
                'volatility': df['Close'].pct_change().std() * np.sqrt(252),
                'sharpe_ratio': (df['Close'].pct_change().mean() * 252) / (df['Close'].pct_change().std() * np.sqrt(252)) if df['Close'].pct_change().std() > 0 else 0
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating stock metrics: {e}")
            return {}

class MarketDataHelper:
    """Helper class for market-wide data operations"""
    
    @staticmethod
    def aggregate_market_data(stocks_data: List[Dict]) -> Dict:
        """Aggregate data from multiple stocks"""
        try:
            if not stocks_data:
                return {}
            
            market_summary = {
                'total_stocks': len(stocks_data),
                'market_cap_total': sum(stock.get('info', {}).get('marketCap', 0) for stock in stocks_data),
                'sectors': {},
                'avg_pe_ratio': 0,
                'avg_dividend_yield': 0
            }
            
            # Calculate sector distribution
            for stock in stocks_data:
                sector = stock.get('info', {}).get('sector', 'Unknown')
                if sector not in market_summary['sectors']:
                    market_summary['sectors'][sector] = 0
                market_summary['sectors'][sector] += 1
            
            # Calculate averages
            pe_ratios = [stock.get('info', {}).get('trailingPE', 0) for stock in stocks_data if stock.get('info', {}).get('trailingPE', 0) > 0]
            dividend_yields = [stock.get('info', {}).get('dividendYield', 0) for stock in stocks_data if stock.get('info', {}).get('dividendYield', 0) > 0]
            
            if pe_ratios:
                market_summary['avg_pe_ratio'] = sum(pe_ratios) / len(pe_ratios)
            if dividend_yields:
                market_summary['avg_dividend_yield'] = sum(dividend_yields) / len(dividend_yields)
            
            return market_summary
            
        except Exception as e:
            logger.error(f"Error aggregating market data: {e}")
            return {}
    
    @staticmethod
    def detect_market_trends(stocks_data: List[Dict], days: int = 30) -> Dict:
        """Detect market-wide trends"""
        try:
            if not stocks_data:
                return {}
            
            trends = {
                'advancing': 0,
                'declining': 0,
                'unchanged': 0,
                'strongest_sectors': [],
                'weakest_sectors': {}
            }
            
            sector_performance = {}
            
            for stock in stocks_data:
                ticker = stock.get('ticker', '')
                if 'intraday_data' in stock and stock['intraday_data']:
                    # Get recent price data
                    recent_data = stock['intraday_data'][-days:] if len(stock['intraday_data']) >= days else stock['intraday_data']
                    
                    if len(recent_data) >= 2:
                        start_price = recent_data[0].get('Close', 0)
                        end_price = recent_data[-1].get('Close', 0)
                        
                        if end_price > start_price:
                            trends['advancing'] += 1
                        elif end_price < start_price:
                            trends['declining'] += 1
                        else:
                            trends['unchanged'] += 1
                        
                        # Track sector performance
                        sector = stock.get('info', {}).get('sector', 'Unknown')
                        if sector not in sector_performance:
                            sector_performance[sector] = {'gains': 0, 'losses': 0, 'total': 0}
                        
                        sector_performance[sector]['total'] += 1
                        if end_price > start_price:
                            sector_performance[sector]['gains'] += 1
                        else:
                            sector_performance[sector]['losses'] += 1
            
            # Calculate sector strength
            for sector, data in sector_performance.items():
                if data['total'] > 0:
                    win_rate = data['gains'] / data['total']
                    sector_performance[sector]['win_rate'] = win_rate
            
            # Sort sectors by performance
            sorted_sectors = sorted(sector_performance.items(), key=lambda x: x[1].get('win_rate', 0), reverse=True)
            trends['strongest_sectors'] = [sector for sector, _ in sorted_sectors[:5]]
            trends['weakest_sectors'] = {sector: data for sector, data in sorted_sectors[-5:]}
            
            return trends
            
        except Exception as e:
            logger.error(f"Error detecting market trends: {e}")
            return {}

# Utility functions
def merge_stock_data(data_list: List[Dict]) -> pd.DataFrame:
    """Merge multiple stock datasets into one DataFrame"""
    try:
        if not data_list:
            return pd.DataFrame()
        
        merged_data = []
        for stock_data in data_list:
            if 'intraday_data' in stock_data and stock_data['intraday_data']:
                df = pd.DataFrame(stock_data['intraday_data'])
                df['ticker'] = stock_data.get('ticker', '')
                merged_data.append(df)
        
        if merged_data:
            return pd.concat(merged_data, ignore_index=True)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Error merging stock data: {e}")
        return pd.DataFrame()

def calculate_correlation_matrix(stocks_data: List[Dict]) -> pd.DataFrame:
    """Calculate correlation matrix between stocks"""
    try:
        if not stocks_data:
            return pd.DataFrame()
        
        # Extract closing prices for each stock
        price_data = {}
        for stock in stocks_data:
            ticker = stock.get('ticker', '')
            if 'intraday_data' in stock and stock['intraday_data']:
                prices = [day.get('Close', 0) for day in stock['intraday_data']]
                if prices:
                    price_data[ticker] = prices
        
        if not price_data:
            return pd.DataFrame()
        
        # Create DataFrame and calculate correlations
        df = pd.DataFrame(price_data)
        return df.corr()
        
    except Exception as e:
        logger.error(f"Error calculating correlation matrix: {e}")
        return pd.DataFrame()
