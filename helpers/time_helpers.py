"""
Time and Date Helpers
Utilities for timezone conversions, date formatting, and time-based operations
"""

import pytz
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Union
import logging

logger = logging.getLogger(__name__)

class TimeUtils:
    """Main time utility class"""
    
    # Common timezones
    TIMEZONES = {
        'UTC': 'UTC',
        'EST': 'America/New_York',
        'PST': 'America/Los_Angeles',
        'CST': 'America/Chicago',
        'MST': 'America/Denver',
        'GMT': 'Europe/London',
        'CET': 'Europe/Paris',
        'JST': 'Asia/Tokyo',
        'HKT': 'Asia/Hong_Kong',
        'IST': 'Asia/Kolkata'
    }
    
    @staticmethod
    def get_current_time(timezone: str = 'UTC') -> datetime:
        """Get current time in specified timezone"""
        try:
            tz = pytz.timezone(TimeUtils.TIMEZONES.get(timezone, timezone))
            return datetime.now(tz)
        except Exception as e:
            logger.error(f"Error getting current time for timezone {timezone}: {e}")
            return datetime.now(pytz.UTC)
    
    @staticmethod
    def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
        """Convert datetime between timezones"""
        try:
            from_timezone = pytz.timezone(TimeUtils.TIMEZONES.get(from_tz, from_tz))
            to_timezone = pytz.timezone(TimeUtils.TIMEZONES.get(to_tz, to_tz))
            
            # Localize the datetime if it's naive
            if dt.tzinfo is None:
                dt = from_timezone.localize(dt)
            
            # Convert to target timezone
            return dt.astimezone(to_timezone)
            
        except Exception as e:
            logger.error(f"Error converting timezone from {from_tz} to {to_tz}: {e}")
            return dt
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S", timezone: str = None) -> str:
        """Format datetime with optional timezone conversion"""
        try:
            if timezone:
                dt = TimeUtils.convert_timezone(dt, 'UTC', timezone)
            
            return dt.strftime(format_str)
            
        except Exception as e:
            logger.error(f"Error formatting datetime: {e}")
            return str(dt)
    
    @staticmethod
    def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S", timezone: str = None) -> Optional[datetime]:
        """Parse datetime string with optional timezone"""
        try:
            dt = datetime.strptime(date_str, format_str)
            
            if timezone:
                tz = pytz.timezone(TimeUtils.TIMEZONES.get(timezone, timezone))
                dt = tz.localize(dt)
            
            return dt
            
        except Exception as e:
            logger.error(f"Error parsing datetime string '{date_str}': {e}")
            return None
    
    @staticmethod
    def get_market_hours(timezone: str = 'EST') -> Dict[str, datetime]:
        """Get market open/close times for a timezone"""
        try:
            tz = pytz.timezone(TimeUtils.TIMEZONES.get(timezone, timezone))
            now = datetime.now(tz)
            
            # Market hours (9:30 AM - 4:00 PM EST)
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            return {
                'open': market_open,
                'close': market_close,
                'timezone': timezone
            }
            
        except Exception as e:
            logger.error(f"Error getting market hours for timezone {timezone}: {e}")
            return {}
    
    @staticmethod
    def is_market_open(timezone: str = 'EST') -> bool:
        """Check if market is currently open"""
        try:
            market_hours = TimeUtils.get_market_hours(timezone)
            if not market_hours:
                return False
            
            current_time = TimeUtils.get_current_time(timezone)
            market_open = market_hours['open']
            market_close = market_hours['close']
            
            # Check if current time is within market hours
            return market_open <= current_time <= market_close
            
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return False
    
    @staticmethod
    def get_next_market_open(timezone: str = 'EST') -> Optional[datetime]:
        """Get next market open time"""
        try:
            market_hours = TimeUtils.get_market_hours(timezone)
            if not market_hours:
                return None
            
            current_time = TimeUtils.get_current_time(timezone)
            market_open = market_hours['open']
            
            # If market is already open today, get next business day
            if current_time >= market_open:
                next_open = market_open + timedelta(days=1)
                # Skip weekends
                while next_open.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    next_open += timedelta(days=1)
                return next_open
            
            return market_open
            
        except Exception as e:
            logger.error(f"Error getting next market open: {e}")
            return None

