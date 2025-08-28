"""
String Utilities
Utilities for text manipulation, formatting, and text analysis
"""

import re
import unicodedata
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from datetime import datetime
import hashlib
import base64

logger = logging.getLogger(__name__)

class StringUtils:
    """Main string utility class"""
    
    @staticmethod
    def clean_string(text: str, remove_extra_spaces: bool = True, normalize_unicode: bool = True) -> str:
        """Clean and normalize string"""
        try:
            if not isinstance(text, str):
                return str(text)
            
            # Normalize unicode
            if normalize_unicode:
                text = unicodedata.normalize('NFKC', text)
            
            # Remove extra whitespace
            if remove_extra_spaces:
                text = ' '.join(text.split())
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error cleaning string: {e}")
            return str(text) if text else ""
    
    @staticmethod
    def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate string to specified length with suffix"""
        try:
            if not isinstance(text, str):
                text = str(text)
            
            if len(text) <= max_length:
                return text
            
            # Calculate how much space to leave for suffix
            available_length = max_length - len(suffix)
            if available_length <= 0:
                return suffix
            
            return text[:available_length] + suffix
        except Exception as e:
            logger.error(f"Error truncating string: {e}")
            return str(text)[:max_length] if text else ""
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """Extract all numbers from string"""
        try:
            if not isinstance(text, str):
                return []
            
            # Find all numbers (including decimals and negative)
            number_pattern = r'-?\d+\.?\d*'
            numbers = re.findall(number_pattern, text)
            
            return [float(num) for num in numbers]
        except Exception as e:
            logger.error(f"Error extracting numbers from string: {e}")
            return []
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract all email addresses from string"""
        try:
            if not isinstance(text, str):
                return []
            
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            
            return emails
        except Exception as e:
            logger.error(f"Error extracting emails from string: {e}")
            return []
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract all URLs from string"""
        try:
            if not isinstance(text, str):
                return []
            
            url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
            urls = re.findall(url_pattern, text)
            
            return urls
        except Exception as e:
            logger.error(f"Error extracting URLs from string: {e}")
            return []
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """Extract all phone numbers from string"""
        try:
            if not isinstance(text, str):
                return []
            
            # Various phone number formats
            phone_patterns = [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
                r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # (123) 456-7890
                r'\b\+\d{1,3}\s*\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # +1 123-456-7890
                r'\b\d{10,11}\b'  # 1234567890 or 11234567890
            ]
            
            phone_numbers = []
            for pattern in phone_patterns:
                matches = re.findall(pattern, text)
                phone_numbers.extend(matches)
            
            return phone_numbers
        except Exception as e:
            logger.error(f"Error extracting phone numbers from string: {e}")
            return []
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in string"""
        try:
            if not isinstance(text, str) or not text.strip():
                return 0
            
            # Split by whitespace and filter out empty strings
            words = [word for word in text.split() if word.strip()]
            return len(words)
        except Exception as e:
            logger.error(f"Error counting words: {e}")
            return 0
    
    @staticmethod
    def count_characters(text: str, include_spaces: bool = True) -> int:
        """Count characters in string"""
        try:
            if not isinstance(text, str):
                return 0
            
            if include_spaces:
                return len(text)
            else:
                return len(text.replace(' ', ''))
        except Exception as e:
            logger.error(f"Error counting characters: {e}")
            return 0
    
    @staticmethod
    def count_lines(text: str) -> int:
        """Count lines in string"""
        try:
            if not isinstance(text, str):
                return 0
            
            if not text:
                return 0
            
            # Count newlines and add 1 for the last line
            return text.count('\n') + 1
        except Exception as e:
            logger.error(f"Error counting lines: {e}")
            return 0
    
    @staticmethod
    def reverse_string(text: str) -> str:
        """Reverse string"""
        try:
            if not isinstance(text, str):
                return str(text)[::-1]
            
            return text[::-1]
        except Exception as e:
            logger.error(f"Error reversing string: {e}")
            return str(text) if text else ""
    
    @staticmethod
    def is_palindrome(text: str, case_sensitive: bool = False) -> bool:
        """Check if string is palindrome"""
        try:
            if not isinstance(text, str):
                text = str(text)
            
            if not case_sensitive:
                text = text.lower()
            
            # Remove non-alphanumeric characters
            cleaned_text = re.sub(r'[^a-zA-Z0-9]', '', text)
            
            return cleaned_text == cleaned_text[::-1]
        except Exception as e:
            logger.error(f"Error checking palindrome: {e}")
            return False
    
    @staticmethod
    def find_substring_positions(text: str, substring: str) -> List[int]:
        """Find all positions of substring in text"""
        try:
            if not isinstance(text, str) or not isinstance(substring, str):
                return []
            
            positions = []
            start = 0
            
            while True:
                pos = text.find(substring, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            return positions
        except Exception as e:
            logger.error(f"Error finding substring positions: {e}")
            return []

class TextFormatter:
    """Helper class for text formatting"""
    
    @staticmethod
    def title_case(text: str, minor_words: List[str] = None) -> str:
        """Convert text to title case with proper handling of minor words"""
        try:
            if not isinstance(text, str):
                return str(text).title()
            
            if not minor_words:
                minor_words = ['a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'up']
            
            words = text.lower().split()
            if not words:
                return text
            
            # Always capitalize first and last word
            words[0] = words[0].title()
            if len(words) > 1:
                words[-1] = words[-1].title()
            
            # Capitalize other words unless they're minor words
            for i in range(1, len(words) - 1):
                if words[i] not in minor_words:
                    words[i] = words[i].title()
            
            return ' '.join(words)
        except Exception as e:
            logger.error(f"Error converting to title case: {e}")
            return str(text).title() if text else ""
    
    @staticmethod
    def format_number(number: Union[int, float], format_type: str = 'comma') -> str:
        """Format number with various formatting options"""
        try:
            if format_type == 'comma':
                return f"{number:,}"
            elif format_type == 'currency':
                return f"${number:,.2f}"
            elif format_type == 'percentage':
                return f"{number:.2f}%"
            elif format_type == 'scientific':
                return f"{number:.2e}"
            else:
                return str(number)
        except Exception as e:
            logger.error(f"Error formatting number: {e}")
            return str(number)
    
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
    def format_file_size(bytes_size: int) -> str:
        """Format file size in human-readable format"""
        try:
            if bytes_size < 1024:
                return f"{bytes_size}B"
            elif bytes_size < 1024 * 1024:
                kb = bytes_size / 1024
                return f"{kb:.1f}KB"
            elif bytes_size < 1024 * 1024 * 1024:
                mb = bytes_size / (1024 * 1024)
                return f"{mb:.1f}MB"
            else:
                gb = bytes_size / (1024 * 1024 * 1024)
                return f"{gb:.1f}GB"
        except Exception as e:
            logger.error(f"Error formatting file size: {e}")
            return str(bytes_size)
    
    @staticmethod
    def wrap_text(text: str, width: int, break_long_words: bool = True) -> str:
        """Wrap text to specified width"""
        try:
            if not isinstance(text, str):
                text = str(text)
            
            if width <= 0:
                return text
            
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line) + len(word) + 1 <= width:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        # Word is longer than width
                        if break_long_words and break_long_words:
                            # Break long word
                            while len(word) > width:
                                lines.append(word[:width])
                                word = word[width:]
                            if word:
                                current_line = word
                        else:
                            current_line = word
            
            if current_line:
                lines.append(current_line)
            
            return '\n'.join(lines)
        except Exception as e:
            logger.error(f"Error wrapping text: {e}")
            return text

class TextAnalyzer:
    """Helper class for text analysis"""
    
    @staticmethod
    def get_text_statistics(text: str) -> Dict[str, Any]:
        """Get comprehensive text statistics"""
        try:
            if not isinstance(text, str):
                text = str(text)
            
            stats = {
                'characters': StringUtils.count_characters(text, include_spaces=True),
                'characters_no_spaces': StringUtils.count_characters(text, include_spaces=False),
                'words': StringUtils.count_words(text),
                'lines': StringUtils.count_lines(text),
                'sentences': TextAnalyzer.count_sentences(text),
                'paragraphs': TextAnalyzer.count_paragraphs(text),
                'unique_words': len(set(text.lower().split())),
                'avg_word_length': 0,
                'avg_sentence_length': 0
            }
            
            # Calculate averages
            if stats['words'] > 0:
                stats['avg_word_length'] = stats['characters_no_spaces'] / stats['words']
            
            if stats['sentences'] > 0:
                stats['avg_sentence_length'] = stats['words'] / stats['sentences']
            
            return stats
        except Exception as e:
            logger.error(f"Error getting text statistics: {e}")
            return {}
    
    @staticmethod
    def count_sentences(text: str) -> int:
        """Count sentences in text"""
        try:
            if not isinstance(text, str):
                return 0
            
            # Simple sentence detection (ends with .!?)
            sentence_pattern = r'[.!?]+'
            sentences = re.split(sentence_pattern, text)
            
            # Filter out empty sentences
            sentences = [s.strip() for s in sentences if s.strip()]
            return len(sentences)
        except Exception as e:
            logger.error(f"Error counting sentences: {e}")
            return 0
    
    @staticmethod
    def count_paragraphs(text: str) -> int:
        """Count paragraphs in text"""
        try:
            if not isinstance(text, str):
                return 0
            
            # Split by double newlines (paragraphs)
            paragraphs = text.split('\n\n')
            
            # Filter out empty paragraphs
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            return len(paragraphs)
        except Exception as e:
            logger.error(f"Error counting paragraphs: {e}")
            return 0
    
    @staticmethod
    def get_word_frequency(text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get most frequent words in text"""
        try:
            if not isinstance(text, str):
                return []
            
            # Convert to lowercase and split into words
            words = text.lower().split()
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            words = [word for word in words if word not in stop_words and len(word) > 2]
            
            # Count word frequencies
            word_count = {}
            for word in words:
                # Clean word (remove punctuation)
                clean_word = re.sub(r'[^\w]', '', word)
                if clean_word:
                    word_count[clean_word] = word_count.get(clean_word, 0) + 1
            
            # Sort by frequency and return top N
            sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
            return sorted_words[:top_n]
        except Exception as e:
            logger.error(f"Error getting word frequency: {e}")
            return []
    
    @staticmethod
    def get_reading_time(text: str, words_per_minute: int = 200) -> float:
        """Estimate reading time in minutes"""
        try:
            word_count = StringUtils.count_words(text)
            return word_count / words_per_minute
        except Exception as e:
            logger.error(f"Error calculating reading time: {e}")
            return 0.0

class StringEncoder:
    """Helper class for string encoding and hashing"""
    
    @staticmethod
    def hash_string(text: str, algorithm: str = 'md5') -> str:
        """Hash string using specified algorithm"""
        try:
            if not isinstance(text, str):
                text = str(text)
            
            if algorithm == 'md5':
                return hashlib.md5(text.encode()).hexdigest()
            elif algorithm == 'sha1':
                return hashlib.sha1(text.encode()).hexdigest()
            elif algorithm == 'sha256':
                return hashlib.sha256(text.encode()).hexdigest()
            elif algorithm == 'sha512':
                return hashlib.sha512(text.encode()).hexdigest()
            else:
                logger.warning(f"Unknown hash algorithm: {algorithm}, using MD5")
                return hashlib.md5(text.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error hashing string: {e}")
            return ""
    
    @staticmethod
    def encode_base64(text: str) -> str:
        """Encode string to base64"""
        try:
            if not isinstance(text, str):
                text = str(text)
            
            return base64.b64encode(text.encode()).decode()
        except Exception as e:
            logger.error(f"Error encoding to base64: {e}")
            return ""
    
    @staticmethod
    def decode_base64(encoded_text: str) -> str:
        """Decode string from base64"""
        try:
            if not isinstance(encoded_text, str):
                return ""
            
            return base64.b64decode(encoded_text.encode()).decode()
        except Exception as e:
            logger.error(f"Error decoding from base64: {e}")
            return ""
    
    @staticmethod
    def create_slug(text: str, separator: str = '-') -> str:
        """Create URL-friendly slug from text"""
        try:
            if not isinstance(text, str):
                text = str(text)
            
            # Convert to lowercase
            text = text.lower()
            
            # Replace spaces and special characters with separator
            text = re.sub(r'[^\w\s-]', '', text)
            text = re.sub(r'[-\s]+', separator, text)
            
            # Remove leading/trailing separators
            text = text.strip(separator)
            
            return text
        except Exception as e:
            logger.error(f"Error creating slug: {e}")
            return str(text).lower().replace(' ', separator) if text else ""

# Utility functions
def clean_text(text: str) -> str:
    """Quick function to clean text"""
    return StringUtils.clean_string(text)

def truncate_text(text: str, max_length: int) -> str:
    """Quick function to truncate text"""
    return StringUtils.truncate_string(text, max_length)

def count_words(text: str) -> int:
    """Quick function to count words"""
    return StringUtils.count_words(text)

def is_palindrome(text: str) -> bool:
    """Quick function to check if text is palindrome"""
    return StringUtils.is_palindrome(text)

def title_case(text: str) -> str:
    """Quick function to convert to title case"""
    return TextFormatter.title_case(text)

def format_number(number: Union[int, float]) -> str:
    """Quick function to format number"""
    return TextFormatter.format_number(number)

def get_text_stats(text: str) -> Dict[str, Any]:
    """Quick function to get text statistics"""
    return TextAnalyzer.get_text_statistics(text)

def hash_text(text: str) -> str:
    """Quick function to hash text"""
    return StringEncoder.hash_string(text)
