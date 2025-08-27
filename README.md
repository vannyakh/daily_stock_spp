# Stock Data API Documentation

## 🚀 Overview

The Stock Data API is a comprehensive REST API built with FastAPI that provides easy access to scraped stock market data. It offers multiple endpoints for retrieving stock information, summaries, and historical data with support for filtering, pagination, and search functionality.

## 🌟 Features

- **Multi-threaded Data Scraping** - Efficient collection of stock data using concurrent workers
- **RESTful API** - Clean, intuitive endpoints following REST principles
- **Real-time Data Access** - Get current stock prices and historical data
- **Flexible Filtering** - Filter data by date ranges and limits
- **Search Functionality** - Find stocks by ticker or company name
- **Comprehensive Statistics** - API usage and data metrics
- **Error Handling** - Robust error handling with meaningful messages
- **CORS Support** - Cross-origin resource sharing enabled
- **Auto-generated Documentation** - Interactive API docs with Swagger UI

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Stock Data    │    │   FastAPI       │    │   CSV Files     │
│   Scraper       │───▶│   REST API      │───▶│   (stock_data/  │
│   (yf_scraper)  │    │   (stock_api)   │    │    folder)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 API Endpoints

### Base URL
```
http://localhost:8000
```

### 1. Root Endpoint
- **GET** `/`
- **Description**: API information and available endpoints
- **Response**: API metadata and endpoint list

### 2. Health Check
- **GET** `/api/health`
- **Description**: Check API health and status
- **Response**: Health status, available stocks count, data folder info

### 3. List Stocks
- **GET** `/api/stocks`
- **Query Parameters**:
  - `limit` (optional): Maximum number of results
  - `offset` (optional): Pagination offset
- **Description**: Get list of available stock tickers
- **Response**: Array of stock tickers with pagination info

### 4. Stock Data
- **GET** `/api/stocks/{ticker}`
- **Path Parameters**:
  - `ticker`: Stock ticker symbol (e.g., AAPL, MSFT)
- **Query Parameters**:
  - `start_date` (optional): Start date (YYYY-MM-DD)
  - `end_date` (optional): End date (YYYY-MM-DD)
  - `limit` (optional): Maximum data points (default: 100)
  - `interval` (optional): Data interval (default: 1m)
- **Description**: Get historical stock data for a specific ticker
- **Response**: Stock data with OHLCV information and metadata

### 5. Stock Summary
- **GET** `/api/stocks/{ticker}/summary`
- **Path Parameters**:
  - `ticker`: Stock ticker symbol
- **Description**: Get summary statistics for a stock
- **Response**: Price change, volume, data points, date range

### 6. Latest Price
- **GET** `/api/stocks/{ticker}/latest`
- **Path Parameters**:
  - `ticker`: Stock ticker symbol
- **Description**: Get the most recent price for a stock
- **Response**: Latest price, timestamp, volume, price change

### 7. Search Stocks
- **GET** `/api/search`
- **Query Parameters**:
  - `query`: Search query (ticker or company name)
  - `limit` (optional): Maximum results (default: 10)
- **Description**: Search for stocks by ticker or company name
- **Response**: Matching stock tickers

### 8. API Statistics
- **GET** `/api/stats`
- **Description**: Get API usage and data statistics
- **Response**: Total stocks, data points, averages, folder size

## 📊 Data Models

### StockData
```json
{
  "ticker": "AAPL",
  "datetime": "2025-08-26 19:59:00",
  "open": 501.76,
  "high": 502.46,
  "low": 501.71,
  "close": 501.93,
  "adj_close": 501.93,
  "volume": 775473
}
```

### StockSummary
```json
{
  "ticker": "AAPL",
  "data_points": 780,
  "date_range": {
    "start": "2025-08-25 13:30:00",
    "end": "2025-08-26 19:59:00"
  },
  "latest_price": 501.93,
  "price_change": -5.15,
  "price_change_percent": -1.02,
  "volume_today": 775473
}
```

### APIResponse
```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": {...},
  "timestamp": "2025-08-27T17:55:08.552300",
  "count": 5
}
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd daily_stock_scraper-main
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Scrape stock data** (if not already done)
   ```bash
   python3 yf_scraper.py
   ```

5. **Start the API server**
   ```bash
   python3 stock_api.py
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## 📱 Usage Examples

### Python Client Example

```python
from api_client_example import StockDataAPIClient

# Initialize client
client = StockDataAPIClient()

# Get stock summary
summary = client.get_stock_summary("AAPL")
print(f"AAPL latest price: ${summary['data']['latest_price']}")

# Get recent data
data = client.get_stock_data("AAPL", limit=10)
for point in data['data']:
    print(f"{point['datetime']}: ${point['close']}")
```

### cURL Examples

```bash
# Get API health
curl http://localhost:8000/api/health

# Get AAPL summary
curl http://localhost:8000/api/stocks/aapl/summary

# Get recent AAPL data (last 5 points)
curl "http://localhost:8000/api/stocks/aapl?limit=5"

# Search for stocks containing "MSFT"
curl "http://localhost:8000/api/search?query=msft"
```

### JavaScript/Node.js Example

```javascript
// Get stock data
fetch('http://localhost:8000/api/stocks/aapl?limit=10')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('AAPL data:', data.data);
    }
  });
```

## 🔧 Configuration

### Environment Variables
- `STOCK_DATA_FOLDER`: Path to stock data folder (default: "stock_data")
- `MAX_WORKERS`: Maximum concurrent threads for scraping (default: 3)

### API Settings
- **Host**: 0.0.0.0 (accessible from any IP)
- **Port**: 8000
- **CORS**: Enabled for all origins (configure for production)

## 📈 Performance

- **Multi-threading**: Up to 3 concurrent workers for data scraping
- **Data Processing**: Efficient pandas-based data handling
- **Memory Usage**: Optimized for large datasets
- **Response Time**: Sub-second response times for most endpoints

## 🛡️ Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid parameters or date formats
- **404 Not Found**: Stock ticker not found or no data available
- **500 Internal Server Error**: Server-side processing errors

All errors include:
- Descriptive error messages
- Error codes
- Timestamps
- Structured error responses

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Features
- Interactive endpoint testing
- Request/response examples
- Schema validation
- Authentication (if implemented)

## 🔍 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the API server is running
   - Check if port 8000 is available

2. **No Data Found**
   - Verify stock data has been scraped
   - Check stock_data folder contents

3. **Column Mapping Errors**
   - Ensure CSV files have correct structure
   - Check for data corruption

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Deployment

### Production Considerations

1. **Security**
   - Configure CORS origins
   - Implement authentication
   - Use HTTPS

2. **Performance**
   - Use production ASGI server (Gunicorn + Uvicorn)
   - Implement caching
   - Database optimization

3. **Monitoring**
   - Health checks
   - Metrics collection
   - Log aggregation

### Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "stock_api.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

**Happy Trading! 📈💰**