class DateUtils:
    """Helper class for date operations"""
    
    @staticmethod
    def get_date_range(start_date: date, end_date: date, include_weekends: bool = True) -> List[date]:
        """Get list of dates between start and end dates"""
        try:
            dates = []
            current_date = start_date
            
            while current_date <= end_date:
                if include_weekends or current_date.weekday() < 5:  # Monday = 0, Friday = 4
                    dates.append(current_date)
                current_date += timedelta(days=1)
            
            return dates
            
        except Exception as e:
            logger.error(f"Error getting date range: {e}")
            return []
    
    @staticmethod
    def get_business_days(start_date: date, end_date: date) -> List[date]:
        """Get list of business days between start and end dates"""
        return DateUtils.get_date_range(start_date, end_date, include_weekends=False)
    
    @staticmethod
    def get_quarter_dates(year: int, quarter: int) -> Dict[str, date]:
        """Get start and end dates for a specific quarter"""
        try:
            quarter_starts = {
                1: date(year, 1, 1),
                2: date(year, 4, 1),
                3: date(year, 7, 1),
                4: date(year, 10, 1)
            }
            
            quarter_ends = {
                1: date(year, 3, 31),
                2: date(year, 6, 30),
                3: date(year, 9, 30),
                4: date(year, 12, 31)
            }
            
            if quarter not in quarter_starts:
                raise ValueError(f"Invalid quarter: {quarter}. Must be 1-4.")
            
            return {
                'start': quarter_starts[quarter],
                'end': quarter_ends[quarter],
                'year': year,
                'quarter': quarter
            }
            
        except Exception as e:
            logger.error(f"Error getting quarter dates: {e}")
            return {}
    
    @staticmethod
    def get_fiscal_year_dates(year: int, fiscal_start_month: int = 10) -> Dict[str, date]:
        """Get fiscal year start and end dates"""
        try:
            fiscal_start = date(year, fiscal_start_month, 1)
            fiscal_end = date(year + 1, fiscal_start_month - 1, 30)
            
            # Handle December fiscal start
            if fiscal_start_month == 12:
                fiscal_end = date(year + 1, 11, 30)
            
            return {
                'start': fiscal_start,
                'end': fiscal_end,
                'fiscal_year': year
            }
            
        except Exception as e:
            logger.error(f"Error getting fiscal year dates: {e}")
            return {}
    
    @staticmethod
    def is_holiday(check_date: date, country: str = 'US') -> bool:
        """Check if a date is a holiday (basic US holidays)"""
        try:
            # Basic US market holidays
            us_holidays = [
                date(check_date.year, 1, 1),   # New Year's Day
                date(check_date.year, 7, 4),   # Independence Day
                date(check_date.year, 12, 25), # Christmas Day
            ]
            
            # Add Martin Luther King Jr. Day (third Monday in January)
            mlk_day = DateUtils._get_nth_weekday(check_date.year, 1, 0, 3)  # Monday = 0
            us_holidays.append(mlk_day)
            
            # Add Memorial Day (last Monday in May)
            memorial_day = DateUtils._get_nth_weekday(check_date.year, 5, 0, -1)  # Last Monday
            us_holidays.append(memorial_day)
            
            # Add Labor Day (first Monday in September)
            labor_day = DateUtils._get_nth_weekday(check_date.year, 9, 0, 1)  # First Monday
            us_holidays.append(labor_day)
            
            # Add Thanksgiving (fourth Thursday in November)
            thanksgiving = DateUtils._get_nth_weekday(check_date.year, 11, 3, 4)  # Thursday = 3
            us_holidays.append(thanksgiving)
            
            return check_date in us_holidays
            
        except Exception as e:
            logger.error(f"Error checking holiday status: {e}")
            return False
    
    @staticmethod
    def _get_nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
        """Get the nth occurrence of a weekday in a month"""
        # weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday
        # n: 1=first, 2=second, ..., -1=last
        
        if n == -1:
            # Get last occurrence
            last_day = date(year, month + 1, 1) - timedelta(days=1)
            while last_day.weekday() != weekday:
                last_day -= timedelta(days=1)
            return last_day
        else:
            # Get nth occurrence
            first_day = date(year, month, 1)
            days_until_weekday = (weekday - first_day.weekday()) % 7
            target_day = first_day + timedelta(days=days_until_weekday + (n - 1) * 7)
            return target_day

