from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import os
import glob
from datetime import datetime, timedelta
import uvicorn
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Stock Data API",
    description="API for accessing comprehensive stock market data collected using yfinance components",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class StockDataResponse(BaseModel):
    ticker: str
    timestamp: str
    data_points: int
    status: str
    message: str

class MarketOverviewResponse(BaseModel):
    indices: Dict[str, Any]
    sectors: Dict[str, Any]
    trending: Dict[str, Any]
    global_markets: Dict[str, Any]
    timestamp: str

class StockSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class StockScreenerRequest(BaseModel):
    sector: Optional[str] = None
    market_cap_min: Optional[float] = None
    market_cap_max: Optional[float] = None
    pe_ratio_min: Optional[float] = None
    pe_ratio_max: Optional[float] = None
    dividend_yield_min: Optional[float] = None
    limit: Optional[int] = 50

# Global variables for data paths
ENHANCED_DATA_PATH = "json_stock_data"
STOCK_DATA_PATH = "stock_data"

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Enhanced Stock Data API",
        "version": "2.0.0",
        "description": "Comprehensive stock market data using yfinance components",
        "endpoints": {
            "stocks": "/api/v1/stocks",
            "stock": "/api/v1/stocks/{ticker}",
            "market": "/api/v1/market/overview",
            "search": "/api/v1/stocks/search",
            "screener": "/api/v1/stocks/screener",
            "sectors": "/api/v1/market/sectors",
            "indices": "/api/v1/market/indices",
            "global": "/api/v1/market/global"
        }
    }

@app.get("/api/v1/stocks", response_model=List[StockDataResponse])
async def get_all_stocks():
    """Get list of all available stocks with their data status"""
    try:
        stocks = []
        
        # Check enhanced data directory
        if os.path.exists(ENHANCED_DATA_PATH):
            json_files = glob.glob(os.path.join(ENHANCED_DATA_PATH, "*_comprehensive.json"))
            
            for file_path in json_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    ticker = data.get('ticker', 'Unknown')
                    timestamp = data.get('timestamp', 'Unknown')
                    
                    stocks.append(StockDataResponse(
                        ticker=ticker,
                        timestamp=timestamp,
                        data_points=len(data),
                        status="available",
                        message=f"Comprehensive data available for {ticker}"
                    ))
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")
        
        # Check original stock data directory
        if os.path.exists(STOCK_DATA_PATH):
            csv_files = glob.glob(os.path.join(STOCK_DATA_PATH, "*_intraday.csv"))
            
            for file_path in csv_files:
                try:
                    ticker = os.path.basename(file_path).replace("_intraday.csv", "").upper()
                    
                    # Check if we already have this ticker in enhanced data
                    if not any(s.ticker == ticker for s in stocks):
                        stocks.append(StockDataResponse(
                            ticker=ticker,
                            timestamp=datetime.now().isoformat(),
                            data_points=1,
                            status="basic",
                            message=f"Basic intraday data available for {ticker}"
                        ))
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
        
        return sorted(stocks, key=lambda x: x.ticker)
        
    except Exception as e:
        logger.error(f"Error getting all stocks: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/stocks/{ticker}", response_model=Dict[str, Any])
async def get_stock_data(ticker: str):
    """Get comprehensive data for a specific stock"""
    try:
        ticker = ticker.upper()
        
        # Try to get enhanced data first
        enhanced_file = os.path.join(ENHANCED_DATA_PATH, f"{ticker.lower()}_comprehensive.json")
        
        if os.path.exists(enhanced_file):
            with open(enhanced_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "ticker": ticker,
                "data_type": "comprehensive",
                "data": data,
                "source": "enhanced_scraper"
            }
        
        # Fall back to basic data
        basic_file = os.path.join(STOCK_DATA_PATH, f"{ticker.lower()}_intraday.csv")
        
        if os.path.exists(basic_file):
            import pandas as pd
            df = pd.read_csv(basic_file, index_col=0, parse_dates=True)
            
            return {
                "ticker": ticker,
                "data_type": "basic",
                "data": {
                    "intraday_data": df.tail(100).to_dict('records'),  # Last 100 records
                    "total_records": len(df),
                    "date_range": {
                        "start": df.index[0].isoformat() if len(df) > 0 else None,
                        "end": df.index[-1].isoformat() if len(df) > 0 else None
                    }
                },
                "source": "basic_scraper"
            }
        
        raise HTTPException(status_code=404, detail=f"Stock data not found for {ticker}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stock data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/market/overview", response_model=MarketOverviewResponse)
