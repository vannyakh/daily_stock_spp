"""
Network Utilities
Utilities for HTTP requests, connection management, and network operations
"""

import requests
import urllib3
import socket
import ssl
from typing import Dict, List, Optional, Any, Union, Tuple
import time
import logging
from urllib.parse import urlparse, urljoin
import json

logger = logging.getLogger(__name__)

class NetworkUtils:
    """Main network utility class"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3, delay: float = 1.0):
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay = delay
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Setup session with default headers and retry strategy"""
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'StockDataScraper/1.0 (Python)',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Setup retry strategy
        retry_strategy = urllib3.util.Retry(
            total=self.max_retries,
            backoff_factor=self.delay,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        method = method.upper()
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Check if response is successful
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries:
                    time.sleep(self.delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed for {url}")
                    return None
        
        return None
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make GET request"""
        return self.make_request(url, 'GET', **kwargs)
    
    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make POST request"""
        return self.make_request(url, 'POST', **kwargs)
    
    def put(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make PUT request"""
        return self.make_request(url, 'PUT', **kwargs)
    
    def delete(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make DELETE request"""
        return self.make_request(url, 'DELETE', **kwargs)
    
    def download_file(self, url: str, filepath: str, chunk_size: int = 8192) -> bool:
        """Download file from URL"""
        try:
            response = self.get(url, stream=True)
            if not response:
                return False
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"File downloaded successfully: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading file from {url}: {e}")
            return False
    
    def check_url_status(self, url: str) -> Dict[str, Any]:
        """Check URL status and response time"""
        try:
            start_time = time.time()
            response = self.get(url)
            response_time = time.time() - start_time
            
            if response:
                return {
                    'url': url,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'content_length': len(response.content),
                    'headers': dict(response.headers),
                    'is_accessible': True
                }
            else:
                return {
                    'url': url,
                    'status_code': None,
                    'response_time': None,
                    'content_length': None,
                    'headers': {},
                    'is_accessible': False,
                    'error': 'Request failed'
                }
                
        except Exception as e:
            return {
                'url': url,
                'status_code': None,
                'response_time': None,
                'content_length': None,
                'headers': {},
                'is_accessible': False,
                'error': str(e)
            }
    
    def get_json(self, url: str, **kwargs) -> Optional[Dict]:
        """Get JSON response from URL"""
        try:
            response = self.get(url, **kwargs)
            if response and response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                logger.warning(f"Response is not JSON: {url}")
                return None
        except Exception as e:
            logger.error(f"Error getting JSON from {url}: {e}")
            return None
    
    def post_json(self, url: str, data: Dict, **kwargs) -> Optional[Dict]:
        """Post JSON data to URL"""
        try:
            kwargs['json'] = data
            response = self.post(url, **kwargs)
            if response and response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                return {'status_code': response.status_code} if response else None
        except Exception as e:
            logger.error(f"Error posting JSON to {url}: {e}")
            return None

class ConnectionTester:
    """Helper class for testing network connections"""
    
    @staticmethod
    def test_tcp_connection(host: str, port: int, timeout: int = 5) -> bool:
        """Test TCP connection to host:port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.error(f"Error testing TCP connection to {host}:{port}: {e}")
            return False
    
    @staticmethod
    def test_ssl_connection(host: str, port: int = 443, timeout: int = 5) -> Dict[str, Any]:
        """Test SSL connection and get certificate info"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        'host': host,
                        'port': port,
                        'is_accessible': True,
                        'ssl_version': ssock.version(),
                        'cipher': ssock.cipher(),
                        'certificate': {
                            'subject': dict(x[0] for x in cert['subject']),
                            'issuer': dict(x[0] for x in cert['issuer']),
                            'not_before': cert['notBefore'],
                            'not_after': cert['notAfter'],
                            'serial_number': cert['serialNumber']
                        }
                    }
                    
        except Exception as e:
            return {
                'host': host,
                'port': port,
                'is_accessible': False,
                'error': str(e)
            }
    
    @staticmethod
    def test_dns_resolution(hostname: str) -> Dict[str, Any]:
        """Test DNS resolution for hostname"""
        try:
            ip_addresses = socket.gethostbyname_ex(hostname)
            
            return {
                'hostname': hostname,
                'is_resolvable': True,
                'ip_addresses': ip_addresses[2],
                'aliases': ip_addresses[1]
            }
            
        except socket.gaierror as e:
            return {
                'hostname': hostname,
                'is_resolvable': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'hostname': hostname,
                'is_resolvable': False,
                'error': str(e)
            }

class RateLimiter:
    """Helper class for rate limiting requests"""
    
    def __init__(self, max_requests: int, time_window: float):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_make_request(self) -> bool:
        """Check if a request can be made"""
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        # Check if we can make another request
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False
    
    def wait_if_needed(self):
        """Wait if rate limit is reached"""
        while not self.can_make_request():
            time.sleep(0.1)  # Small delay to avoid busy waiting
    
    def get_wait_time(self) -> float:
        """Get time to wait before next request"""
        if len(self.requests) < self.max_requests:
            return 0.0
        
        # Find oldest request
        oldest_request = min(self.requests)
        wait_time = self.time_window - (time.time() - oldest_request)
        return max(0.0, wait_time)

class ProxyManager:
    """Helper class for managing proxy connections"""
    
    def __init__(self):
        self.proxies = []
        self.current_proxy_index = 0
    
    def add_proxy(self, proxy: str, username: str = None, password: str = None):
        """Add proxy to the list"""
        proxy_config = {
            'url': proxy,
            'username': username,
            'password': password,
            'fails': 0,
            'last_used': None
        }
        self.proxies.append(proxy_config)
    
    def get_next_proxy(self) -> Optional[Dict]:
        """Get next available proxy"""
        if not self.proxies:
            return None
        
        # Find proxy with least failures
        available_proxies = [p for p in self.proxies if p['fails'] < 3]
        
        if not available_proxies:
            # Reset all proxy failure counts
            for proxy in self.proxies:
                proxy['fails'] = 0
            available_proxies = self.proxies
        
        # Get next proxy in round-robin fashion
        proxy = available_proxies[self.current_proxy_index % len(available_proxies)]
        self.current_proxy_index += 1
        
        # Update last used time
        proxy['last_used'] = time.time()
        
        return proxy
    
    def mark_proxy_failed(self, proxy_url: str):
        """Mark proxy as failed"""
        for proxy in self.proxies:
            if proxy['url'] == proxy_url:
                proxy['fails'] += 1
                break
    
    def get_proxy_dict(self, proxy_config: Dict) -> Dict[str, str]:
        """Convert proxy config to requests proxy format"""
        if not proxy_config:
            return {}
        
        proxy_url = proxy_config['url']
        
        if proxy_config['username'] and proxy_config['password']:
            # Add authentication to proxy URL
            parsed = urlparse(proxy_url)
            auth_url = f"{parsed.scheme}://{proxy_config['username']}:{proxy_config['password']}@{parsed.netloc}"
            return {
                'http': auth_url,
                'https': auth_url
            }
        else:
            return {
                'http': proxy_url,
                'https': proxy_url
            }

class NetworkMonitor:
    """Helper class for monitoring network performance"""
    
    def __init__(self):
        self.requests = []
        self.errors = []
    
    def log_request(self, url: str, method: str, response_time: float, status_code: int = None):
        """Log request performance"""
        self.requests.append({
            'timestamp': time.time(),
            'url': url,
            'method': method,
            'response_time': response_time,
            'status_code': status_code
        })
        
        # Keep only last 1000 requests
        if len(self.requests) > 1000:
            self.requests = self.requests[-1000:]
    
    def log_error(self, url: str, method: str, error: str, response_time: float = None):
        """Log request error"""
        self.errors.append({
            'timestamp': time.time(),
            'url': url,
            'method': method,
            'error': error,
            'response_time': response_time
        })
        
        # Keep only last 1000 errors
        if len(self.errors) > 1000:
            self.errors = self.errors[-1000:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get network performance statistics"""
        if not self.requests:
            return {}
        
        response_times = [req['response_time'] for req in self.requests if req['response_time']]
        status_codes = [req['status_code'] for req in self.requests if req['status_code']]
        
        stats = {
            'total_requests': len(self.requests),
            'total_errors': len(self.errors),
            'success_rate': (len(self.requests) - len(self.errors)) / len(self.requests) * 100 if self.requests else 0,
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'status_code_distribution': {}
        }
        
        # Calculate status code distribution
        for status_code in status_codes:
            if status_code not in stats['status_code_distribution']:
                stats['status_code_distribution'][status_code] = 0
            stats['status_code_distribution'][status_code] += 1
        
        return stats

# Utility functions
def test_connection(host: str, port: int = 80) -> bool:
    """Quick function to test connection"""
    return ConnectionTester.test_tcp_connection(host, port)

def check_url(url: str) -> Dict[str, Any]:
    """Quick function to check URL status"""
    network_utils = NetworkUtils()
    return network_utils.check_url_status(url)

def download_file(url: str, filepath: str) -> bool:
    """Quick function to download file"""
    network_utils = NetworkUtils()
    return network_utils.download_file(url, filepath)

def get_json(url: str) -> Optional[Dict]:
    """Quick function to get JSON from URL"""
    network_utils = NetworkUtils()
    return network_utils.get_json(url)

def create_rate_limiter(max_requests: int, time_window: float) -> RateLimiter:
    """Quick function to create rate limiter"""
    return RateLimiter(max_requests, time_window)
