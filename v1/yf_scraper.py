import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Dict, Optional
import logging
from colorama import init, Fore, Back, Style

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

# Configure logging with colored output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

# Apply colored formatter to console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)
logger.handlers = []  # Clear existing handlers
logger.addHandler(logging.FileHandler('scraper.log'))
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

class StockDataWorker:
    """Worker class for fetching individual stock data"""
    
    def __init__(self, ticker: str, folder_path: str):
        self.ticker = ticker
        self.folder_path = folder_path
        self.lock = threading.Lock()
    
    def fetch_stock_data(self, start_date: datetime, end_date: datetime) -> Dict:
        """Fetch data for a single stock"""
        try:
            logger.info(f"{Fore.CYAN}🔄 Fetching data for {self.ticker}...{Style.RESET_ALL}")
            
            # Add small delay to avoid rate limiting
            time.sleep(0.1)
            
            intraday_data = yf.download(
                self.ticker,
                interval='1m',
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                progress=False  # Disable progress bar for cleaner output
            )
            
            if intraday_data.empty:
                logger.warning(f"{Fore.YELLOW}⚠️ No data retrieved for {self.ticker}.{Style.RESET_ALL}")
                return {
                    'ticker': self.ticker,
                    'status': 'no_data',
                    'message': 'No data available'
                }
            
            # Process the data
            processed_data = self._process_data(intraday_data)
            
            # Save to CSV
            success = self._save_to_csv(processed_data)
            
            if success:
                return {
                    'ticker': self.ticker,
                    'status': 'success',
                    'rows_fetched': len(processed_data),
                    'message': f'Successfully updated {self.ticker} data'
                }
            else:
                return {
                    'ticker': self.ticker,
                    'status': 'save_error',
                    'message': f'Failed to save data for {self.ticker}'
                }
                
        except Exception as e:
            logger.error(f"{Fore.RED}❌ Error fetching data for {self.ticker}: {str(e)}{Style.RESET_ALL}")
            return {
                'ticker': self.ticker,
                'status': 'error',
                'message': str(e)
            }
    
    def _process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process and clean the downloaded data"""
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
        
        return data
    
    def _save_to_csv(self, data: pd.DataFrame) -> bool:
        """Save data to CSV file with thread-safe operations"""
        try:
            file_path = os.path.join(self.folder_path, f"{self.ticker.lower()}_intraday.csv")
            
            with self.lock:
                if os.path.exists(file_path):
                    # Read existing data
                    existing_data = pd.read_csv(file_path, index_col=0, parse_dates=True)
                    
                    # Append new data to the existing data
                    combined_data = pd.concat([existing_data, data])
                    
                    # Drop duplicate rows based on the index (datetime)
                    combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
                    
                    # Sort by datetime
                    combined_data = combined_data.sort_index()
                else:
                    # If file doesn't exist, just use the new data
                    combined_data = data
                
                # Save the updated data back to the CSV file
                combined_data.to_csv(file_path, index=True)
                
            logger.info(f"{Fore.GREEN}✅ Updated {file_path} with {len(data)} new rows.{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            logger.error(f"{Fore.RED}❌ Error saving data for {self.ticker}: {str(e)}{Style.RESET_ALL}")
            return False

def print_banner():
    """Print a colorful banner for the scraper"""
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}
╔══════════════════════════════════════════════════════════════╗
║                    📈 STOCK DATA SCRAPER 📈                   ║
║                    Multi-Threaded Edition                    ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
    print(banner)

def print_progress_bar(current: int, total: int, width: int = 50):
    """Print a colorful progress bar"""
    progress = int(width * current / total)
    bar = f"{Fore.GREEN}{'█' * progress}{Fore.WHITE}{'░' * (width - progress)}{Style.RESET_ALL}"
    percentage = (current / total) * 100
    print(f"\r{Fore.CYAN}Progress: {bar} {percentage:.1f}% ({current}/{total}){Style.RESET_ALL}", end='', flush=True)

def scrape_yahoo_finance_intraday(max_workers: int = 4):
    """
    Scrape 2 days' worth of intraday data for stocks using multi-threading.
    
    Args:
        max_workers (int): Maximum number of concurrent threads (default: 4)
    """
    from stock_data import stock_names
    
    print_banner()
    
    # Define the start and end dates for 2 days of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)
    
    logger.info(f"{Fore.BLUE}🚀 Starting data collection from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}{Style.RESET_ALL}")
    logger.info(f"{Fore.BLUE}📊 Processing {len(stock_names)} stocks with {max_workers} workers{Style.RESET_ALL}")
    print()
    
    # Ensure the folder exists
    folder_path = os.path.join(os.getcwd(), "stock_data")
    os.makedirs(folder_path, exist_ok=True)
    
    # Create workers for each stock
    workers = [StockDataWorker(ticker, folder_path) for ticker in stock_names]
    
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
            executor.submit(worker.fetch_stock_data, start_date, end_date): worker 
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
    logger.info(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    logger.info(f"{Fore.CYAN}{Style.BRIGHT}📊 SCRAPING SUMMARY REPORT{Style.RESET_ALL}")
    logger.info(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    
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
    
    logger.info(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    
    return results

if __name__ == "__main__":
    # You can adjust the number of workers based on your system capabilities
    # and to avoid overwhelming Yahoo Finance's servers
    try:
        scrape_yahoo_finance_intraday(max_workers=3)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Scraping interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Unexpected error: {str(e)}{Style.RESET_ALL}")
        logger.error(f"Unexpected error: {str(e)}")
