import hashlib
from collections import Counter

def analyze_string(value: str) -> dict:
    value_clean = value.strip()
    lower_value = value_clean.lower()

    length = len(value_clean)
    is_palindrome = lower_value == lower_value[::-1]
    unique_characters = len(set(value_clean))
    word_count = len(value_clean.split())
    sha256_hash = hashlib.sha256(value_clean.encode()).hexdigest()
    character_frequency_map = dict(Counter(value_clean))

    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": character_frequency_map
    }
