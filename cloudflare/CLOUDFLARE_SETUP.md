# 🌐 Cloudflare Integration Setup Guide

This guide will help you set up Cloudflare services for storing and managing your stock data. The integration includes:

- **R2 Object Storage** - For storing JSON and CSV files
- **KV Namespace** - For metadata and quick lookups
- **D1 Database** - For structured data queries
- **Cloudflare Workers** - For API endpoints and data processing

## 📋 Prerequisites

Before starting, ensure you have:

1. **Cloudflare Account** - Sign up at [cloudflare.com](https://cloudflare.com)
2. **Node.js** (v16 or higher) - Download from [nodejs.org](https://nodejs.org)
3. **npm** - Usually comes with Node.js
4. **Python 3.9+** - For running the setup scripts

## 🚀 Quick Start

### Step 1: Install Wrangler CLI

```bash
npm install -g wrangler
```

### Step 2: Login to Cloudflare

```bash
wrangler login
```

### Step 3: Run the Setup Script

```bash
python cloudflare_setup.py
```

The script will:
- Check prerequisites
- Create configuration files
- Set up R2 bucket
- Create KV namespace
- Set up D1 database
- Deploy the Worker
- Test all services

## ⚙️ Manual Configuration

If you prefer to configure manually or the automated setup fails:

### 1. Create Configuration File

```bash
python cloudflare_config.py
```

This creates `cloudflare_config_sample.json`. Copy it to `cloudflare_config.json` and fill in your values:

```json
{
  "api_token": "your_cloudflare_api_token_here",
  "account_id": "your_cloudflare_account_id_here",
  "zone_id": "your_cloudflare_zone_id_here",
  "r2_access_key_id": "your_r2_access_key_id_here",
  "r2_secret_access_key": "your_r2_secret_access_key_here",
  "r2_endpoint_url": "https://your_account_id.r2.cloudflarestorage.com",
  "r2_bucket_name": "stock-data-bucket",
  "workers_script_name": "stock-data-processor"
}
```

### 2. Get Cloudflare Credentials

#### API Token
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **My Profile** > **API Tokens**
3. Click **Create Token**
4. Use **Custom token** template
5. Add permissions:
   - **Account** > **Cloudflare Workers** > **Edit**
   - **Account** > **R2 Object Storage** > **Edit**
   - **Zone** > **Cloudflare Workers** > **Edit**

#### Account ID
1. In Cloudflare Dashboard, look at the right sidebar
2. Your Account ID is displayed there

#### Zone ID
1. Select your domain in the dashboard
2. Zone ID is shown in the right sidebar

### 3. Create R2 Bucket

```bash
wrangler r2 bucket create stock-data-bucket
```

### 4. Create R2 API Token

1. Go to **R2 Object Storage** in dashboard
2. Click **Manage R2 API tokens**
3. Create new token with appropriate permissions
4. Note the Access Key ID and Secret Access Key

### 5. Create KV Namespace

```bash
wrangler kv:namespace create stock_metadata
```

Copy the namespace ID from the output.

### 6. Create D1 Database

```bash
wrangler d1 create stock_data_db
```

Copy the database ID from the output.

### 7. Update Configuration

Update your `cloudflare_config.json` with the IDs from steps 5-6.

### 8. Deploy Worker

```bash
wrangler deploy
```

## 🔧 Integration with Existing Scrapers

### V1 Scraper Integration

```python
from cloudflare_integration import integrate_with_v1_scraper

# In your V1 scraper
integration = integrate_with_v1_scraper(your_scraper_instance)

# Store data
if hasattr(your_scraper_instance, 'cloudflare_integration'):
    success = your_scraper_instance.cloudflare_integration.store_v1_stock_data(
        ticker, csv_data
    )
```

### V2 Scraper Integration

```python
from cloudflare_integration import integrate_with_v2_scraper

# In your V2 scraper
integration = integrate_with_v2_scraper(your_scraper_instance)

# Store data
if hasattr(your_scraper_instance, 'cloudflare_integration'):
    success = your_scraper_instance.cloudflare_integration.store_v2_stock_data(
        ticker, comprehensive_data
    )
```

## 📊 API Endpoints

Once deployed, your Worker provides these endpoints:

### Stock Data
- `GET /api/stocks` - List all available stocks
- `GET /api/stocks/{ticker}` - Get specific stock data
- `POST /api/stocks/{ticker}` - Update stock data

### Market Data
- `GET /api/market/overview` - Get market overview
- `GET /api/market/sectors` - Get sector performance

### Analytics
- `GET /api/analytics/stats` - Get storage statistics
- `GET /api/analytics/trends` - Get data trends

### Health Check
- `GET /health` - Check service health

## 🔄 Data Migration

### Auto-Migration

```python
from cloudflare_integration import auto_migrate_existing_data

# Migrate all existing data
results = auto_migrate_existing_data()
print(results)
```

### Manual Migration

```python
from cloudflare_integration import CloudflareStockIntegration

integration = CloudflareStockIntegration()

# Migrate V1 data
v1_stats = integration.migrate_existing_data('stock_data', 'v1')

# Migrate V2 data
v2_stats = integration.migrate_existing_data('json_stock_data', 'v2')
```

## 🧹 Maintenance

### Cleanup Old Data

```python
# Remove data older than 30 days
deleted_count = integration.cleanup_old_data(days_old=30)
```

### Create Backups

```python
# Create local backup
success = integration.create_backup("my_backup_folder")
```

### Get Storage Stats

```python
# Get storage statistics
stats = integration.get_storage_summary()
print(stats)
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Wrangler Not Found
```bash
npm install -g wrangler
```

#### 2. Authentication Failed
```bash
wrangler login
```

#### 3. Permission Denied
- Check your API token permissions
- Ensure account has appropriate access levels

#### 4. R2 Bucket Already Exists
- This is normal if you've run setup before
- The script will handle existing buckets

#### 5. Worker Deployment Failed
- Check your `wrangler.toml` configuration
- Ensure all environment variables are set

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Service Status

```bash
# Test R2 access
wrangler r2 bucket list

# Test KV access
wrangler kv:key list --namespace-id YOUR_NAMESPACE_ID

# Test D1 access
wrangler d1 execute stock_data_db --command "SELECT 1"
```

## 📈 Monitoring

### Cloudflare Dashboard
- **R2 Object Storage** - Monitor storage usage and costs
- **Workers** - Check Worker performance and errors
- **Analytics** - View API usage and performance

### Logs
- Worker logs are available in the Cloudflare dashboard
- Local logs are saved to `cloudflare_setup.log`

## 💰 Cost Considerations

### R2 Storage
- **Storage**: $0.015 per GB per month
- **Class A Operations**: $4.50 per million requests
- **Class B Operations**: $0.36 per million requests

### Workers
- **Requests**: 100,000 requests per day free
- **Additional**: $5.00 per million requests

### KV Storage
- **Reads**: 100,000 reads per day free
- **Writes**: 1,000 writes per day free
- **Additional**: $0.50 per million operations

### D1 Database
- **Reads**: 10 million reads per month free
- **Writes**: 1 million writes per month free
- **Additional**: $0.40 per million reads, $5.00 per million writes

## 🔐 Security Best Practices

1. **API Tokens**: Use least-privilege tokens
2. **Environment Variables**: Store secrets securely
3. **CORS**: Configure appropriate CORS policies
4. **Rate Limiting**: Implement rate limiting for public APIs
5. **Data Validation**: Validate all input data

## 📚 Additional Resources

- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)
- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Cloudflare KV Documentation](https://developers.cloudflare.com/workers/configuration/storage/workers-kv/)
- [Cloudflare D1 Documentation](https://developers.cloudflare.com/d1/)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Cloudflare documentation
3. Check the setup logs in `cloudflare_setup.log`
4. Verify your configuration in `cloudflare_config.json`

## 🎯 Next Steps

After successful setup:

1. **Test the API endpoints** with your deployed Worker
2. **Integrate with your scrapers** using the provided functions
3. **Migrate existing data** to Cloudflare storage
4. **Monitor usage** in the Cloudflare dashboard
5. **Set up alerts** for storage limits and costs

---

**Happy coding! 🚀**

If you find this guide helpful, consider giving the repository a star! ⭐
