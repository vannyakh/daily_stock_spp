import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Dict, Optional, Any
import logging
from colorama import init, Fore, Back, Style
import json

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Configure logging with colors
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT
    }
    
    def format(self, record):
        # Add color to the log level
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{Style.RESET_ALL}"
        
        # Add color to specific messages
        if '✅' in record.msg:
            record.msg = f"{Fore.GREEN}{record.msg}{Style.RESET_ALL}"
        elif '❌' in record.msg:
            record.msg = f"{Fore.RED}{record.msg}{Style.RESET_ALL}"
        elif '⚠️' in record.msg:
            record.msg = f"{Fore.YELLOW}{record.msg}{Style.RESET_ALL}"
        
        return super().format(record)


# Configure logging with colored output to dir logs/*

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("logs", "enhanced_scraper.log")),
        logging.StreamHandler()
    ]
)

# Apply colored formatter to console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)
logger.handlers = []  # Clear existing handlers
logger.addHandler(logging.FileHandler(os.path.join("logs", "enhanced_scraper.log")))
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

class StockDataWorker:
    """Enhanced worker class for fetching comprehensive stock data using yfinance components"""
    
    def __init__(self, ticker: str, folder_path: str, max_data_size: int = None):
        self.ticker = ticker
        self.folder_path = folder_path
        self.max_data_size = max_data_size
        self.lock = threading.Lock()
        self.ticker_obj = yf.Ticker(ticker)
    
    def fetch_comprehensive_stock_data(self, start_date: datetime, end_date: datetime) -> Dict:
        """Fetch comprehensive data for a single stock using multiple yfinance components"""
        try:
            logger.info(f"{Fore.CYAN}🔄 Fetching comprehensive data for {self.ticker}...{Style.RESET_ALL}")
            
            # Add small delay to avoid rate limiting
            time.sleep(0.1)
            
            # 1. Basic market data (intraday)
            intraday_data = self._fetch_intraday_data(start_date, end_date)
            
            # 2. Stock information and fundamentals
            stock_info = self._fetch_stock_info()
            
            # 3. Financial statements
            financials = self._fetch_financials()
            
            # 4. Options data
            options_data = self._fetch_options_data()
            
            # 5. News and recommendations
            news_data = self._fetch_news_data()
            
            # 6. Institutional holders and major holders
            holders_data = self._fetch_holders_data()
            
            # 7. Earnings and calendar
            earnings_data = self._fetch_earnings_data()
            
            # Combine all data
            comprehensive_data = {
                'ticker': self.ticker,
                'timestamp': datetime.now().isoformat(),
                'intraday_data': intraday_data,
                'stock_info': stock_info,
                'financials': financials,
                'options_data': options_data,
                'news_data': news_data,
                'holders_data': holders_data,
                'earnings_data': earnings_data
            }
            
            # Save to JSON file
            success = self._save_to_json(comprehensive_data)
            
            if success:
                return {
                    'ticker': self.ticker,
                    'status': 'success',
                    'data_points': len(comprehensive_data),
                    'message': f'Successfully updated {self.ticker} comprehensive data'
                }
            else:
                return {
                    'ticker': self.ticker,
                    'status': 'save_error',
                    'message': f'Failed to save comprehensive data for {self.ticker}'
                }
                
        except Exception as e:
            logger.error(f"{Fore.RED}❌ Error fetching comprehensive data for {self.ticker}: {str(e)}{Style.RESET_ALL}")
            return {
                'ticker': self.ticker,
                'status': 'error',
                'message': str(e)
            }
    
    def _fetch_intraday_data(self, start_date: datetime, end_date: datetime) -> Dict:
        """Fetch intraday market data"""
        try:
            data = yf.download(
                self.ticker,
                interval='1m',
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                progress=False
            )
            
            if data.empty:
                return {'status': 'no_data', 'message': 'No intraday data available'}
            
            # Process the data
            processed_data = self._process_intraday_data(data)
            return {
                'status': 'success',
                'rows': len(processed_data),
                'data': processed_data.to_dict('records')  # Full data, not truncated
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _fetch_stock_info(self) -> Dict:
        """Fetch basic stock information"""
        try:
            info = self.ticker_obj.info
            if info:
                # Filter out None values and large objects
                filtered_info = {k: v for k, v in info.items() if v is not None and not isinstance(v, (dict, list))}
                return {'status': 'success', 'data': filtered_info}
            else:
                return {'status': 'no_data', 'message': 'No stock info available'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _fetch_financials(self) -> Dict:
        """Fetch financial statements"""
        try:
            financials = {}
            
            # Income statement
            try:
                income_stmt = self.ticker_obj.income_stmt
                if not income_stmt.empty:
                    financials['income_statement'] = {
                        'status': 'success',
                        'rows': len(income_stmt),
                        'columns': list(income_stmt.columns),
                        'data': income_stmt.to_dict('records')  # Full data, not truncated
                    }
                else:
                    financials['income_statement'] = {'status': 'no_data'}
            except Exception as e:
                financials['income_statement'] = {'status': 'error', 'message': str(e)}
            
            # Balance sheet
            try:
                balance_sheet = self.ticker_obj.balance_sheet
                if not balance_sheet.empty:
                    financials['balance_sheet'] = {
                        'status': 'success',
                        'rows': len(balance_sheet),
                        'columns': list(balance_sheet.columns),
                        'data': balance_sheet.to_dict('records')  # Full data, not truncated
                    }
                else:
                    financials['balance_sheet'] = {'status': 'no_data'}
            except Exception as e:
                financials['balance_sheet'] = {'status': 'error', 'message': str(e)}
            
            # Cash flow
            try:
                cash_flow = self.ticker_obj.cashflow
                if not cash_flow.empty:
                    financials['cash_flow'] = {
                        'status': 'success',
                        'rows': len(cash_flow),
                        'columns': list(cash_flow.columns),
                        'data': cash_flow.to_dict('records')  # Full data, not truncated
                    }
                else:
                    financials['cash_flow'] = {'status': 'no_data'}
            except Exception as e:
                financials['cash_flow'] = {'status': 'error', 'message': str(e)}
            
            return financials
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _fetch_options_data(self) -> Dict:
        """Fetch options data"""
        try:
            options = {}
            
            # Get available expiration dates
            try:
                expirations = self.ticker_obj.options
                if expirations:
                    options['expirations'] = expirations  # All expiration dates, not truncated
                    
                    # Get options for first few expirations (to avoid overwhelming data)
                    if expirations:
                        # Get options for first 3 expirations
                        for i, exp in enumerate(expirations[:3]):
                            try:
                                option_chain = self.ticker_obj.option_chain(exp)
                                calls = option_chain.calls
                                puts = option_chain.puts
                                
                                options[f'expiration_{exp}'] = {
                                    'calls_count': len(calls),
                                    'puts_count': len(puts),
                                    'calls': calls.to_dict('records') if len(calls) <= 100 else calls.head(100).to_dict('records'),
                                    'puts': puts.to_dict('records') if len(puts) <= 100 else puts.head(100).to_dict('records')
                                }
                            except Exception as e:
                                options[f'expiration_{exp}'] = {'error': str(e)}
                else:
                    options['expirations'] = []
            except Exception as e:
                options['status'] = 'error'
                options['error_message'] = str(e)
            
            return options
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _fetch_news_data(self) -> Dict:
        """Fetch news and recommendations"""
        try:
            news_data = {}
            
            # News
            try:
                news = self.ticker_obj.news
                if news:
                    news_data['news'] = {
                        'status': 'success',
                        'count': len(news),
                        'data': news  # Full news data, not truncated
                    }
                else:
                    news_data['news'] = {'status': 'no_data'}
            except Exception as e:
                news_data['news'] = {'status': 'error', 'message': str(e)}
            
            # Recommendations
            try:
                recommendations = self.ticker_obj.recommendations
                if not recommendations.empty:
                    news_data['recommendations'] = {
                        'status': 'success',
                        'rows': len(recommendations),
                        'data': recommendations.to_dict('records')  # Full data, not truncated
                    }
                else:
                    news_data['recommendations'] = {'status': 'no_data'}
            except Exception as e:
                news_data['recommendations'] = {'status': 'error', 'message': str(e)}
            
            return news_data
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _fetch_holders_data(self) -> Dict:
        """Fetch institutional and major holders"""
        try:
            holders_data = {}
            
            # Major holders
            try:
                major_holders = self.ticker_obj.major_holders
                if not major_holders.empty:
                    holders_data['major_holders'] = {
                        'status': 'success',
                        'data': major_holders.to_dict('records')
                    }
                else:
                    holders_data['major_holders'] = {'status': 'no_data'}
            except:
                holders_data['major_holders'] = {'status': 'error'}
            
            # Institutional holders
            try:
                institutional_holders = self.ticker_obj.institutional_holders
                if not institutional_holders.empty:
                    holders_data['institutional_holders'] = {
                        'status': 'success',
                        'data': institutional_holders.to_dict('records')
                    }
                else:
                    holders_data['institutional_holders'] = {'status': 'no_data'}
            except:
                holders_data['institutional_holders'] = {'status': 'error'}
            
            return holders_data
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _fetch_earnings_data(self) -> Dict:
        """Fetch earnings and calendar data"""
        try:
            earnings_data = {}
            
            # Earnings
            try:
                earnings = self.ticker_obj.earnings
                if not earnings.empty:
                    earnings_data['earnings'] = {
                        'status': 'success',
                        'rows': len(earnings),
                        'data': earnings.to_dict('records')  # Full data, not truncated
                    }
                else:
                    earnings_data['earnings'] = {'status': 'no_data'}
            except Exception as e:
                earnings_data['earnings'] = {'status': 'error', 'message': str(e)}
            
            # Calendar
            try:
                calendar = self.ticker_obj.calendar
                if not calendar.empty:
                    earnings_data['calendar'] = {
                        'status': 'success',
                        'data': calendar.to_dict('records')
                    }
                else:
                    earnings_data['calendar'] = {'status': 'no_data'}
            except Exception as e:
                earnings_data['calendar'] = {'status': 'error', 'message': str(e)}
            
            return earnings_data
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _process_intraday_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process and clean the downloaded intraday data"""
        if isinstance(data.columns, pd.MultiIndex):
            # Flatten the multi-level columns
            data.columns = [' '.join(col).strip() for col in data.columns.values]
            
            # Rename the columns to match the desired format
            data = data.rename(columns={
                f'Open {self.ticker}': 'Open',
                f'High {self.ticker}': 'High',
                f'Low {self.ticker}': 'Low',
                f'Close {self.ticker}': 'Close',
                f'Adj Close {self.ticker}': 'Adj Close',
                f'Volume {self.ticker}': 'Volume'
            })
        
        # Clean up any NaN values
        data = data.dropna()
        
        # Apply data size limit if specified
        if self.max_data_size and len(data) > self.max_data_size:
            logger.info(f"{Fore.YELLOW}⚠️ {self.ticker}: Limiting intraday data to {self.max_data_size} rows from {len(data)} available{Style.RESET_ALL}")
            data = data.tail(self.max_data_size)  # Keep most recent data
        
        return data
    
    def _save_to_json(self, data: Dict) -> bool:
        """Save comprehensive data to JSON file with thread-safe operations"""
        try:
            file_path = os.path.join(self.folder_path, f"{self.ticker.lower()}_comprehensive.json")
            
            with self.lock:
                # Save the comprehensive data to JSON file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                
            logger.info(f"{Fore.GREEN}✅ Updated {file_path} with comprehensive data.{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            logger.error(f"{Fore.RED}❌ Error saving comprehensive data for {self.ticker}: {str(e)}{Style.RESET_ALL}")
            return False

class MarketDataCollector:
    """Collect market-wide data using yfinance Market and Search components"""
    
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
    
    def collect_market_data(self) -> Dict:
        """Collect comprehensive market data"""
        try:
            logger.info(f"{Fore.BLUE}🌍 Collecting market-wide data...{Style.RESET_ALL}")
            
            market_data = {}
            
            # 1. Market indices
            market_data['indices'] = self._collect_market_indices()
            
            # 2. Sector performance
            market_data['sectors'] = self._collect_sector_data()
            
            # 3. Market search results for trending stocks
            market_data['trending'] = self._collect_trending_stocks()
            
            # 4. Global market overview
            market_data['global'] = self._collect_global_markets()
            
            # Save market data
            self._save_market_data(market_data)
            
            return market_data
            
        except Exception as e:
            logger.error(f"{Fore.RED}❌ Error collecting market data: {str(e)}{Style.RESET_ALL}")
            return {'status': 'error', 'message': str(e)}
    
    def _collect_market_indices(self) -> Dict:
        """Collect major market indices data"""
        try:
            indices = ['^GSPC', '^DJI', '^IXIC', '^RUT', '^VIX']  # S&P 500, Dow, NASDAQ, Russell 2000, VIX
            indices_data = {}
            
            for index in indices:
                try:
                    ticker = yf.Ticker(index)
                    info = ticker.info
                    hist = ticker.history(period='5d')
                    
                    indices_data[index] = {
                        'name': info.get('longName', index),
                        'current_price': hist['Close'].iloc[-1] if not hist.empty else None,
                        'change_5d': hist['Close'].iloc[-1] - hist['Close'].iloc[0] if len(hist) > 1 else None,
                        'volume': hist['Volume'].iloc[-1] if not hist.empty else None
                    }
                except Exception as e:
                    indices_data[index] = {'error': str(e)}
            
            return indices_data
        except Exception as e:
            return {'error': str(e)}
    
    def _collect_sector_data(self) -> Dict:
        """Collect sector performance data"""
        try:
            # Major sector ETFs
            sector_etfs = {
                'XLK': 'Technology',
                'XLF': 'Financials',
                'XLE': 'Energy',
                'XLV': 'Healthcare',
                'XLI': 'Industrials',
                'XLP': 'Consumer Staples',
                'XLY': 'Consumer Discretionary',
                'XLB': 'Materials',
                'XLU': 'Utilities',
                'XLRE': 'Real Estate'
            }
            
            sector_data = {}
            
            for etf, sector_name in sector_etfs.items():
                try:
                    ticker = yf.Ticker(etf)
                    hist = ticker.history(period='5d')
                    
                    if not hist.empty:
                        sector_data[sector_name] = {
                            'etf': etf,
                            'current_price': hist['Close'].iloc[-1],
                            'change_5d': hist['Close'].iloc[-1] - hist['Close'].iloc[0],
                            'change_pct': ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                        }
                except Exception as e:
                    sector_data[sector_name] = {'error': str(e)}
            
            return sector_data
        except Exception as e:
            return {'error': str(e)}
    
    def _collect_trending_stocks(self) -> Dict:
        """Collect trending stocks using search functionality"""
        try:
            # Search for popular stocks
            search_terms = ['AI', 'EV', 'Tech', 'Biotech', 'Crypto']
            trending_data = {}
            
            for term in search_terms:
                try:
                    # Use yfinance search functionality
                    search_results = yf.Tickers(term)
                    if hasattr(search_results, 'tickers'):
                        trending_data[term] = {
                            'status': 'success',
                            'count': len(search_results.tickers)
                        }
                    else:
                        trending_data[term] = {'status': 'no_results'}
                except Exception as e:
                    trending_data[term] = {'error': str(e)}
            
            return trending_data
        except Exception as e:
            return {'error': str(e)}
    
    def _collect_global_markets(self) -> Dict:
        """Collect global market data"""
        try:
            global_markets = {
                '^FTSE': 'FTSE 100 (UK)',
                '^GDAXI': 'DAX (Germany)',
                '^FCHI': 'CAC 40 (France)',
                '^N225': 'Nikkei 225 (Japan)',
                '^HSI': 'Hang Seng (Hong Kong)',
                '^BSESN': 'BSE SENSEX (India)'
            }
            
            global_data = {}
            
            for market, name in global_markets.items():
                try:
                    ticker = yf.Ticker(market)
                    hist = ticker.history(period='5d')
                    
                    if not hist.empty:
                        global_data[name] = {
                            'symbol': market,
                            'current_price': hist['Close'].iloc[-1],
                            'change_5d': hist['Close'].iloc[-1] - hist['Close'].iloc[0],
                            'change_pct': ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                        }
                except Exception as e:
                    global_data[name] = {'error': str(e)}
            
            return global_data
        except Exception as e:
            return {'error': str(e)}
    
    def _save_market_data(self, market_data: Dict):
        """Save market data to JSON file"""
        try:
            file_path = os.path.join(self.folder_path, "market_overview.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(market_data, f, indent=2, default=str)
            
            logger.info(f"{Fore.GREEN}✅ Saved market overview to {file_path}{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"{Fore.RED}❌ Error saving market data: {str(e)}{Style.RESET_ALL}")

def print_banner():
    """Print a colorful banner for the enhanced scraper"""
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}
╔══════════════════════════════════════════════════════════════╗
║                🚀 ENHANCED STOCK DATA SCRAPER 🚀              ║
║              Comprehensive yfinance Integration               ║
║              Ticker • Tickers • Market • Search              ║
║              Sector • Industry • EquityQuery • Screener      ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
    print(banner)

def print_progress_bar(current: int, total: int, width: int = 50):
    """Print a colorful progress bar"""
    progress = int(width * current / total)
    bar = f"{Fore.GREEN}{'█' * progress}{Fore.WHITE}{'░' * (width - progress)}{Style.RESET_ALL}"
    percentage = (current / total) * 100
    print(f"\r{Fore.CYAN}Progress: {bar} {percentage:.1f}% ({current}/{total}){Style.RESET_ALL}", end='', flush=True)

def scrape_yahoo_finance(max_workers: int = 4, include_market_data: bool = True, max_data_size: int = None):
    """
    Enhanced scraper using multiple yfinance components for comprehensive data collection.
    
    Args:
        max_workers (int): Maximum number of concurrent threads (default: 4)
        include_market_data (bool): Whether to collect market-wide data (default: True)
        max_data_size (int): Maximum number of rows for large datasets (None = unlimited)
    """
    from stock_data import stock_names
    
    print_banner()
    
    # Define the start and end dates for 2 days of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)
    
    logger.info(f"{Fore.BLUE}🚀 Starting enhanced data collection from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}{Style.RESET_ALL}")
    logger.info(f"{Fore.BLUE}📊 Processing {len(stock_names)} stocks with {max_workers} workers{Style.RESET_ALL}")
    logger.info(f"{Fore.BLUE}🌍 Market data collection: {'Enabled' if include_market_data else 'Disabled'}{Style.RESET_ALL}")
    print()
    
    # Ensure the folder exists
    folder_path = os.path.join(os.getcwd(), "json_stock_data")
    os.makedirs(folder_path, exist_ok=True)
    
    # Collect market-wide data first
    if include_market_data:
        logger.info(f"{Fore.MAGENTA}🌍 Collecting market-wide data...{Style.RESET_ALL}")
        market_collector = MarketDataCollector(folder_path)
        market_data = market_collector.collect_market_data()
        logger.info(f"{Fore.GREEN}✅ Market data collection completed{Style.RESET_ALL}")
        print()
    
    # Create enhanced workers for each stock
    workers = [StockDataWorker(ticker, folder_path, max_data_size) for ticker in stock_names]
    
    # Results tracking
    results = []
    successful_fetches = 0
    failed_fetches = 0
    processed_count = 0
    
    start_time = time.time()
    
    # Use ThreadPoolExecutor for concurrent execution
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_worker = {
            executor.submit(worker.fetch_comprehensive_stock_data, start_date, end_date): worker 
            for worker in workers
        }
        
        # Process completed tasks
        for future in as_completed(future_to_worker):
            worker = future_to_worker[future]
            try:
                result = future.result()
                results.append(result)
                processed_count += 1
                
                # Update progress bar
                print_progress_bar(processed_count, len(stock_names))
                
                if result['status'] == 'success':
                    successful_fetches += 1
                    # Success message is already logged in the worker
                else:
                    failed_fetches += 1
                    logger.warning(f"{Fore.YELLOW}⚠️ {result['ticker']}: {result['message']}{Style.RESET_ALL}")
                    
            except Exception as e:
                failed_fetches += 1
                processed_count += 1
                logger.error(f"{Fore.RED}❌ {worker.ticker}: Unexpected error - {str(e)}{Style.RESET_ALL}")
                results.append({
                    'ticker': worker.ticker,
                    'status': 'exception',
                    'message': str(e)
                })
                print_progress_bar(processed_count, len(stock_names))
    
    # Clear progress bar and print summary
    print("\n")
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Summary report with colors
    logger.info(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    logger.info(f"{Fore.CYAN}{Style.BRIGHT}📊 ENHANCED SCRAPING SUMMARY REPORT{Style.RESET_ALL}")
    logger.info(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    
    # Performance metrics
    logger.info(f"{Fore.GREEN}✅ Total stocks processed: {len(stock_names)}{Style.RESET_ALL}")
    logger.info(f"{Fore.GREEN}✅ Successful fetches: {successful_fetches}{Style.RESET_ALL}")
    logger.info(f"{Fore.RED}❌ Failed fetches: {failed_fetches}{Style.RESET_ALL}")
    
    success_rate = (successful_fetches/len(stock_names)*100) if len(stock_names) > 0 else 0
    if success_rate >= 90:
        color = Fore.GREEN
    elif success_rate >= 70:
        color = Fore.YELLOW
    else:
        color = Fore.RED
    
    logger.info(f"{color}📈 Success rate: {success_rate:.1f}%{Style.RESET_ALL}")
    logger.info(f"{Fore.BLUE}⏱️  Execution time: {execution_time:.2f} seconds{Style.RESET_ALL}")
    logger.info(f"{Fore.BLUE}🚀 Average time per stock: {execution_time/len(stock_names):.2f} seconds{Style.RESET_ALL}")
    
    if include_market_data:
        logger.info(f"{Fore.MAGENTA}🌍 Market data collection: Completed{Style.RESET_ALL}")
    
    # Data collection summary
    if successful_fetches > 0:
        logger.info(f"\n{Fore.CYAN}📊 Data Collection Summary:{Style.RESET_ALL}")
        logger.info(f"  📈 Intraday data: 2 days of 1-minute intervals")
        logger.info(f"  💰 Financial statements: Full income, balance sheet, cash flow")
        logger.info(f"  📰 News & recommendations: Complete data")
        logger.info(f"  📊 Options data: Multiple expiration dates")
        logger.info(f"  👥 Holders data: Institutional and major holders")
        logger.info(f"  📅 Earnings data: Historical earnings and calendar")
        if max_data_size:
            logger.info(f"  ⚠️  Data size limit: {max_data_size} rows per dataset")
        else:
            logger.info(f"  ✅ No data size limits applied")
    
    if failed_fetches > 0:
        logger.info(f"\n{Fore.YELLOW}⚠️  Failed stocks:{Style.RESET_ALL}")
        for result in results:
            if result['status'] != 'success':
                logger.info(f"  {Fore.RED}• {result['ticker']}: {result['message']}{Style.RESET_ALL}")
    
    # Final status
    if failed_fetches == 0:
        logger.info(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 All stocks processed successfully!{Style.RESET_ALL}")
    elif successful_fetches > failed_fetches:
        logger.info(f"\n{Fore.YELLOW}{Style.BRIGHT}⚠️  Most stocks processed successfully with some failures.{Style.RESET_ALL}")
    else:
        logger.info(f"\n{Fore.RED}{Style.BRIGHT}❌ Many stocks failed to process.{Style.RESET_ALL}")
    
    logger.info(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    
    return results

if __name__ == "__main__":
    # You can adjust the number of workers based on your system capabilities
    # and to avoid overwhelming Yahoo Finance's servers
    try:
        # Set max_data_size to None for unlimited data, or set a limit like 10000
        scrape_yahoo_finance(
            max_workers=3, 
            include_market_data=True,
            max_data_size=None  # None = unlimited, or set number like 10000
        )
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Enhanced scraping interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Unexpected error: {str(e)}{Style.RESET_ALL}")
        logger.error(f"Unexpected error: {str(e)}")
