import hashlib
import re
from collections import Counter
from typing import Dict, Any

def analyze_string(value: str) -> Dict[str, Any]:
    """
    Analyze a string and compute various properties.
    
    Args:
        value: The input string to analyze
        
    Returns:
        A dictionary containing the computed properties
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")
        
    # Clean the input string (remove leading/trailing whitespace)
    value_clean = value.strip()
    
    # Convert to lowercase for case-insensitive operations
    lower_value = value_clean.lower()
    
    # Calculate string length
    length = len(value_clean)
    
    # Check if the string is a palindrome (case-insensitive, ignores whitespace)
    # Remove all non-alphanumeric characters for palindrome check
    alphanumeric = re.sub(r'[^a-z0-9]', '', lower_value)
    is_palindrome = alphanumeric == alphanumeric[::-1] if alphanumeric else False
    
    # Count unique characters (case-sensitive)
    unique_characters = len(set(value_clean))
    
    # Count words (split on any whitespace)
    word_count = len(value_clean.split()) if value_clean else 0
    
    # Compute SHA-256 hash (using UTF-8 encoding)
    sha256_hash = hashlib.sha256(value_clean.encode('utf-8')).hexdigest()
    
    # Calculate character frequency (case-sensitive)
    character_frequency_map = dict(Counter(value_clean))
    
    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": character_frequency_map
    }
