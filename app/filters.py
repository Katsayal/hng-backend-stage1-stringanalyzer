import re
from typing import Dict, Any, Optional

# Extended number words for better parsing
NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    "hundred": 100, "thousand": 1000
}

# Common patterns for natural language queries
PATTERNS = {
    'palindrome': r'(palindromic|palindrome)',
    'word_count': r'(\d+)\s*(?:word|words?)|(?:single|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\s+words?',
    'length_gt': r'(?:longer|greater|more)\s+than\s+(\d+)',
    'length_lt': r'(?:shorter|less)\s+than\s+(\d+)',
    'length_eq': r'(?:exactly|precisely|of)\s+(\d+)\s+(?:characters?|letters?)',
    'contains_char': r'(?:containing?|with|that has|having|includes?)\s+(?:the\s+)?(?:letter\s+)?([a-zA-Z])',
    'vowel': r'[aeiou]',
    'first_vowel': r'first\s+vowel',
    'last_vowel': r'last\s+vowel'
}

def text_to_number(text: str) -> int:
    """Convert text representation of numbers to integers."""
    if text.isdigit():
        return int(text)
    
    text = text.lower().strip()
    if text in NUMBER_WORDS:
        return NUMBER_WORDS[text]
    
    # Handle compound numbers like "twenty one"
    words = text.replace('-', ' ').replace(' and ', ' ').split()
    result = 0
    current = 0
    
    for word in words:
        if word in NUMBER_WORDS:
            num = NUMBER_WORDS[word]
            if num >= 100:
                current *= num
                result += current
                current = 0
            else:
                current += num
    
    return result + current

def extract_number(text: str) -> Optional[int]:
    """Extract the first number from text."""
    # Look for digits first
    match = re.search(r'\d+', text)
    if match:
        return int(match.group(0))
    
    # Then try to convert number words
    words = text.lower().split()
    for word in words:
        if word in NUMBER_WORDS:
            return NUMBER_WORDS[word]
    
    return None

def parse_natural_language(query: str) -> Dict[str, Any]:
    """
    Parse natural language queries into filter parameters.
    
    Args:
        query: Natural language query string
        
    Returns:
        Dictionary of filter parameters
        
    Raises:
        ValueError: If the query cannot be parsed
    """
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
    
    query = query.lower().strip()
    filters = {}
    
    try:
        # Check for palindrome
        if re.search(PATTERNS['palindrome'], query):
            filters["is_palindrome"] = True
        
        # Check for word count
        word_count_match = re.search(PATTERNS['word_count'], query)
        if word_count_match:
            num = extract_number(word_count_match.group(0))
            if num is not None:
                filters["word_count"] = num
        
        # Check for length constraints
        length_gt = re.search(PATTERNS['length_gt'], query)
        if length_gt:
            filters["min_length"] = int(length_gt.group(1)) + 1
        
        length_lt = re.search(PATTERNS['length_lt'], query)
        if length_lt:
            filters["max_length"] = int(length_lt.group(1)) - 1
        
        length_eq = re.search(PATTERNS['length_eq'], query)
        if length_eq:
            length = int(length_eq.group(1))
            filters["min_length"] = length
            filters["max_length"] = length
        
        # Check for character containment
        char_match = re.search(PATTERNS['contains_char'], query)
        if char_match:
            char = char_match.group(1).lower()
            filters["contains_character"] = char
        
        # Special case for first/last vowel
        if re.search(PATTERNS['first_vowel'], query):
            filters["contains_character"] = 'a'  # Default to 'a' as first vowel
        elif re.search(PATTERNS['last_vowel'], query):
            filters["contains_character"] = 'u'  # Default to 'u' as last vowel
        
        # If no filters were applied, raise an error
        if not filters:
            raise ValueError("Could not parse the query. Please try a different format.")
        
        return filters
    
    except Exception as e:
        raise ValueError(f"Error parsing query: {str(e)}")
    if match:
        filters["max_length"] = int(match.group(1)) - 1

    match = re.search(r"exactly (\d+) words?", q)
    if match:
        filters["word_count"] = int(match.group(1))

    match = re.search(r"containing the letter (\w)", q)
    if match:
        filters["contains_character"] = match.group(1)

    match = re.search(r"containing the character (\w)", q)
    if match:
        filters["contains_character"] = match.group(1)

    if "first vowel" in q:
        filters["contains_character"] = "a"  # naive heuristic

    if not filters:
        raise ValueError("Unable to parse natural language query.")

    return filters
