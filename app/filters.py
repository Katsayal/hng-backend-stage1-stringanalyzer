import re

NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}

def replace_number_words(query: str) -> str:
    """Replace number words in a string with digits."""
    pattern = re.compile(r'\b(' + '|'.join(NUMBER_WORDS.keys()) + r')\b')
    return pattern.sub(lambda m: str(NUMBER_WORDS[m.group(0)]), query)

def parse_natural_language(query: str):
    filters = {}

    q = query.lower()
    q = replace_number_words(q)  # convert "two" to "2", etc.

    # Basic rules
    if "palindromic" in q or "palindrome" in q:
        filters["is_palindrome"] = True

    if "single word" in q or "one word" in q:
        filters["word_count"] = 1

    match = re.search(r"longer than (\d+)", q)
    if match:
        filters["min_length"] = int(match.group(1)) + 1

    match = re.search(r"shorter than (\d+)", q)
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
