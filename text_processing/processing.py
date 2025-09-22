from collections import Counter
import spacy
import re
import text_preprocessing.preprocessing as text_prep

def load_model(lang: str):
    """Load spaCy model for a given language code."""
    try:
        return spacy.load(f"{lang}_core_news_sm")
    except OSError:
        return spacy.blank(lang)  # fallback: tokenizer only

def extract_frequent_words(
    text: str,
    lang: str = "de",
    top_pct: float = 10,
    min_len: int = 2,
    require_pos: bool = True,
    min_words: int = 5,
    debug: bool = False
):
    nlp = load_model(lang)
    text = text_prep.clean_text(text)
    text = text_prep.remove_stopwords(text)
    print(25)
    doc = nlp(text)

    has_pos = any(token.pos_ for token in doc)
    print(29)
    content_words = []
    for token in doc:
        if not token.is_alpha or token.is_stop or len(token) < min_len:
            continue
        if require_pos and has_pos and token.pos_ not in {"NOUN", "VERB", "ADJ"}:
            continue
        content_words.append(token.lemma_.lower() if token.lemma_ else token.text.lower())
    print(37)
    counter = Counter(content_words)
    sorted_words = counter.most_common()
    print(sorted_words)
    # Take top X% of unique words
    num_unique = len(sorted_words)
    cutoff = max(min_words, int(num_unique * (top_pct / 100)))

    return sorted_words[:cutoff]