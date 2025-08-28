"""
Validation Helpers
Utilities for data validation, input sanitization, and error checking
"""

import re
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Main data validation utility class"""
    
    @staticmethod
    def validate_ticker(ticker: str) -> bool:
        """Validate stock ticker symbol"""
        if not ticker or not isinstance(ticker, str):
            return False
        
        # Ticker should be 1-5 characters, alphanumeric
        pattern = r'^[A-Z]{1,5}$'
        return bool(re.match(pattern, ticker.upper()))
    
    @staticmethod
    def validate_date(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
        """Validate date string format"""
        try:
            datetime.strptime(date_str, format_str)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_numeric(value: Any, min_value: float = None, max_value: float = None) -> bool:
        """Validate numeric value with optional range"""
        try:
            num = float(value)
            
            if min_value is not None and num < min_value:
                return False
            if max_value is not None and num > max_value:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        if not email or not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        if not url or not isinstance(url, str):
            return False
        
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone or not isinstance(phone, str):
            return False
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Check if it's a valid length (7-15 digits)
        return 7 <= len(digits) <= 15
    
    @staticmethod
    def validate_stock_data(data: Dict) -> Dict[str, Any]:
        """Validate stock data structure and return validation results"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'missing_fields': []
        }
        
        required_fields = ['ticker', 'data']
        optional_fields = ['info', 'metadata', 'timestamp']
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                validation_result['missing_fields'].append(field)
                validation_result['is_valid'] = False
        
        # Validate ticker
        if 'ticker' in data:
            if not DataValidator.validate_ticker(data['ticker']):
                validation_result['errors'].append(f"Invalid ticker format: {data['ticker']}")
                validation_result['is_valid'] = False
        
        # Validate data structure
        if 'data' in data:
            if not isinstance(data['data'], (list, dict)):
                validation_result['errors'].append("Data field must be a list or dictionary")
                validation_result['is_valid'] = False
        
        # Check for warnings
        if 'timestamp' in data:
            if not DataValidator.validate_date(data['timestamp']):
                validation_result['warnings'].append(f"Invalid timestamp format: {data['timestamp']}")
        
        return validation_result
    
    @staticmethod
    def validate_csv_data(data: List[Dict]) -> Dict[str, Any]:
        """Validate CSV data structure"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'row_count': len(data),
            'column_count': 0,
            'columns': []
        }
        
        if not data:
            validation_result['errors'].append("Empty data")
            validation_result['is_valid'] = False
            return validation_result
        
        # Get columns from first row
        first_row = data[0]
        validation_result['columns'] = list(first_row.keys())
        validation_result['column_count'] = len(first_row.keys())
        
        # Check all rows have same columns
        for i, row in enumerate(data):
            if set(row.keys()) != set(first_row.keys()):
                validation_result['errors'].append(f"Row {i+1} has different columns")
                validation_result['is_valid'] = False
        
        # Check for empty values in required fields
        required_fields = ['Date', 'Close']
        for field in required_fields:
            if field in first_row.keys():
                empty_count = sum(1 for row in data if not row.get(field))
                if empty_count > 0:
                    validation_result['warnings'].append(f"{empty_count} rows have empty {field} values")
        
        return validation_result

class InputSanitizer:
    """Helper class for input sanitization"""
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(input_str, str):
            return ""
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', input_str)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file operations"""
        if not isinstance(filename, str):
            return "unnamed_file"
        
        # Remove or replace unsafe characters
        unsafe_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(unsafe_chars, '_', filename)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Ensure filename is not empty
        if not sanitized:
            sanitized = "unnamed_file"
        
        return sanitized
    
    @staticmethod
    def sanitize_json_key(key: str) -> str:
        """Sanitize JSON key for safe operations"""
        if not isinstance(key, str):
            return "key"
        
        # Remove unsafe characters for JSON keys
        unsafe_chars = r'[^a-zA-Z0-9_-]'
        sanitized = re.sub(unsafe_chars, '_', key)
        
        # Ensure key doesn't start with number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"key_{sanitized}"
        
        return sanitized or "key"
    
    @staticmethod
    def sanitize_sql_value(value: Any) -> str:
        """Sanitize value for SQL operations (basic protection)"""
        if value is None:
            return "NULL"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return str(value).upper()
        elif isinstance(value, (datetime, date)):
            return f"'{value.isoformat()}'"
        else:
            # Basic SQL injection protection
            string_value = str(value)
            # Escape single quotes
            string_value = string_value.replace("'", "''")
            return f"'{string_value}'"

