import langid
import torch
import re
from transformers import (
    MBartForConditionalGeneration, MBart50TokenizerFast,
    BartForConditionalGeneration, BartTokenizer
)
from .translation import translate_text

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

LANGUAGE_CODES = {
    "en": "en_XX", "de": "de_DE", "es": "es_XX", "fr": "fr_XX",
    "ru": "ru_RU", "zh": "zh_CN", "zh-cn": "zh_CN", "ar": "ar_AR",
    "it": "it_IT", "pt": "pt_XX", "hi": "hi_IN", "ja": "ja_XX", "ko": "ko_KR"
}

def to_mbart_code(lang_code: str) -> str:
    return LANGUAGE_CODES.get(lang_code.lower(), "en_XX")

# English summarizer
SUMMARIZER_NAME = "facebook/bart-large-cnn"
summarizer_tokenizer = BartTokenizer.from_pretrained(SUMMARIZER_NAME)
summarizer_model = BartForConditionalGeneration.from_pretrained(SUMMARIZER_NAME).to(device)

# Multilingual model for translation/paraphrasing
MT_MODEL_NAME = "facebook/mbart-large-50-many-to-many-mmt"
mt_tokenizer = MBart50TokenizerFast.from_pretrained(MT_MODEL_NAME)

device = "cuda" if torch.cuda.is_available() else "cpu"
mt_model = MBartForConditionalGeneration.from_pretrained(MT_MODEL_NAME, device_map=None)
mt_model.to(device)



def chunk_text(text: str, max_tokens: int = 500, tokenizer=None):
    """Chunk text into smaller parts for processing."""
    tokens = tokenizer.tokenize(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        sub_tokens = tokens[i:i + max_tokens]
        chunks.append(tokenizer.convert_tokens_to_string(sub_tokens))
    return chunks


def inject_keywords(text, keywords=None):
    """Prepend a natural instruction to include keywords in the summary."""
    if not keywords:
        return text
    keyword_str = ", ".join(keywords)
    return f"Include the following concepts naturally in the summary: {keyword_str}.\n\n{text}"

def summarize_and_translate(text, translate_to="en", keywords=None):
    """Summarize and translate text using mBART.

    Args:
        text (str): The input text to summarize and translate.
        translate_to (str, optional): The target language for translation. Defaults to "en".
        keywords (list, optional): A list of keywords to include in the summary. Defaults to None.

    Returns:
        dict: A dictionary containing the original language, final summary, and target language.
    """

    # Detect source language
    detected_lang, _ = langid.classify(text)

    #Translate non-English input → English
    if detected_lang != "en":
        text_en = translate_text(text, detected_lang, "en")
    else:
        text_en = text

    # Inject keywords
    text_with_keywords = inject_keywords(text_en, keywords)

    # Summarize in English
    chunks = chunk_text(text_with_keywords, max_tokens=500, tokenizer=summarizer_tokenizer)
    summaries = []
    for chunk in chunks:
        inputs = summarizer_tokenizer(chunk, return_tensors="pt", truncation=True, max_length=1024).to(device)
        summary_ids = summarizer_model.generate(
            **inputs,
            max_length=150,
            min_length=20,
            num_beams=4,
            no_repeat_ngram_size=2
        )
        summaries.append(summarizer_tokenizer.decode(summary_ids[0], skip_special_tokens=True))
    summary_en = " ".join(summaries)

    # Translate to target language 
    if translate_to != "en":
        final_summary = translate_text(summary_en, "en", translate_to)
    else:
        final_summary = summary_en

    return {
        "original_language": detected_lang,
        "final_summary": final_summary,
        "translated_to": translate_to
    }
