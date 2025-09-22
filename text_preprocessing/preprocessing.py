import re
from langdetect import detect
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Download resources
nltk.download("punkt_tab")
nltk.download("stopwords")

def clean_text(text):
    """Cleans the input text by removing extra whitespace, punctuation, and numbers.

    Args:
        text (str): The input text to clean.

    Returns:
        str: The cleaned text.
    """
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)

    text = re.sub(r'[^\w\s]', '', text)   # remove punctuation
    text = re.sub(r'\d+', '', text)       # remove numbers
    return text.strip()


def remove_stopwords(text: str):
    # Detect language
    lang = detect(text)  
    print(f"Detected language: {lang}")

    # Load stopwords if available
    if lang in stopwords.fileids():
        stop_words = set(stopwords.words(lang))
    else:
        stop_words = set()

    # Tokenize and filter
    tokens = word_tokenize(text.lower())
    filtered_tokens = [w for w in tokens if w.isalpha() and w not in stop_words]

    # Join back into a string for spaCy
    return " ".join(filtered_tokens)

