# V2 Enhanced Stock Data API Dockerfile
# Use Python 3.9 slim image for smaller size
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV API_PORT=8000
ENV API_VERSION=v2

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy V2 application code
COPY v2/stock_api_server.py .
COPY stock_data/ ./stock_data/
COPY json_stock_data/ ./json_stock_data/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose the API port
EXPOSE $API_PORT

# Health check for V2 API
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$API_PORT/ || exit 1

# Run the V2 API
CMD ["python", "stock_api_server.py"]
