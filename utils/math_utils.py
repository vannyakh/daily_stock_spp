"""
Mathematical Utilities
Utilities for financial calculations, statistics, and mathematical operations
"""

import math
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from decimal import Decimal, getcontext
import statistics

logger = logging.getLogger(__name__)

# Set precision for decimal calculations
getcontext().prec = 28

class MathUtils:
    """Main mathematical utility class"""
    
    @staticmethod
    def round_to_decimals(value: float, decimals: int = 2) -> float:
        """Round value to specified number of decimal places"""
        try:
            return round(value, decimals)
        except Exception as e:
            logger.error(f"Error rounding value {value}: {e}")
            return value
    
    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """Calculate percentage change between two values"""
        try:
            if old_value == 0:
                return float('inf') if new_value > 0 else float('-inf') if new_value < 0 else 0
            
            return ((new_value - old_value) / old_value) * 100
        except Exception as e:
            logger.error(f"Error calculating percentage change: {e}")
            return 0.0
    
    @staticmethod
    def calculate_compound_growth_rate(initial_value: float, final_value: float, periods: int) -> float:
        """Calculate compound annual growth rate (CAGR)"""
        try:
            if initial_value <= 0 or periods <= 0:
                return 0.0
            
            growth_rate = (final_value / initial_value) ** (1 / periods) - 1
            return growth_rate * 100
        except Exception as e:
            logger.error(f"Error calculating CAGR: {e}")
            return 0.0
    
    @staticmethod
    def calculate_moving_average(values: List[float], window: int) -> List[float]:
        """Calculate moving average for a list of values"""
        try:
            if not values or window <= 0 or window > len(values):
                return []
            
            moving_averages = []
            for i in range(window - 1, len(values)):
                window_values = values[i - window + 1:i + 1]
                moving_averages.append(sum(window_values) / window)
            
            return moving_averages
        except Exception as e:
            logger.error(f"Error calculating moving average: {e}")
            return []
    
    @staticmethod
    def calculate_exponential_moving_average(values: List[float], alpha: float) -> List[float]:
        """Calculate exponential moving average"""
        try:
            if not values or alpha < 0 or alpha > 1:
                return []
            
            ema = [values[0]]  # First value is the same
            
            for i in range(1, len(values)):
                ema_value = alpha * values[i] + (1 - alpha) * ema[i - 1]
                ema.append(ema_value)
            
            return ema
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return []
    
    @staticmethod
    def calculate_standard_deviation(values: List[float]) -> float:
        """Calculate standard deviation of values"""
        try:
            if not values or len(values) < 2:
                return 0.0
            
            mean = sum(values) / len(values)
            squared_diff_sum = sum((x - mean) ** 2 for x in values)
            variance = squared_diff_sum / (len(values) - 1)  # Sample variance
            return math.sqrt(variance)
        except Exception as e:
            logger.error(f"Error calculating standard deviation: {e}")
            return 0.0
    
    @staticmethod
    def calculate_variance(values: List[float]) -> float:
        """Calculate variance of values"""
        try:
            if not values or len(values) < 2:
                return 0.0
            
            mean = sum(values) / len(values)
            squared_diff_sum = sum((x - mean) ** 2 for x in values)
            return squared_diff_sum / (len(values) - 1)  # Sample variance
        except Exception as e:
            logger.error(f"Error calculating variance: {e}")
            return 0.0
    
    @staticmethod
    def calculate_correlation(x_values: List[float], y_values: List[float]) -> float:
        """Calculate correlation coefficient between two lists of values"""
        try:
            if len(x_values) != len(y_values) or len(x_values) < 2:
                return 0.0
            
            n = len(x_values)
            x_mean = sum(x_values) / n
            y_mean = sum(y_values) / n
            
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
            x_variance = sum((x - x_mean) ** 2 for x in x_values)
            y_variance = sum((y - y_mean) ** 2 for y in y_values)
            
            denominator = math.sqrt(x_variance * y_variance)
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0.0
    
    @staticmethod
    def calculate_median(values: List[float]) -> float:
        """Calculate median of values"""
        try:
            if not values:
                return 0.0
            
            sorted_values = sorted(values)
            n = len(sorted_values)
            
            if n % 2 == 0:
                # Even number of values
                mid1 = sorted_values[n // 2 - 1]
                mid2 = sorted_values[n // 2]
                return (mid1 + mid2) / 2
            else:
                # Odd number of values
                return sorted_values[n // 2]
        except Exception as e:
            logger.error(f"Error calculating median: {e}")
            return 0.0
    
    @staticmethod
    def calculate_percentile(values: List[float], percentile: float) -> float:
        """Calculate percentile value from list"""
        try:
            if not values or percentile < 0 or percentile > 100:
                return 0.0
            
            sorted_values = sorted(values)
            n = len(sorted_values)
            
            if n == 1:
                return sorted_values[0]
            
            # Calculate position
            position = (percentile / 100) * (n - 1)
            
            if position.is_integer():
                return sorted_values[int(position)]
            else:
                # Interpolate between two values
                lower_pos = int(position)
                upper_pos = lower_pos + 1
                weight = position - lower_pos
                
                lower_val = sorted_values[lower_pos]
                upper_val = sorted_values[upper_pos]
                
                return lower_val + weight * (upper_val - lower_val)
        except Exception as e:
            logger.error(f"Error calculating percentile: {e}")
            return 0.0

class FinancialMath:
    """Helper class for financial calculations"""
    
    @staticmethod
    def calculate_present_value(future_value: float, rate: float, periods: int) -> float:
        """Calculate present value using discount rate"""
        try:
            if rate == 0:
                return future_value
            
            return future_value / ((1 + rate) ** periods)
        except Exception as e:
            logger.error(f"Error calculating present value: {e}")
            return 0.0
    
    @staticmethod
    def calculate_future_value(present_value: float, rate: float, periods: int) -> float:
        """Calculate future value using interest rate"""
        try:
            if rate == 0:
                return present_value
            
            return present_value * ((1 + rate) ** periods)
        except Exception as e:
            logger.error(f"Error calculating future value: {e}")
            return 0.0
    
    @staticmethod
    def calculate_annuity_payment(present_value: float, rate: float, periods: int) -> float:
        """Calculate annuity payment amount"""
        try:
            if rate == 0:
                return present_value / periods
            
            if rate > 0:
                return present_value * (rate * (1 + rate) ** periods) / ((1 + rate) ** periods - 1)
            else:
                return present_value / periods
        except Exception as e:
            logger.error(f"Error calculating annuity payment: {e}")
            return 0.0
    
    @staticmethod
    def calculate_internal_rate_of_return(cash_flows: List[float], guess: float = 0.1) -> float:
        """Calculate internal rate of return using Newton-Raphson method"""
        try:
            if not cash_flows or len(cash_flows) < 2:
                return 0.0
            
            def npv(rate):
                return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))
            
            def npv_derivative(rate):
                return sum(-i * cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cash_flows))
            
            rate = guess
            for _ in range(100):  # Max 100 iterations
                npv_val = npv(rate)
                if abs(npv_val) < 1e-10:
                    break
                
                derivative = npv_derivative(rate)
                if abs(derivative) < 1e-10:
                    break
                
                rate = rate - npv_val / derivative
                
                # Prevent extreme values
                if rate < -0.99 or rate > 10:
                    break
            
            return rate
        except Exception as e:
            logger.error(f"Error calculating IRR: {e}")
            return 0.0
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio"""
        try:
            if not returns:
                return 0.0
            
            avg_return = sum(returns) / len(returns)
            excess_return = avg_return - risk_free_rate
            
            if excess_return <= 0:
                return 0.0
            
            std_dev = MathUtils.calculate_standard_deviation(returns)
            if std_dev == 0:
                return 0.0
            
            return excess_return / std_dev
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {e}")
            return 0.0
    
    @staticmethod
    def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        """Calculate Sortino ratio (downside deviation)"""
        try:
            if not returns:
                return 0.0
            
            avg_return = sum(returns) / len(returns)
            excess_return = avg_return - risk_free_rate
            
            if excess_return <= 0:
                return 0.0
            
            # Calculate downside deviation
            downside_returns = [r for r in returns if r < avg_return]
            if not downside_returns:
                return float('inf')
            
            downside_variance = sum((r - avg_return) ** 2 for r in downside_returns) / len(downside_returns)
            downside_deviation = math.sqrt(downside_variance)
            
            if downside_deviation == 0:
                return 0.0
            
            return excess_return / downside_deviation
        except Exception as e:
            logger.error(f"Error calculating Sortino ratio: {e}")
            return 0.0
    
    @staticmethod
    def calculate_max_drawdown(values: List[float]) -> float:
        """Calculate maximum drawdown from peak"""
        try:
            if not values or len(values) < 2:
                return 0.0
            
            peak = values[0]
            max_drawdown = 0.0
            
            for value in values:
                if value > peak:
                    peak = value
                else:
                    drawdown = (peak - value) / peak
                    max_drawdown = max(max_drawdown, drawdown)
            
            return max_drawdown * 100  # Return as percentage
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
    
    @staticmethod
    def calculate_beta(asset_returns: List[float], market_returns: List[float]) -> float:
        """Calculate beta (systematic risk)"""
        try:
            if len(asset_returns) != len(market_returns) or len(asset_returns) < 2:
                return 0.0
            
            # Calculate covariance and market variance
            asset_mean = sum(asset_returns) / len(asset_returns)
            market_mean = sum(market_returns) / len(market_returns)
            
            covariance = sum((a - asset_mean) * (m - market_mean) 
                           for a, m in zip(asset_returns, market_returns)) / (len(asset_returns) - 1)
            
            market_variance = sum((m - market_mean) ** 2 for m in market_returns) / (len(market_returns) - 1)
            
            if market_variance == 0:
                return 0.0
            
            return covariance / market_variance
        except Exception as e:
            logger.error(f"Error calculating beta: {e}")
            return 0.0

class StatisticsUtils:
    """Helper class for statistical calculations"""
    
    @staticmethod
    def calculate_skewness(values: List[float]) -> float:
        """Calculate skewness (measure of distribution asymmetry)"""
        try:
            if not values or len(values) < 3:
                return 0.0
            
            mean = sum(values) / len(values)
            std_dev = MathUtils.calculate_standard_deviation(values)
            
            if std_dev == 0:
                return 0.0
            
            n = len(values)
            skewness = sum(((x - mean) / std_dev) ** 3 for x in values) / n
            
            # Apply bias correction for small samples
            if n > 3:
                skewness = skewness * math.sqrt(n * (n - 1)) / (n - 2)
            
            return skewness
        except Exception as e:
            logger.error(f"Error calculating skewness: {e}")
            return 0.0
    
    @staticmethod
    def calculate_kurtosis(values: List[float]) -> float:
        """Calculate kurtosis (measure of distribution tail weight)"""
        try:
            if not values or len(values) < 4:
                return 0.0
            
            mean = sum(values) / len(values)
            std_dev = MathUtils.calculate_standard_deviation(values)
            
            if std_dev == 0:
                return 0.0
            
            n = len(values)
            kurtosis = sum(((x - mean) / std_dev) ** 4 for x in values) / n - 3
            
            # Apply bias correction for small samples
            if n > 4:
                kurtosis = (kurtosis * (n + 1) + 6) / (n - 3)
            
            return kurtosis
        except Exception as e:
            logger.error(f"Error calculating kurtosis: {e}")
            return 0.0
    
    @staticmethod
    def calculate_confidence_interval(values: List[float], confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for mean"""
        try:
            if not values or len(values) < 2:
                return (0.0, 0.0)
            
            mean = sum(values) / len(values)
            std_dev = MathUtils.calculate_standard_deviation(values)
            n = len(values)
            
            # Z-score for confidence level (approximate)
            z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
            z_score = z_scores.get(confidence, 1.96)
            
            margin_of_error = z_score * (std_dev / math.sqrt(n))
            
            return (mean - margin_of_error, mean + margin_of_error)
        except Exception as e:
            logger.error(f"Error calculating confidence interval: {e}")
            return (0.0, 0.0)
    
    @staticmethod
    def calculate_outliers(values: List[float], method: str = 'iqr') -> List[int]:
        """Find outlier indices using specified method"""
        try:
            if not values or len(values) < 4:
                return []
            
            if method == 'iqr':
                # Interquartile Range method
                q1 = MathUtils.calculate_percentile(values, 25)
                q3 = MathUtils.calculate_percentile(values, 75)
                iqr = q3 - q1
                
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = [i for i, x in enumerate(values) if x < lower_bound or x > upper_bound]
                
            elif method == 'zscore':
                # Z-score method
                mean = sum(values) / len(values)
                std_dev = MathUtils.calculate_standard_deviation(values)
                
                if std_dev == 0:
                    return []
                
                outliers = [i for i, x in enumerate(values) if abs((x - mean) / std_dev) > 3]
                
            else:
                logger.warning(f"Unknown outlier detection method: {method}")
                return []
            
            return outliers
        except Exception as e:
            logger.error(f"Error calculating outliers: {e}")
            return []

