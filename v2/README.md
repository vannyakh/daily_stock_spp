# 🚀 Enhanced Stock Data Scraper & API

A comprehensive stock market data collection and API system that leverages multiple yfinance components to provide rich, multi-dimensional market insights.

## 🌟 Features

### Enhanced Data Collection
- **Comprehensive Stock Data**: Intraday prices, fundamentals, financials, options, news, and more
- **Market Overview**: Indices, sectors, global markets, and trending stocks
- **Multi-threaded Processing**: Efficient data collection with configurable concurrency
- **Data Persistence**: JSON storage for enhanced data, CSV for basic data

### yfinance Component Integration
- **Ticker**: Individual stock data collection
- **Tickers**: Multiple stock processing
- **Market**: Market-wide data collection
- **Search**: Stock search and discovery
- **Sector/Industry**: Sector performance analysis
- **EquityQuery/Screener**: Stock screening capabilities

### RESTful API
- **FastAPI Backend**: Modern, fast, and auto-documented
- **Comprehensive Endpoints**: Stock data, market overview, search, screening
- **Data Validation**: Pydantic models for request/response validation
- **CORS Support**: Cross-origin resource sharing enabled

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Enhanced      │    │   Stock Data     │    │   FastAPI       │
│   Scraper      │───▶│   Storage        │───▶│   Server        │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   yfinance      │    │   JSON/CSV       │    │   REST API      │
│   Components    │    │   Files          │    │   Endpoints     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd daily_stock_scraper-main
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -c "import yfinance, fastapi, uvicorn; print('✅ All dependencies installed')"
   ```

## 🚀 Usage

### 1. Data Collection

#### Run Enhanced Scraper
```bash
python enhanced_stock_scraper.py
```

**Options:**
- `max_workers`: Number of concurrent threads (default: 4)
- `include_market_data`: Collect market-wide data (default: True)

**Example:**
```bash
python enhanced_stock_scraper.py --max_workers 6 --include_market_data true
```

#### What Gets Collected

**Individual Stocks:**
- Intraday price data (1-minute intervals)
- Company information and fundamentals
- Financial statements (income, balance sheet, cash flow)
- Options data and expiration dates
- News and analyst recommendations
- Institutional and major holders
- Earnings data and calendar

**Market Overview:**
- Major indices (S&P 500, Dow, NASDAQ, Russell 2000, VIX)
- Sector performance (Technology, Financials, Energy, etc.)
- Global markets (FTSE, DAX, Nikkei, Hang Seng, etc.)
- Trending stocks by category

### 2. API Server

#### Start the API Server
```bash
python stock_api_server.py
```

The server will start at `http://localhost:8000`

#### API Documentation
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### 3. API Client

#### Run the Example Client
```bash
python api_client_example.py
```

This demonstrates all available API endpoints and data types.

## 📡 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/api/v1/health` | GET | Health check |
| `/api/v1/stats` | GET | API usage statistics |

### Stock Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/stocks` | GET | List all available stocks |
| `/api/v1/stocks/{ticker}` | GET | Get comprehensive stock data |
| `/api/v1/stocks/{ticker}/financials` | GET | Get financial statements |
| `/api/v1/stocks/{ticker}/news` | GET | Get news and recommendations |
| `/api/v1/stocks/{ticker}/options` | GET | Get options data |

### Market Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/market/overview` | GET | Complete market overview |
| `/api/v1/market/sectors` | GET | Sector performance data |
| `/api/v1/market/indices` | GET | Market indices data |
| `/api/v1/market/global` | GET | Global market data |

