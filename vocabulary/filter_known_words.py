from typing import List

def filter_known_words(keywords: List[str], known_words: List[str]) -> List[str]:
    """
    Filters out known words from the list of keywords (case-insensitive).

    Args:
        keywords (List[str]): List of keywords to filter.
        known_words (List[str]): List of known words to exclude.

    Returns:
        List[str]: Filtered list of keywords excluding known words.
    """
    known_words_lower = set(word.lower() for word in known_words)
    filtered = [kw for kw in keywords if kw.lower() not in known_words_lower]
    return filtered