class DecimalMath:
    """Helper class for high-precision decimal calculations"""
    
    @staticmethod
    def decimal_round(value: Union[float, str, Decimal], precision: int = 2) -> Decimal:
        """Round decimal value to specified precision"""
        try:
            if isinstance(value, str):
                decimal_value = Decimal(value)
            elif isinstance(value, float):
                decimal_value = Decimal(str(value))
            else:
                decimal_value = value
            
            return decimal_value.quantize(Decimal('0.01'))
        except Exception as e:
            logger.error(f"Error rounding decimal value: {e}")
            return Decimal('0')
    
    @staticmethod
    def decimal_sum(values: List[Union[float, str, Decimal]]) -> Decimal:
        """Sum list of values with decimal precision"""
        try:
            decimal_values = []
            for value in values:
                if isinstance(value, str):
                    decimal_values.append(Decimal(value))
                elif isinstance(value, float):
                    decimal_values.append(Decimal(str(value)))
                else:
                    decimal_values.append(value)
            
            return sum(decimal_values)
        except Exception as e:
            logger.error(f"Error calculating decimal sum: {e}")
            return Decimal('0')
    
    @staticmethod
    def decimal_average(values: List[Union[float, str, Decimal]]) -> Decimal:
        """Calculate average with decimal precision"""
        try:
            if not values:
                return Decimal('0')
            
            total = DecimalMath.decimal_sum(values)
            count = Decimal(str(len(values)))
            
            return total / count
        except Exception as e:
            logger.error(f"Error calculating decimal average: {e}")
            return Decimal('0')

# Utility functions
def round_number(value: float, decimals: int = 2) -> float:
    """Quick function to round number"""
    return MathUtils.round_to_decimals(value, decimals)

def percentage_change(old_value: float, new_value: float) -> float:
    """Quick function to calculate percentage change"""
    return MathUtils.calculate_percentage_change(old_value, new_value)

def moving_average(values: List[float], window: int) -> List[float]:
    """Quick function to calculate moving average"""
    return MathUtils.calculate_moving_average(values, window)

def standard_deviation(values: List[float]) -> float:
    """Quick function to calculate standard deviation"""
    return MathUtils.calculate_standard_deviation(values)

def present_value(future_value: float, rate: float, periods: int) -> float:
    """Quick function to calculate present value"""
    return FinancialMath.calculate_present_value(future_value, rate, periods)

def sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
    """Quick function to calculate Sharpe ratio"""
    return FinancialMath.calculate_sharpe_ratio(returns, risk_free_rate)

def max_drawdown(values: List[float]) -> float:
    """Quick function to calculate maximum drawdown"""
    return FinancialMath.calculate_max_drawdown(values)
