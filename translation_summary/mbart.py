import re
from typing import List, Optional, Dict

import langid
import torch
from transformers import (
    MBartForConditionalGeneration, MBart50TokenizerFast,
    BartForConditionalGeneration, BartTokenizer
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------
# Language codes for mBART
# -----------------------------
LANGUAGE_CODES = {
    "en": "en_XX", "de": "de_DE", "es": "es_XX", "fr": "fr_XX",
    "ru": "ru_RU", "zh-cn": "zh_CN", "zh": "zh_CN", "ar": "ar_AR",
    "it": "it_IT", "pt": "pt_XX", "hi": "hi_IN", "ja": "ja_XX", "ko": "ko_KR"
}

def to_mbart_code(lang_code: str) -> str:
    return LANGUAGE_CODES.get(lang_code.lower(), "en_XX")


# -----------------------------
# Load models and tokenizers
# -----------------------------
# English summarizer
SUMMARIZER_NAME = "facebook/bart-large-cnn"
summarizer_tokenizer = BartTokenizer.from_pretrained(SUMMARIZER_NAME)
summarizer_model = BartForConditionalGeneration.from_pretrained(SUMMARIZER_NAME).to(device)

# Multilingual translation
MT_MODEL_NAME = "facebook/mbart-large-50-many-to-many-mmt"
mt_tokenizer = MBart50TokenizerFast.from_pretrained(MT_MODEL_NAME)
mt_model = MBartForConditionalGeneration.from_pretrained(MT_MODEL_NAME).to(device)


# -----------------------------
# Helper functions
# -----------------------------
def chunk_text(text: str, max_tokens: int = 500, tokenizer=None) -> List[str]:
    """Chunk text safely for processing."""
    tokens = tokenizer.tokenize(text)
    if not tokens:
        return []
    
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        sub_tokens = tokens[i:i + max_tokens]
        chunk_str = tokenizer.convert_tokens_to_string(sub_tokens).strip()
        if chunk_str:  # skip empty chunks
            chunks.append(chunk_str)
    return chunks


def inject_keywords(text: str, keywords: Optional[List[str]] = None) -> str:
    """Prepend instructions to include keywords in summary."""
    if not keywords:
        return text
    keyword_str = ", ".join(keywords)
    return f"Include the following concepts naturally in the summary: {keyword_str}.\n\n{text}"


def translate_with_mbart(text: str, src_lang: str, tgt_lang: str) -> str:
    """Translate text using mBART safely."""
    if not text.strip():
        return ""
    mt_tokenizer.src_lang = to_mbart_code(src_lang)
    inputs = mt_tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
    translated_ids = mt_model.generate(
        **inputs,
        forced_bos_token_id=mt_tokenizer.lang_code_to_id[to_mbart_code(tgt_lang)],
        max_new_tokens=150,
        num_beams=4
    )
    return mt_tokenizer.decode(translated_ids[0], skip_special_tokens=True)


def summarize_text_chunks(chunks: List[str]) -> str:
    """Summarize a list of text chunks safely."""
    summaries = []
    for chunk in chunks:
        if not chunk.strip():
            continue
        inputs = summarizer_tokenizer(chunk, return_tensors="pt", truncation=True, max_length=1024).to(device)
        summary_ids = summarizer_model.generate(
            **inputs,
            max_length=150,
            min_length=20,
            num_beams=4,
            no_repeat_ngram_size=2
        )
        decoded = summarizer_tokenizer.decode(summary_ids[0], skip_special_tokens=True).strip()
        if decoded:
            summaries.append(decoded)
    return " ".join(summaries)


# -----------------------------
# Main function
# -----------------------------
def summarize_and_translate(
    text: str,
    translate_to: str = "en",
    keywords: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Summarize text in English and optionally translate to another language.

    Returns a dict:
        - original_language
        - final_summary
        - translated_to
    """
    # Detect source language
    detected_lang, _ = langid.classify(text)

    # Step 1: Translate to English if needed
    if detected_lang != "en":
        text_en = translate_with_mbart(text, detected_lang, "en")
    else:
        text_en = text

    # Step 2: Inject keywords
    text_with_keywords = inject_keywords(text_en, keywords)

    # Step 3: Chunk and summarize
    chunks = chunk_text(text_with_keywords, max_tokens=500, tokenizer=summarizer_tokenizer)
    summary_en = summarize_text_chunks(chunks)

    # Step 4: Translate back if needed
    if translate_to.lower() != "en":
        final_summary = translate_with_mbart(summary_en, "en", translate_to)
    else:
        final_summary = summary_en

    return {
        "original_language": detected_lang,
        "final_summary": final_summary,
        "translated_to": translate_to
    }