class TimeFormatter:
    """Helper class for time formatting"""
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format"""
        try:
            if seconds < 60:
                return f"{seconds:.1f}s"
            elif seconds < 3600:
                minutes = seconds / 60
                return f"{minutes:.1f}m"
            elif seconds < 86400:
                hours = seconds / 3600
                return f"{hours:.1f}h"
            else:
                days = seconds / 86400
                return f"{days:.1f}d"
                
        except Exception as e:
            logger.error(f"Error formatting duration: {e}")
            return str(seconds)
    
    @staticmethod
    def format_timestamp(timestamp: Union[datetime, float, int], format_str: str = None) -> str:
        """Format timestamp in various formats"""
        try:
            if isinstance(timestamp, (int, float)):
                dt = datetime.fromtimestamp(timestamp)
            else:
                dt = timestamp
            
            if format_str:
                return dt.strftime(format_str)
            else:
                return dt.isoformat()
                
        except Exception as e:
            logger.error(f"Error formatting timestamp: {e}")
            return str(timestamp)
    
    @staticmethod
    def get_relative_time(dt: datetime) -> str:
        """Get relative time description (e.g., '2 hours ago')"""
        try:
            now = datetime.now()
            diff = now - dt
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                return "just now"
                
        except Exception as e:
            logger.error(f"Error getting relative time: {e}")
            return str(dt)

class MarketTimeUtils:
    """Helper class for market-specific time operations"""
    
    @staticmethod
    def get_market_session_times(timezone: str = 'EST') -> Dict[str, Dict[str, datetime]]:
        """Get market session times (pre-market, regular, after-hours)"""
        try:
            tz = pytz.timezone(TimeUtils.TIMEZONES.get(timezone, timezone))
            now = datetime.now(tz)
            
            # Regular market hours
            regular_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            regular_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            # Pre-market (4:00 AM - 9:30 AM)
            pre_market_open = now.replace(hour=4, minute=0, second=0, microsecond=0)
            pre_market_close = regular_open
            
            # After-hours (4:00 PM - 8:00 PM)
            after_hours_open = regular_close
            after_hours_close = now.replace(hour=20, minute=0, second=0, microsecond=0)
            
            return {
                'pre_market': {
                    'open': pre_market_open,
                    'close': pre_market_close
                },
                'regular': {
                    'open': regular_open,
                    'close': regular_close
                },
                'after_hours': {
                    'open': after_hours_open,
                    'close': after_hours_close
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting market session times: {e}")
            return {}
    
    @staticmethod
    def get_current_market_session(timezone: str = 'EST') -> str:
        """Get current market session"""
        try:
            session_times = MarketTimeUtils.get_market_session_times(timezone)
            if not session_times:
                return "unknown"
            
            current_time = TimeUtils.get_current_time(timezone)
            
            for session, times in session_times.items():
                if times['open'] <= current_time <= times['close']:
                    return session
            
            return "closed"
            
        except Exception as e:
            logger.error(f"Error getting current market session: {e}")
            return "unknown"
    
    @staticmethod
    def get_market_holidays(year: int) -> List[date]:
        """Get list of market holidays for a year"""
        try:
            holidays = []
            
            # Check each business day of the year
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            
            for check_date in DateUtils.get_business_days(start_date, end_date):
                if DateUtils.is_holiday(check_date):
                    holidays.append(check_date)
            
            return holidays
            
        except Exception as e:
            logger.error(f"Error getting market holidays: {e}")
            return []

# Utility functions
def get_current_time(timezone: str = 'UTC') -> datetime:
    """Quick function to get current time"""
    return TimeUtils.get_current_time(timezone)

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Quick function to format datetime"""
    return TimeUtils.format_datetime(dt, format_str)

def is_market_open(timezone: str = 'EST') -> bool:
    """Quick function to check if market is open"""
    return TimeUtils.is_market_open(timezone)

def get_business_days(start_date: date, end_date: date) -> List[date]:
    """Quick function to get business days"""
    return DateUtils.get_business_days(start_date, end_date)

def format_duration(seconds: float) -> str:
    """Quick function to format duration"""
    return TimeFormatter.format_duration(seconds)
