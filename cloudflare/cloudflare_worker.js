/**
 * Cloudflare Worker for Stock Data Processing
 * Handles data processing, API endpoints, and real-time updates
 */

// Environment variables
const R2_BUCKET = 'stock-data-bucket'
const KV_NAMESPACE = 'stock_metadata'
const D1_DATABASE = 'stock_data_db'

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Max-Age': '86400',
}

/**
 * Main request handler
 */
async function handleRequest(request, env, ctx) {
  const url = new URL(request.url)
  const path = url.pathname
  const method = request.method

  // Handle CORS preflight
  if (method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: corsHeaders
    })
  }

  try {
    // Route requests based on path
    if (path.startsWith('/api/stocks')) {
      return await handleStockAPI(request, env, ctx)
    } else if (path.startsWith('/api/market')) {
      return await handleMarketAPI(request, env, ctx)
    } else if (path.startsWith('/api/analytics')) {
      return await handleAnalyticsAPI(request, env, ctx)
    } else if (path === '/health') {
      return new Response(JSON.stringify({ status: 'healthy', timestamp: new Date().toISOString() }), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    } else {
      return new Response(JSON.stringify({ error: 'Not found' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
  } catch (error) {
    console.error('Worker error:', error)
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
}

/**
 * Handle stock-related API endpoints
 */
async function handleStockAPI(request, env, ctx) {
  const url = new URL(request.url)
  const path = url.pathname
  const method = request.method

  if (path === '/api/stocks' && method === 'GET') {
    // Get list of all stocks
    return await getAllStocks(env)
  } else if (path.startsWith('/api/stocks/') && method === 'GET') {
    // Get specific stock data
    const ticker = path.split('/')[3]
    return await getStockData(ticker, env)
  } else if (path.startsWith('/api/stocks/') && method === 'POST') {
    // Update stock data
    const ticker = path.split('/')[3]
    const data = await request.json()
    return await updateStockData(ticker, data, env)
  }

  return new Response(JSON.stringify({ error: 'Method not allowed' }), {
    status: 405,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  })
}

/**
 * Handle market-related API endpoints
 */
async function handleMarketAPI(request, env, ctx) {
  const url = new URL(request.url)
  const path = url.pathname
  const method = request.method

  if (path === '/api/market/overview' && method === 'GET') {
    // Get market overview
    return await getMarketOverview(env)
  } else if (path === '/api/market/sectors' && method === 'GET') {
    // Get sector performance
    return await getSectorPerformance(env)
  }

  return new Response(JSON.stringify({ error: 'Method not allowed' }), {
    status: 405,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  })
}

/**
 * Handle analytics API endpoints
 */
async function handleAnalyticsAPI(request, env, ctx) {
  const url = new URL(request.url)
  const path = url.pathname
  const method = request.method

  if (path === '/api/analytics/stats' && method === 'GET') {
    // Get storage statistics
    return await getStorageStats(env)
  } else if (path === '/api/analytics/trends' && method === 'GET') {
    // Get data trends
    return await getDataTrends(env)
  }

  return new Response(JSON.stringify({ error: 'Method not allowed' }), {
    status: 405,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  })
}

/**
 * Get all available stocks
 */
async function getAllStocks(env) {
  try {
    // List objects in R2 bucket
    const objects = await env[R2_BUCKET].list({ prefix: 'stock_data/comprehensive/' })
    
    const stocks = []
    for (const obj of objects.objects) {
      const ticker = obj.key.split('/')[2].split('_')[0]
      if (!stocks.includes(ticker)) {
        stocks.push(ticker)
      }
    }

    return new Response(JSON.stringify({
      stocks: stocks.sort(),
      count: stocks.length,
      timestamp: new Date().toISOString()
    }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    console.error('Error getting stocks:', error)
    return new Response(JSON.stringify({ error: 'Failed to get stocks' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
}

/**
 * Get data for a specific stock
 */
async function getStockData(ticker, env) {
  try {
    // Get the latest data for the ticker
    const objects = await env[R2_BUCKET].list({ 
      prefix: `stock_data/comprehensive/${ticker}_`,
      limit: 1
    })

    if (objects.objects.length === 0) {
      return new Response(JSON.stringify({ error: 'Stock not found' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Get the most recent file
    const latestObject = objects.objects[0]
    const data = await env[R2_BUCKET].get(latestObject.key)
    const stockData = JSON.parse(await data.text())

    return new Response(JSON.stringify({
      ticker: ticker,
      data: stockData,
      last_updated: latestObject.uploaded,
      file_size: latestObject.size
    }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    console.error('Error getting stock data:', error)
    return new Response(JSON.stringify({ error: 'Failed to get stock data' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
}

/**
 * Update stock data
 */
async function updateStockData(ticker, data, env) {
  try {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const key = `stock_data/comprehensive/${ticker}_${timestamp}.json`
    
    // Store in R2
    await env[R2_BUCKET].put(key, JSON.stringify(data), {
      httpMetadata: {
        contentType: 'application/json'
      },
      customMetadata: {
        ticker: ticker,
        timestamp: timestamp,
        upload_date: new Date().toISOString()
      }
    })

    // Store metadata in KV
    const metadata = {
      ticker: ticker,
      file_path: key,
      timestamp: timestamp,
      upload_date: new Date().toISOString()
    }
    
    await env[KV_NAMESPACE].put(`stock_metadata:${ticker}:${timestamp}`, JSON.stringify(metadata))

    return new Response(JSON.stringify({
      success: true,
      ticker: ticker,
      key: key,
      timestamp: timestamp
    }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    console.error('Error updating stock data:', error)
    return new Response(JSON.stringify({ error: 'Failed to update stock data' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
}

/**
 * Get market overview
 */
async function getMarketOverview(env) {
  try {
    // Get market overview data
    const marketData = await env[R2_BUCKET].get('market_data/market_overview.json')
    
    if (marketData) {
      const data = JSON.parse(await marketData.text())
      return new Response(JSON.stringify(data), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    } else {
      return new Response(JSON.stringify({ error: 'Market data not available' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
  } catch (error) {
    console.error('Error getting market overview:', error)
    return new Response(JSON.stringify({ error: 'Failed to get market overview' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
}

/**
 * Get sector performance
 */
async function getSectorPerformance(env) {
  try {
    // Get sector performance data
    const sectorData = await env[R2_BUCKET].get('market_data/sector_performance.json')
    
    if (sectorData) {
      const data = JSON.parse(await sectorData.text())
      return new Response(JSON.stringify(data), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    } else {
      return new Response(JSON.stringify({ error: 'Sector data not available' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }
  } catch (error) {
    console.error('Error getting sector performance:', error)
    return new Response(JSON.stringify({ error: 'Failed to get sector performance' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
}

/**
 * Get storage statistics
 */
async function getStorageStats(env) {
  try {
    const objects = await env[R2_BUCKET].list()
    
    let totalSize = 0
    const dataTypes = {}
    
    for (const obj of objects.objects) {
      totalSize += obj.size
      const keyParts = obj.key.split('/')
      if (keyParts.length >= 2) {
        const dataType = keyParts[1]
        if (!dataTypes[dataType]) {
          dataTypes[dataType] = { count: 0, size: 0 }
        }
        dataTypes[dataType].count++
        dataTypes[dataType].size += obj.size
      }
    }

    return new Response(JSON.stringify({
      total_files: objects.objects.length,
      total_size_bytes: totalSize,
      total_size_mb: Math.round(totalSize / (1024 * 1024) * 100) / 100,
      data_types: dataTypes,
      timestamp: new Date().toISOString()
    }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    console.error('Error getting storage stats:', error)
    return new Response(JSON.stringify({ error: 'Failed to get storage stats' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
}

/**
 * Get data trends
 */
async function getDataTrends(env) {
  try {
    // Get recent uploads from KV
    const keys = await env[KV_NAMESPACE].list({ prefix: 'stock_metadata:' })
    
    const trends = {}
    for (const key of keys.keys) {
      const metadata = await env[KV_NAMESPACE].get(key.name)
      if (metadata) {
        const data = JSON.parse(metadata)
        const date = data.upload_date.split('T')[0]
        if (!trends[date]) {
          trends[date] = { count: 0, tickers: [] }
        }
        trends[date].count++
        if (!trends[date].tickers.includes(data.ticker)) {
          trends[date].tickers.push(data.ticker)
        }
      }
    }

    // Sort by date
    const sortedTrends = Object.entries(trends)
      .sort(([a], [b]) => new Date(b) - new Date(a))
      .slice(0, 7) // Last 7 days

    return new Response(JSON.stringify({
      trends: Object.fromEntries(sortedTrends),
      timestamp: new Date().toISOString()
    }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    console.error('Error getting data trends:', error)
    return new Response(JSON.stringify({ error: 'Failed to get data trends' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
}

// Export the handler
export default {
  fetch: handleRequest
}