### Search & Screening

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/stocks/search` | POST | Search for stocks |
| `/api/v1/stocks/screener` | POST | Screen stocks by criteria |

## 🔍 Data Examples

### Stock Search Request
```json
{
  "query": "AI",
  "limit": 10
}
```

### Stock Screening Request
```json
{
  "sector": "Technology",
  "market_cap_min": 1000000000,
  "pe_ratio_max": 25,
  "dividend_yield_min": 0.02,
  "limit": 20
}
```

### Stock Data Response
```json
{
  "ticker": "AAPL",
  "data_type": "comprehensive",
  "data": {
    "intraday_data": {...},
    "stock_info": {...},
    "financials": {...},
    "options_data": {...},
    "news_data": {...},
    "holders_data": {...},
    "earnings_data": {...}
  },
  "source": "enhanced_scraper"
}
```

## 🛠️ Configuration

### Scraper Configuration
```python
# In enhanced_stock_scraper.py
def scrape_enhanced_yahoo_finance(
    max_workers: int = 4,           # Concurrent threads
    include_market_data: bool = True # Market data collection
):
```

### API Configuration
```python
# In stock_api_server.py
ENHANCED_DATA_PATH = "json_stock_data"  # Enhanced data directory
STOCK_DATA_PATH = "stock_data"              # Basic data directory
```

### Server Configuration
```python
# In stock_api_server.py
uvicorn.run(
    "stock_api_server:app",
    host="0.0.0.0",        # Bind address
    port=8000,             # Port number
    reload=True,           # Auto-reload on changes
    log_level="info"       # Logging level
)
```

## 📊 Data Storage

### File Structure
```
project_root/
├── json_stock_data/           # Enhanced scraper output
│   ├── aapl_comprehensive.json   # Apple comprehensive data
│   ├── msft_comprehensive.json   # Microsoft comprehensive data
│   └── market_overview.json      # Market overview data
├── stock_data/                    # Basic scraper output
│   ├── aapl_intraday.csv         # Apple intraday data
│   └── msft_intraday.csv         # Microsoft intraday data
└── logs/
    ├── enhanced_scraper.log       # Enhanced scraper logs
    └── scraper.log               # Basic scraper logs
```

### Data Formats

**Enhanced Data (JSON):**
- Comprehensive stock information
- Nested data structures
- Metadata and timestamps
- Error handling and status codes

**Basic Data (CSV):**
- Intraday price data
- Simple tabular format
- Historical data accumulation
- Lightweight storage

## 🔧 Customization

### Adding New Data Sources
1. Extend `EnhancedStockDataWorker` class
2. Add new data collection methods
3. Update the comprehensive data structure
4. Add corresponding API endpoints

### Modifying Data Collection
1. Adjust `max_workers` for performance
2. Modify date ranges and intervals
3. Add new stock symbols to `stock_data.py`
4. Customize data processing logic

### API Extensions
1. Add new Pydantic models
2. Create additional endpoints
3. Implement data filtering
4. Add authentication/authorization

## 📈 Performance Considerations

### Rate Limiting
- Built-in delays to avoid overwhelming Yahoo Finance
- Configurable worker threads
- Error handling and retry logic

### Data Management
- JSON compression for large datasets
- Incremental data updates
- Efficient data structures
- Memory-conscious processing

### Scalability
- Multi-threaded data collection
- Async API endpoints
- Efficient data serialization
- Modular architecture

## 🚨 Troubleshooting

### Common Issues

**1. Rate Limiting Errors**
```
❌ Error fetching data: HTTP Error 429: Too Many Requests
```
**Solution**: Reduce `max_workers` or increase delays

**2. Missing Data**
```
⚠️ No data retrieved for TICKER
```
**Solution**: Check ticker symbol validity and market hours

**3. API Connection Errors**
```
❌ API is not accessible
```
**Solution**: Ensure server is running and check port configuration

**4. Memory Issues**
```
❌ MemoryError during data processing
```
**Solution**: Reduce batch sizes or increase system memory

### Debug Mode
```python
# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
```

### Data Validation
```python
# Check data integrity
python -c "
import json
with open('json_stock_data/aapl_comprehensive.json') as f:
    data = json.load(f)
    print(f'Data points: {len(data)}')
    print(f'Keys: {list(data.keys())}')
"
```

## 🔮 Future Enhancements

### Planned Features
- **Real-time WebSocket streaming**
- **Advanced technical indicators**
- **Machine learning insights**
- **Portfolio management tools**
- **Alert system for price movements**
- **Data visualization dashboard**

### Integration Possibilities
- **Trading platforms** (Alpaca, Interactive Brokers)
- **Data warehouses** (Snowflake, BigQuery)
- **Analytics tools** (Tableau, Power BI)
- **Mobile applications** (React Native, Flutter)

## 📚 Additional Resources

### Documentation
- [yfinance Documentation](https://pypi.org/project/yfinance/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pandas Documentation](https://pandas.pydata.org/)

### Related Projects
- [yfinance](https://github.com/ranaroussi/yfinance)
- [FastAPI](https://github.com/tiangolo/fastapi)
- [Pandas](https://github.com/pandas-dev/pandas)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **yfinance contributors** for the excellent Yahoo Finance wrapper
- **FastAPI team** for the modern web framework
- **Pandas team** for data manipulation tools
- **Open source community** for inspiration and support

---

**Happy Trading! 📈💰**
