"""
Decorator Utilities
Utilities for function enhancement, caching, retry logic, and performance monitoring
"""

import functools
import time
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Union, Callable, TypeVar, ParamSpec
from datetime import datetime, timedelta
import threading
import asyncio
import inspect

logger = logging.getLogger(__name__)

# Type variables for generic decorators
T = TypeVar('T')
P = ParamSpec('P')

class DecoratorUtils:
    """Main decorator utility class"""
    
    @staticmethod
    def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, 
                        backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
               """Decorator to retry function on failure with exponential backoff"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            wait_time = delay * (backoff_factor ** attempt)
                            logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                                         f"Retrying in {wait_time:.2f} seconds...")
                            time.sleep(wait_time)
                        else:
                            logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
                
                # Re-raise the last exception if all attempts failed
                raise last_exception
            
            return wrapper
        return decorator
    
    @staticmethod
    def timeout_handler(timeout_seconds: float, default_value: Any = None):
        """Decorator to handle function timeout"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
                
                # Set signal handler for timeout
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(timeout_seconds))
                
                try:
                    result = func(*args, **kwargs)
                    signal.alarm(0)  # Cancel alarm
                    return result
                except TimeoutError:
                    logger.warning(f"Function {func.__name__} timed out, returning default value")
                    return default_value
                finally:
                    signal.signal(signal.SIGALRM, old_handler)
                    signal.alarm(0)
            
            return wrapper
        return decorator
    
    @staticmethod
    def rate_limit(max_calls: int, time_window: float):
        """Decorator to limit function call rate"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            # Store call timestamps
            call_times = []
            lock = threading.Lock()
            
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                with lock:
                    now = time.time()
                    
                    # Remove old timestamps outside the time window
                    call_times[:] = [t for t in call_times if now - t < time_window]
                    
                    if len(call_times) >= max_calls:
                        # Calculate wait time
                        oldest_call = min(call_times)
                        wait_time = time_window - (now - oldest_call)
                        
                        if wait_time > 0:
                            logger.warning(f"Rate limit reached for {func.__name__}, waiting {wait_time:.2f} seconds")
                            time.sleep(wait_time)
                    
                    # Add current call timestamp
                    call_times.append(time.time())
                
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    @staticmethod
    def cache_result(ttl_seconds: float = 300, max_size: int = 1000, key_func: Callable = None):
        """Decorator to cache function results with TTL and size limit"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            cache = {}
            lock = threading.Lock()
            
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default key generation
                    key_parts = [func.__name__]
                    key_parts.extend([str(arg) for arg in args])
                    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
                    cache_key = hashlib.md5(json.dumps(key_parts, sort_keys=True).encode()).hexdigest()
                
                with lock:
                    # Check cache
                    if cache_key in cache:
                        cached_item = cache[cache_key]
                        if time.time() - cached_item['timestamp'] < ttl_seconds:
                            logger.debug(f"Cache hit for {func.__name__}")
                            return cached_item['value']
                        else:
                            # Expired, remove from cache
                            del cache[cache_key]
                    
                    # Check cache size limit
                    if len(cache) >= max_size:
                        # Remove oldest entries
                        oldest_keys = sorted(cache.keys(), 
                                          key=lambda k: cache[k]['timestamp'])[:len(cache) - max_size + 1]
                        for old_key in oldest_keys:
                            del cache[old_key]
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                
                with lock:
                    cache[cache_key] = {
                        'value': result,
                        'timestamp': time.time()
                    }
                
                logger.debug(f"Cache miss for {func.__name__}, result cached")
                return result
            
            # Add cache management methods
            wrapper.clear_cache = lambda: cache.clear()
            wrapper.get_cache_stats = lambda: {
                'size': len(cache),
                'max_size': max_size,
                'ttl': ttl_seconds
            }
            
            return wrapper
        return decorator
    
    @staticmethod
    def log_function_call(log_args: bool = True, log_result: bool = False, log_time: bool = True):
        """Decorator to log function calls, arguments, and execution time"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                start_time = time.time()
                
                # Log function call
                log_msg = f"Calling {func.__name__}"
                if log_args:
                    args_str = ", ".join([str(arg) for arg in args])
                    kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
                    params = []
                    if args_str:
                        params.append(args_str)
                    if kwargs_str:
                        params.append(kwargs_str)
                    if params:
                        log_msg += f" with parameters: {', '.join(params)}"
                
                logger.info(log_msg)
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Log execution time
                    if log_time:
                        execution_time = time.time() - start_time
                        logger.info(f"{func.__name__} completed in {execution_time:.4f} seconds")
                    
                    # Log result if requested
                    if log_result:
                        result_str = str(result)
                        if len(result_str) > 100:
                            result_str = result_str[:100] + "..."
                        logger.debug(f"{func.__name__} returned: {result_str}")
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {e}")
                    raise
            
            return wrapper
        return decorator
    
    @staticmethod
    def validate_arguments(validation_rules: Dict[str, Callable]):
        """Decorator to validate function arguments"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                # Get function signature
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Validate arguments
                for param_name, validation_func in validation_rules.items():
                    if param_name in bound_args.arguments:
                        value = bound_args.arguments[param_name]
                        if not validation_func(value):
                            raise ValueError(f"Invalid argument '{param_name}': {value}")
                
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    @staticmethod
    def memoize(max_size: int = 128):
        """Simple memoization decorator with size limit"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            cache = {}
            
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                # Create cache key from arguments
                key = (args, tuple(sorted(kwargs.items())))
                
                if key in cache:
                    return cache[key]
                
                result = func(*args, **kwargs)
                
                # Check cache size limit
                if len(cache) >= max_size:
                    # Remove oldest entry (simple FIFO)
                    oldest_key = next(iter(cache))
                    del cache[oldest_key]
                
                cache[key] = result
                return result
            
            # Add cache management methods
            wrapper.clear_cache = lambda: cache.clear()
            wrapper.get_cache_size = lambda: len(cache)
            
            return wrapper
        return decorator

class AsyncDecoratorUtils:
    """Helper class for async function decorators"""
    
    @staticmethod
    def async_retry_on_failure(max_attempts: int = 3, delay: float = 1.0, 
                              backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
        """Async decorator to retry function on failure with exponential backoff"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            wait_time = delay * (backoff_factor ** attempt)
                            logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                                         f"Retrying in {wait_time:.2f} seconds...")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
                
                # Re-raise the last exception if all attempts failed
                raise last_exception
            
            return wrapper
        return decorator
    
    @staticmethod
    def async_timeout_handler(timeout_seconds: float, default_value: Any = None):
        """Async decorator to handle function timeout"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                try:
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
                except asyncio.TimeoutError:
                    logger.warning(f"Function {func.__name__} timed out, returning default value")
                    return default_value
            
            return wrapper
        return decorator
    
    @staticmethod
    def async_rate_limit(max_calls: int, time_window: float):
        """Async decorator to limit function call rate"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            # Store call timestamps
            call_times = []
            lock = asyncio.Lock()
            
            @functools.wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                async with lock:
                    now = time.time()
                    
                    # Remove old timestamps outside the time window
                    call_times[:] = [t for t in call_times if now - t < time_window]
                    
                    if len(call_times) >= max_calls:
                        # Calculate wait time
                        oldest_call = min(call_times)
                        wait_time = time_window - (now - oldest_call)
                        
                        if wait_time > 0:
                            logger.warning(f"Rate limit reached for {func.__name__}, waiting {wait_time:.2f} seconds")
                            await asyncio.sleep(wait_time)
                    
                    # Add current call timestamp
                    call_times.append(time.time())
                
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator

