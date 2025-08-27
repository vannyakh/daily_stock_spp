# 🚀 Enhanced Stock Data Scraper & API System

A comprehensive stock market data collection and API system that supports both basic (V1) and enhanced (V2) versions, leveraging multiple yfinance components to provide rich, multi-dimensional market insights.

## 🌟 System Overview

This system provides two distinct API versions to meet different needs:

- **🔄 V1 - Basic Stock Data API**: Simple, lightweight API for intraday data access
- **🚀 V2 - Enhanced Stock Data API**: Comprehensive API with advanced features and market overview

## 🔀 Version Comparison

| Feature | V1 - Basic | V2 - Enhanced |
|---------|------------|----------------|
| **Data Collection** | Intraday prices only | Comprehensive + market data |
| **Storage Format** | CSV files | JSON + CSV files |
| **API Endpoints** | Basic REST endpoints | Advanced + screening |
| **Market Data** | Individual stocks | + Indices, sectors, trending |
| **Performance** | Fast, lightweight | Feature-rich, comprehensive |
| **Use Case** | Simple data access | Advanced analysis & screening |

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Stock Data    │    │   Data Storage   │    │   FastAPI       │
│   Scrapers      │───▶│   (CSV/JSON)     │───▶│   Servers       │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   V1: yf_scraper│    │   stock_data/    │    │   V1: stock_api │
│   V2: stock_scraper│  │   json_stock_data│    │   V2: stock_api_server│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Git

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

## 🚀 Quick Start

### Option 1: Interactive Startup Script (Recommended)
```bash
python start_system.py
```
This provides a menu-driven interface to:
- Choose between V1 and V2
- Run scrapers
- Start API servers
- Check data status

### Option 2: Direct Execution

#### V1 - Basic System
```bash
# Run basic scraper
python v1/yf_scraper.py

# Start basic API server
python v1/stock_api.py
```

#### V2 - Enhanced System
```bash
# Run enhanced scraper
python v2/stock_scraper.py

# Start enhanced API server
python v2/stock_api_server.py
```

## 📊 Data Collection

### V1 - Basic Data Collection
```bash
python v1/yf_scraper.py
```
**What Gets Collected:**
- Intraday price data (1-minute intervals)
- Basic stock information
- CSV storage in `stock_data/` folder

### V2 - Enhanced Data Collection
```bash
python v2/stock_scraper.py --max_workers 6 --include_market_data true
```
**What Gets Collected:**
- Intraday price data (1-minute intervals)
- Company information and fundamentals
- Financial statements (income, balance sheet, cash flow)
- Options data and expiration dates
- News and analyst recommendations
- Institutional and major holders
- Earnings data and calendar
- Market indices and sector performance
- Global market data
- Trending stocks

## 🌐 API Usage

### V1 - Basic API Endpoints

**Base URL**: `http://localhost:8000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | API health check |
| `/api/stocks` | GET | List available stocks |
| `/api/stocks/{ticker}` | GET | Get stock data |
| `/api/stocks/{ticker}/summary` | GET | Stock summary |
| `/api/stocks/{ticker}/latest` | GET | Latest price |
| `/api/search` | GET | Search stocks |
| `/api/stats` | GET | API statistics |

### V2 - Enhanced API Endpoints

**Base URL**: `http://localhost:8000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/api/v1/stocks` | GET | List all stocks with status |
| `/api/v1/stocks/{ticker}` | GET | Get comprehensive stock data |
| `/api/v1/market/overview` | GET | Market overview data |
| `/api/v1/stocks/search` | GET | Advanced stock search |
| `/api/v1/stocks/screener` | GET | Stock screening with filters |
| `/api/v1/market/sectors` | GET | Sector performance data |
| `/api/v1/market/indices` | GET | Market indices data |
| `/api/v1/market/global` | GET | Global market data |

## 🐳 Docker Deployment

### Quick Docker Setup
```bash
# Build and run V1 API
docker build -f v1/Dockerfile -t stock-data-api-v1 .
docker run -p 8001:8000 stock-data-api-v1

# Build and run V2 API
docker build -f v2/Dockerfile -t stock-data-api-v2 .
docker run -p 8000:8000 stock-data-api-v2
```

### Docker Compose
```bash
# Deploy V1 stack
API_VERSION=v1 docker-compose up -d

# Deploy V2 stack (default)
API_VERSION=v2 docker-compose up -d

# Deploy specific services
docker-compose --profile v1 up -d stock-api-v1 redis nginx
```

## 🚀 Deployment Scripts