async def get_market_overview():
    """Get comprehensive market overview data"""
    try:
        market_file = os.path.join(ENHANCED_DATA_PATH, "market_overview.json")
        
        if not os.path.exists(market_file):
            raise HTTPException(status_code=404, detail="Market overview data not available. Run the enhanced scraper first.")
        
        with open(market_file, 'r', encoding='utf-8') as f:
            market_data = json.load(f)
        
        return MarketOverviewResponse(
            indices=market_data.get('indices', {}),
            sectors=market_data.get('sectors', {}),
            trending=market_data.get('trending', {}),
            global_markets=market_data.get('global', {}),
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/market/sectors")
async def get_sector_performance():
    """Get sector performance data"""
    try:
        market_file = os.path.join(ENHANCED_DATA_PATH, "market_overview.json")
        
        if not os.path.exists(market_file):
            raise HTTPException(status_code=404, detail="Sector data not available. Run the enhanced scraper first.")
        
        with open(market_file, 'r', encoding='utf-8') as f:
            market_data = json.load(f)
        
        sectors = market_data.get('sectors', {})
        
        # Sort sectors by performance
        sorted_sectors = dict(sorted(
            sectors.items(),
            key=lambda x: x[1].get('change_pct', 0) if isinstance(x[1], dict) and 'change_pct' in x[1] else 0,
            reverse=True
        ))
        
        return {
            "sectors": sorted_sectors,
            "timestamp": datetime.now().isoformat(),
            "total_sectors": len(sorted_sectors)
        }
        
    except Exception as e:
        logger.error(f"Error getting sector performance: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/market/indices")
async def get_market_indices():
    """Get major market indices data"""
    try:
        market_file = os.path.join(ENHANCED_DATA_PATH, "market_overview.json")
        
        if not os.path.exists(market_file):
            raise HTTPException(status_code=404, detail="Indices data not available. Run the enhanced scraper first.")
        
        with open(market_file, 'r', encoding='utf-8') as f:
            market_data = json.load(f)
        
        indices = market_data.get('indices', {})
        
        return {
            "indices": indices,
            "timestamp": datetime.now().isoformat(),
            "total_indices": len(indices)
        }
        
    except Exception as e:
        logger.error(f"Error getting market indices: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/market/global")
async def get_global_markets():
    """Get global market data"""
    try:
        market_file = os.path.join(ENHANCED_DATA_PATH, "market_overview.json")
        
        if not os.path.exists(market_file):
            raise HTTPException(status_code=404, detail="Global market data not available. Run the enhanced scraper first.")
        
        with open(market_file, 'r', encoding='utf-8') as f:
            market_data = json.load(f)
        
        global_markets = market_data.get('global', {})
        
        return {
            "global_markets": global_markets,
            "timestamp": datetime.now().isoformat(),
            "total_markets": len(global_markets)
        }
        
    except Exception as e:
        logger.error(f"Error getting global markets: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/stocks/search")
async def search_stocks(request: StockSearchRequest):
    """Search for stocks based on query"""
    try:
        import yfinance as yf
        
        # Use yfinance search functionality
        search_results = yf.Tickers(request.query)
        
        if hasattr(search_results, 'tickers'):
            results = []
            for ticker in search_results.tickers[:request.limit]:
                try:
                    info = ticker.info
                    results.append({
                        "ticker": ticker.ticker,
                        "name": info.get('longName', ticker.ticker),
                        "sector": info.get('sector', 'Unknown'),
                        "industry": info.get('industry', 'Unknown'),
                        "market_cap": info.get('marketCap'),
                        "current_price": info.get('currentPrice')
                    })
                except:
                    continue
            
            return {
                "query": request.query,
                "results": results,
                "total_found": len(results),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "query": request.query,
                "results": [],
                "total_found": 0,
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/stocks/screener")
async def screen_stocks(request: StockScreenerRequest):
    """Screen stocks based on criteria"""
    try:
        # Get all available stocks
        stocks_response = await get_all_stocks()
        screened_stocks = []
        
        for stock in stocks_response:
            if stock.status == "available":
                try:
                    # Get stock data for screening
                    stock_data = await get_stock_data(stock.ticker)
                    
                    if stock_data["data_type"] == "comprehensive":
                        info = stock_data["data"].get("stock_info", {}).get("data", {})
                        
                        # Apply filters
                        include_stock = True
                        
                        if request.sector and info.get('sector') != request.sector:
                            include_stock = False
                        
                        if request.market_cap_min and info.get('marketCap', 0) < request.market_cap_min:
                            include_stock = False
                        
                        if request.market_cap_max and info.get('marketCap', 0) > request.market_cap_max:
                            include_stock = False
                        
                        if request.pe_ratio_min and info.get('trailingPE', 0) < request.pe_ratio_min:
                            include_stock = False
                        
                        if request.pe_ratio_max and info.get('trailingPE', 0) > request.pe_ratio_max:
                            include_stock = False
                        
                        if request.dividend_yield_min and info.get('dividendYield', 0) < request.dividend_yield_min:
                            include_stock = False
                        
                        if include_stock:
                            screened_stocks.append({
                                "ticker": stock.ticker,
                                "name": info.get('longName', stock.ticker),
                                "sector": info.get('sector', 'Unknown'),
                                "industry": info.get('industry', 'Unknown'),
                                "market_cap": info.get('marketCap'),
                                "pe_ratio": info.get('trailingPE'),
                                "dividend_yield": info.get('dividendYield'),
                                "current_price": info.get('currentPrice')
                            })
                            
                            if len(screened_stocks) >= request.limit:
                                break
                
                except Exception as e:
                    logger.warning(f"Error screening stock {stock.ticker}: {e}")
                    continue
        
        return {
            "criteria": request.dict(),
            "results": screened_stocks,
            "total_found": len(screened_stocks),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error screening stocks: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/stocks/{ticker}/financials")
async def get_stock_financials(ticker: str):
    """Get financial statements for a specific stock"""
    try:
        stock_data = await get_stock_data(ticker)
        
        if stock_data["data_type"] == "comprehensive":
            financials = stock_data["data"].get("financials", {})
            return {
                "ticker": ticker,
                "financials": financials,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Financial data not available for {ticker}. Run the enhanced scraper first.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting financials for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/stocks/{ticker}/news")
async def get_stock_news(ticker: str):
    """Get news and recommendations for a specific stock"""
    try:
        stock_data = await get_stock_data(ticker)
        
        if stock_data["data_type"] == "comprehensive":
            news_data = stock_data["data"].get("news_data", {})
            return {
                "ticker": ticker,
                "news_data": news_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=f"News data not available for {ticker}. Run the enhanced scraper first.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting news for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/stocks/{ticker}/options")
async def get_stock_options(ticker: str):
    """Get options data for a specific stock"""
    try:
        stock_data = await get_stock_data(ticker)
        
        if stock_data["data_type"] == "comprehensive":
            options_data = stock_data["data"].get("options_data", {})
            return {
                "ticker": ticker,
                "options_data": options_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Options data not available for {ticker}. Run the enhanced scraper first.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting options for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.get("/api/v1/stats")
async def get_api_stats():
    """Get API usage statistics"""
    try:
        # Count available data files
        enhanced_files = len(glob.glob(os.path.join(ENHANCED_DATA_PATH, "*_comprehensive.json"))) if os.path.exists(ENHANCED_DATA_PATH) else 0
        basic_files = len(glob.glob(os.path.join(STOCK_DATA_PATH, "*_intraday.csv"))) if os.path.exists(STOCK_DATA_PATH) else 0
        market_file = 1 if os.path.exists(os.path.join(ENHANCED_DATA_PATH, "market_overview.json")) else 0
        
        return {
            "enhanced_stocks": enhanced_files,
            "basic_stocks": basic_files,
            "market_data": market_file,
            "total_data_sources": enhanced_files + basic_files + market_file,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting API stats: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    # Create directories if they don't exist
    os.makedirs(ENHANCED_DATA_PATH, exist_ok=True)
    os.makedirs(STOCK_DATA_PATH, exist_ok=True)
    
    # Run the API server
    uvicorn.run(
        "stock_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
