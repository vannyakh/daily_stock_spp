from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
import json
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Stock Data API",
    description="REST API for accessing scraped stock market data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class StockData(BaseModel):
    ticker: str
    datetime: str
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int

class StockSummary(BaseModel):
    ticker: str
    data_points: int
    date_range: Dict[str, str]
    latest_price: float
    price_change: float
    price_change_percent: float
    volume_today: int

class StockSearchResult(BaseModel):
    ticker: str
    company_name: str
    sector: Optional[str] = None
    market_cap: Optional[float] = None

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Union[Dict, List]] = None
    timestamp: str
    count: Optional[int] = None

# Global variables
STOCK_DATA_FOLDER = "stock_data"
AVAILABLE_STOCKS = []

def get_available_stocks():
    """Get list of available stock tickers from CSV files"""
    global AVAILABLE_STOCKS
    if not AVAILABLE_STOCKS:
        try:
            if os.path.exists(STOCK_DATA_FOLDER):
                csv_files = [f for f in os.listdir(STOCK_DATA_FOLDER) if f.endswith('_intraday.csv')]
                AVAILABLE_STOCKS = [f.replace('_intraday.csv', '').upper() for f in csv_files]
                logger.info(f"Found {len(AVAILABLE_STOCKS)} available stocks")
        except Exception as e:
            logger.error(f"Error getting available stocks: {e}")
            AVAILABLE_STOCKS = []
    return AVAILABLE_STOCKS