class PerformanceDecoratorUtils:
    """Helper class for performance monitoring decorators"""
    
    @staticmethod
    def measure_time(log_level: str = 'INFO'):
        """Decorator to measure and log function execution time"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    log_func = getattr(logger, log_level.lower(), logger.info)
                    log_func(f"{func.__name__} executed in {execution_time:.4f} seconds")
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {e}")
                    raise
            
            return wrapper
        return decorator
    
    @staticmethod
    def profile_function(profile_name: str = None):
        """Decorator to profile function performance"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            profile_name_final = profile_name or func.__name__
            
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                import cProfile
                import pstats
                import io
                
                # Create profiler
                pr = cProfile.Profile()
                pr.enable()
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    pr.disable()
                    
                    # Get profiling stats
                    s = io.StringIO()
                    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
                    ps.print_stats(10)  # Top 10 functions
                    
                    logger.info(f"Profile for {profile_name_final}:\n{s.getvalue()}")
            
            return wrapper
        return decorator

class SecurityDecoratorUtils:
    """Helper class for security-related decorators"""
    
    @staticmethod
    def require_authentication(auth_check_func: Callable):
        """Decorator to require authentication"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                if not auth_check_func():
                    raise PermissionError("Authentication required")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def require_permission(permission: str, permission_check_func: Callable):
        """Decorator to require specific permission"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                if not permission_check_func(permission):
                    raise PermissionError(f"Permission '{permission}' required")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def sanitize_input(sanitize_func: Callable):
        """Decorator to sanitize function input"""
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                # Sanitize arguments
                sanitized_args = tuple(sanitize_func(arg) for arg in args)
                sanitized_kwargs = {k: sanitize_func(v) for k, v in kwargs.items()}
                
                return func(*sanitized_args, **sanitized_kwargs)
            return wrapper
        return decorator

# Utility functions
def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, 
                    backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
    """Quick function to create retry decorator"""
    return DecoratorUtils.retry_on_failure(max_attempts, delay, backoff_factor, exceptions)

def timeout_handler(timeout_seconds: float, default_value: Any = None):
    """Quick function to create timeout decorator"""
    return DecoratorUtils.timeout_handler(timeout_seconds, default_value)

def rate_limit(max_calls: int, time_window: float):
    """Quick function to create rate limit decorator"""
    return DecoratorUtils.rate_limit(max_calls, time_window)

def cache_result(ttl_seconds: float = 300, max_size: int = 1000):
    """Quick function to create cache decorator"""
    return DecoratorUtils.cache_result(ttl_seconds, max_size)

def log_function_call(log_args: bool = True, log_result: bool = False):
    """Quick function to create logging decorator"""
    return DecoratorUtils.log_function_call(log_args, log_result)

def measure_time(log_level: str = 'INFO'):
    """Quick function to create timing decorator"""
    return PerformanceDecoratorUtils.measure_time(log_level)

def memoize(max_size: int = 128):
    """Quick function to create memoization decorator"""
    return DecoratorUtils.memoize(max_size)