class ErrorChecker:
    """Helper class for error checking and handling"""
    
    @staticmethod
    def check_data_consistency(data: List[Dict], key: str) -> Dict[str, Any]:
        """Check data consistency for a specific key"""
        result = {
            'is_consistent': True,
            'errors': [],
            'null_count': 0,
            'unique_values': set(),
            'data_types': set()
        }
        
        for i, row in enumerate(data):
            value = row.get(key)
            
            # Check for null values
            if value is None or value == "":
                result['null_count'] += 1
            
            # Track unique values
            if value is not None:
                result['unique_values'].add(value)
                result['data_types'].add(type(value).__name__)
        
        # Check for consistency issues
        if len(result['data_types']) > 1:
            result['is_consistent'] = False
            result['errors'].append(f"Multiple data types found: {result['data_types']}")
        
        if result['null_count'] > len(data) * 0.5:  # More than 50% null
            result['warnings'] = [f"High null count: {result['null_count']}/{len(data)}"]
        
        return result
    
    @staticmethod
    def check_data_range(data: List[Dict], key: str, expected_range: tuple = None) -> Dict[str, Any]:
        """Check if data values are within expected range"""
        result = {
            'is_in_range': True,
            'errors': [],
            'min_value': None,
            'max_value': None,
            'out_of_range_count': 0
        }
        
        numeric_values = []
        
        for row in data:
            value = row.get(key)
            if isinstance(value, (int, float)) and value is not None:
                numeric_values.append(value)
        
        if not numeric_values:
            result['errors'].append(f"No numeric values found for key: {key}")
            return result
        
        result['min_value'] = min(numeric_values)
        result['max_value'] = max(numeric_values)
        
        if expected_range:
            min_expected, max_expected = expected_range
            out_of_range = [v for v in numeric_values if v < min_expected or v > max_expected]
            result['out_of_range_count'] = len(out_of_range)
            
            if out_of_range:
                result['is_in_range'] = False
                result['errors'].append(f"{len(out_of_range)} values out of expected range [{min_expected}, {max_expected}]")
        
        return result
    
    @staticmethod
    def check_data_completeness(data: List[Dict], required_keys: List[str]) -> Dict[str, Any]:
        """Check data completeness for required keys"""
        result = {
            'is_complete': True,
            'missing_keys': [],
            'completeness_score': 0.0
        }
        
        total_fields = len(data) * len(required_keys)
        missing_fields = 0
        
        for row in data:
            for key in required_keys:
                if key not in row or row[key] is None or row[key] == "":
                    missing_fields += 1
        
        result['completeness_score'] = (total_fields - missing_fields) / total_fields
        
        if result['completeness_score'] < 0.9:  # Less than 90% complete
            result['is_complete'] = False
            result['missing_keys'] = [key for key in required_keys if any(key not in row or row.get(key) is None or row.get(key) == "" for row in data)]
        
        return result

class SchemaValidator:
    """Helper class for schema validation"""
    
    @staticmethod
    def validate_schema(data: Any, schema: Dict) -> Dict[str, Any]:
        """Validate data against a schema definition"""
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            SchemaValidator._validate_schema_recursive(data, schema, result, "")
        except Exception as e:
            result['errors'].append(f"Schema validation error: {e}")
            result['is_valid'] = False
        
        return result
    
    @staticmethod
    def _validate_schema_recursive(data: Any, schema: Dict, result: Dict, path: str):
        """Recursively validate schema"""
        schema_type = schema.get('type')
        
        if schema_type == 'object':
            if not isinstance(data, dict):
                result['errors'].append(f"{path}: Expected object, got {type(data).__name__}")
                result['is_valid'] = False
                return
            
            required_fields = schema.get('required', [])
            properties = schema.get('properties', {})
            
            # Check required fields
            for field in required_fields:
                if field not in data:
                    result['errors'].append(f"{path}.{field}: Required field missing")
                    result['is_valid'] = False
            
            # Validate properties
            for field, value in data.items():
                if field in properties:
                    field_path = f"{path}.{field}" if path else field
                    SchemaValidator._validate_schema_recursive(value, properties[field], result, field_path)
        
        elif schema_type == 'array':
            if not isinstance(data, list):
                result['errors'].append(f"{path}: Expected array, got {type(data).__name__}")
                result['is_valid'] = False
                return
            
            items_schema = schema.get('items')
            if items_schema:
                for i, item in enumerate(data):
                    item_path = f"{path}[{i}]"
                    SchemaValidator._validate_schema_recursive(item, items_schema, result, item_path)
        
        elif schema_type == 'string':
            if not isinstance(data, str):
                result['errors'].append(f"{path}: Expected string, got {type(data).__name__}")
                result['is_valid'] = False
                return
            
            # Check string constraints
            if 'minLength' in schema and len(data) < schema['minLength']:
                result['errors'].append(f"{path}: String too short (min: {schema['minLength']})")
                result['is_valid'] = False
            
            if 'maxLength' in schema and len(data) > schema['maxLength']:
                result['errors'].append(f"{path}: String too long (max: {schema['maxLength']})")
                result['is_valid'] = False
        
        elif schema_type == 'number':
            if not isinstance(data, (int, float)):
                result['errors'].append(f"{path}: Expected number, got {type(data).__name__}")
                result['is_valid'] = False
                return
            
            # Check number constraints
            if 'minimum' in schema and data < schema['minimum']:
                result['errors'].append(f"{path}: Value too small (min: {schema['minimum']})")
                result['is_valid'] = False
            
            if 'maximum' in schema and data > schema['maximum']:
                result['errors'].append(f"{path}: Value too large (max: {schema['maximum']})")
                result['is_valid'] = False
        
        elif schema_type == 'boolean':
            if not isinstance(data, bool):
                result['errors'].append(f"{path}: Expected boolean, got {type(data).__name__}")
                result['is_valid'] = False

# Utility functions
def validate_stock_ticker(ticker: str) -> bool:
    """Quick validation for stock ticker"""
    return DataValidator.validate_ticker(ticker)

def validate_date_range(start_date: str, end_date: str) -> bool:
    """Validate date range"""
    if not (DataValidator.validate_date(start_date) and DataValidator.validate_date(end_date)):
        return False
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    return start <= end

def validate_numeric_range(value: Any, min_val: float, max_val: float) -> bool:
    """Quick validation for numeric range"""
    return DataValidator.validate_numeric(value, min_val, max_val)

def sanitize_input(input_data: str) -> str:
    """Quick sanitization for input data"""
    return InputSanitizer.sanitize_string(input_data)