def load_stock_data(ticker: str) -> Optional[pd.DataFrame]:
    """Load stock data from CSV file"""
    try:
        file_path = os.path.join(STOCK_DATA_FOLDER, f"{ticker.lower()}_intraday.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            
            # Handle different column naming patterns
            if 'Close' in df.columns:
                # Standard column names
                pass
            elif f'Close {ticker.upper()}' in df.columns:
                # Rename columns to standard format
                df = df.rename(columns={
                    f'Open {ticker.upper()}': 'Open',
                    f'High {ticker.upper()}': 'High',
                    f'Low {ticker.upper()}': 'Low',
                    f'Close {ticker.upper()}': 'Close',
                    f'Adj Close {ticker.upper()}': 'Adj Close',
                    f'Volume {ticker.upper()}': 'Volume'
                })
            else:
                # Try to find any close-like column
                close_cols = [col for col in df.columns if 'Close' in col]
                if close_cols:
                    # Use the first close column found
                    df = df.rename(columns={close_cols[0]: 'Close'})
                    # Add other required columns if they exist
                    for col_type in ['Open', 'High', 'Low', 'Volume']:
                        matching_cols = [col for col in df.columns if col_type in col]
                        if matching_cols:
                            df = df.rename(columns={matching_cols[0]: col_type})
                    
                    # If Adj Close doesn't exist, use Close
                    if 'Adj Close' not in df.columns:
                        df['Adj Close'] = df['Close']
            
            return df
        return None
    except Exception as e:
        logger.error(f"Error loading data for {ticker}: {e}")
        return None

def get_stock_summary(ticker: str) -> Optional[StockSummary]:
    """Get summary statistics for a stock"""
    try:
        df = load_stock_data(ticker)
        if df is None or df.empty:
            return None
        
        # Calculate summary statistics
        latest_data = df.iloc[-1]
        earliest_data = df.iloc[0]
        
        # Calculate price change
        price_change = latest_data['Close'] - earliest_data['Close']
        price_change_percent = (price_change / earliest_data['Close']) * 100
        
        # Get today's volume (assuming last trading day)
        today_volume = df.iloc[-1]['Volume'] if len(df) > 0 else 0
        
        return StockSummary(
            ticker=ticker.upper(),
            data_points=len(df),
            date_range={
                "start": earliest_data.name.strftime('%Y-%m-%d %H:%M:%S'),
                "end": latest_data.name.strftime('%Y-%m-%d %H:%M:%S')
            },
            latest_price=round(latest_data['Close'], 2),
            price_change=round(price_change, 2),
            price_change_percent=round(price_change_percent, 2),
            volume_today=today_volume
        )
    except Exception as e:
        logger.error(f"Error calculating summary for {ticker}: {e}")
        return None

# API Endpoints

@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with API information"""
    return APIResponse(
        success=True,
        message="Stock Data API is running",
        data={
            "api_name": "Stock Data API",
            "version": "1.0.0",
            "endpoints": {
                "stocks": "/api/stocks",
                "stock_data": "/api/stocks/{ticker}",
                "stock_summary": "/api/stocks/{ticker}/summary",
                "search": "/api/search",
                "health": "/api/health"
            }
        },
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint"""
    try:
        available_stocks = get_available_stocks()
        return APIResponse(
            success=True,
            message="API is healthy",
            data={
                "status": "healthy",
                "available_stocks": len(available_stocks),
                "data_folder": STOCK_DATA_FOLDER,
                "timestamp": datetime.now().isoformat()
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/api/stocks", response_model=APIResponse)
async def get_stocks(
    limit: Optional[int] = Query(None, description="Limit number of results"),
    offset: Optional[int] = Query(0, description="Offset for pagination")
):
    """Get list of available stocks"""
    try:
        available_stocks = get_available_stocks()
        
        # Apply pagination
        if limit:
            available_stocks = available_stocks[offset:offset + limit]
        elif offset:
            available_stocks = available_stocks[offset:]
        
        return APIResponse(
            success=True,
            message=f"Found {len(available_stocks)} stocks",
            data=available_stocks,
            timestamp=datetime.now().isoformat(),
            count=len(available_stocks)
        )
    except Exception as e:
        logger.error(f"Error getting stocks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stocks")

@app.get("/api/stocks/{ticker}", response_model=APIResponse)
async def get_stock_data(
    ticker: str = Path(..., description="Stock ticker symbol"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: Optional[int] = Query(100, description="Limit number of data points"),
    interval: Optional[str] = Query("1m", description="Data interval (1m, 5m, 15m, 1h, 1d)")
):
    """Get stock data for a specific ticker"""
    try:
        ticker = ticker.upper()
        df = load_stock_data(ticker)
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        # Apply date filters
        if start_date:
            try:
                start_dt = pd.to_datetime(start_date)
                df = df[df.index >= start_dt]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")
        
        if end_date:
            try:
                end_dt = pd.to_datetime(end_date)
                df = df[df.index <= end_dt]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format")
        
        # Apply limit
        if limit and limit > 0:
            df = df.tail(limit)
        
        # Convert to list of dictionaries
        data = []
        for timestamp, row in df.iterrows():
            data.append({
                "ticker": ticker,
                "datetime": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "adj_close": round(row['Adj Close'], 2),
                "volume": int(row['Volume'])
            })
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(data)} data points for {ticker}",
            data={
                "ticker": ticker,
                "data": data,
                "metadata": {
                    "total_points": len(df),
                    "date_range": {
                        "start": df.index[0].strftime('%Y-%m-%d %H:%M:%S'),
                        "end": df.index[-1].strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
            },
            timestamp=datetime.now().isoformat(),
            count=len(data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data for {ticker}")

@app.get("/api/stocks/{ticker}/summary", response_model=APIResponse)
async def get_stock_summary_endpoint(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get summary statistics for a specific stock"""
    try:
        ticker = ticker.upper()
        summary = get_stock_summary(ticker)
        
        if summary is None:
            raise HTTPException(status_code=404, detail=f"No summary available for ticker {ticker}")
        
        return APIResponse(
            success=True,
            message=f"Summary retrieved for {ticker}",
            data=summary.dict(),
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve summary for {ticker}")

@app.get("/api/search", response_model=APIResponse)
async def search_stocks(
    query: str = Query(..., description="Search query (ticker or company name)"),
    limit: Optional[int] = Query(10, description="Maximum number of results")
):
    """Search for stocks by ticker or company name"""
    try:
        available_stocks = get_available_stocks()
        query = query.upper()
        
        # Simple search - can be enhanced with fuzzy matching
        results = [stock for stock in available_stocks if query in stock]
        
        # Limit results
        if limit:
            results = results[:limit]
        
        return APIResponse(
            success=True,
            message=f"Found {len(results)} stocks matching '{query}'",
            data=results,
            timestamp=datetime.now().isoformat(),
            count=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.get("/api/stocks/{ticker}/latest", response_model=APIResponse)
async def get_latest_price(
    ticker: str = Path(..., description="Stock ticker symbol")
):
    """Get the latest price for a specific stock"""
    try:
        ticker = ticker.upper()
        df = load_stock_data(ticker)
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        latest = df.iloc[-1]
        
        return APIResponse(
            success=True,
            message=f"Latest price for {ticker}",
            data={
                "ticker": ticker,
                "latest_price": round(latest['Close'], 2),
                "timestamp": df.index[-1].strftime('%Y-%m-%d %H:%M:%S'),
                "volume": int(latest['Volume']),
                "change": round(latest['Close'] - df.iloc[-2]['Close'], 2) if len(df) > 1 else 0
            },
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest price for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve latest price for {ticker}")

@app.get("/api/stats", response_model=APIResponse)
async def get_api_stats():
    """Get API usage statistics"""
    try:
        available_stocks = get_available_stocks()
        
        # Calculate some basic stats
        total_data_points = 0
        for stock in available_stocks:
            df = load_stock_data(stock)
            if df is not None:
                total_data_points += len(df)
        
        return APIResponse(
            success=True,
            message="API statistics retrieved",
            data={
                "total_stocks": len(available_stocks),
                "total_data_points": total_data_points,
                "average_data_per_stock": round(total_data_points / len(available_stocks), 2) if available_stocks else 0,
                "data_folder_size_mb": round(os.path.getsize(STOCK_DATA_FOLDER) / (1024 * 1024), 2) if os.path.exists(STOCK_DATA_FOLDER) else 0
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting API stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve API statistics")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content=APIResponse(
            success=False,
            message="Resource not found",
            data={"error": "The requested resource was not found"},
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=APIResponse(
            success=False,
            message="Internal server error",
            data={"error": "An internal server error occurred"},
            timestamp=datetime.now().isoformat()
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get available stocks on startup
    get_available_stocks()
    
    print("🚀 Starting Stock Data API...")
    print(f"📊 Found {len(AVAILABLE_STOCKS)} available stocks")
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