### Automated Deployment
```bash
# Deploy V1 API to staging
./deploy.sh staging v1

# Deploy V2 API to production
./deploy.sh production v2

# Deploy V1 API with Docker
./deploy.sh docker v1

# Check deployment status
./deploy.sh status v2
```

### GitHub Actions Workflows

- **Daily Scraper**: Automatically collects data daily
- **API Deployment**: Automated testing and deployment
- **Version Selection**: Choose V1 or V2 for deployment

## 📱 API Client Examples

### Python Client
```python
from example.api_client_example import StockDataAPIClient

# Initialize client
client = StockDataAPIClient()

# V1 API calls
summary = client.get_stock_summary("AAPL")
data = client.get_stock_data("AAPL", limit=10)

# V2 API calls (enhanced features)
market_overview = client.get_market_overview()
screened_stocks = client.screen_stocks(sector="Technology", market_cap_min=1000000000)
```

### cURL Examples

#### V1 API
```bash
# Get stock summary
curl http://localhost:8000/api/stocks/aapl/summary

# Get recent data
curl "http://localhost:8000/api/stocks/aapl?limit=5"
```

#### V2 API
```bash
# Get market overview
curl http://localhost:8000/api/v1/market/overview

# Screen stocks
curl "http://localhost:8000/api/v1/stocks/screener?sector=Technology&market_cap_min=1000000000"
```

## 🔧 Configuration

### Environment Variables
- `API_VERSION`: Set to 'v1' or 'v2' (default: 'v2')
- `MAX_WORKERS`: Concurrent threads for scraping (default: 4)
- `INCLUDE_MARKET_DATA`: Include market overview (V2 only, default: true)

### API Settings
- **V1 Host**: 0.0.0.0:8000
- **V2 Host**: 0.0.0.0:8000
- **CORS**: Enabled for all origins
- **Documentation**: Auto-generated Swagger/ReDoc

## 📈 Performance & Monitoring

### Performance Metrics
- **V1**: Fast response times, lightweight processing
- **V2**: Comprehensive data, advanced features
- **Multi-threading**: Configurable concurrent processing
- **Memory Optimization**: Efficient data handling

### Health Checks
- **V1**: `/api/health` endpoint
- **V2**: `/` root endpoint
- **Docker**: Built-in health checks
- **Monitoring**: Prometheus + Grafana support

## 🛡️ Security & Best Practices

### Security Features
- Input validation and sanitization
- Rate limiting (configurable)
- CORS configuration
- Non-root Docker containers

### Production Considerations
- Use HTTPS in production
- Configure CORS origins
- Implement authentication
- Set up monitoring and logging
- Use production ASGI server (Gunicorn + Uvicorn)

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   - V1 and V2 can run simultaneously on different ports
   - Use `./deploy.sh status v1` to check status

2. **Data Not Found**
   - Run scraper first: `python v1/yf_scraper.py` or `python v2/stock_scraper.py`
   - Check data folders: `stock_data/` and `json_stock_data/`

3. **Docker Issues**
   - Ensure Docker is running
   - Check container logs: `docker logs stock-data-api-v1`

### Debug Mode
```bash
# Enable debug logging
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

## 📚 Documentation

### Interactive API Docs
- **V1 API**: http://localhost:8000/docs (Swagger UI)
- **V2 API**: http://localhost:8000/docs (Swagger UI)

### Additional Resources
- **V1 README**: `v1/README.md`
- **V2 README**: `v2/README.md`
- **API Examples**: `example/api_client_example.py`
- **Deployment Guide**: `deploy.sh --help`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for both V1 and V2
5. Submit a pull request

### Development Guidelines
- Test changes on both API versions
- Update documentation for affected features
- Ensure backward compatibility where possible
- Follow existing code style and patterns

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help
- Create an issue in the repository
- Check the troubleshooting section
- Review version-specific README files
- Use the interactive startup script: `python start_system.py`

### Community
- Report bugs and feature requests
- Share your use cases and examples
- Contribute improvements and fixes

---

## 🎯 Quick Reference

### Start Everything
```bash
python start_system.py
# Choose option 6: Run Full System
```

### V1 - Basic System
```bash
./deploy.sh staging v1
# Access at: http://localhost:8000
```

### V2 - Enhanced System
```bash
./deploy.sh production v2
# Access at: http://localhost:8000
```

### Data Collection
```bash
# V1: Basic intraday data
python v1/yf_scraper.py

# V2: Comprehensive data
python v2/stock_scraper.py
```

**Happy Trading! 📈💰**
