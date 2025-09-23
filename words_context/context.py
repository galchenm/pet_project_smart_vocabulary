import re
from typing import List, Optional, Dict
import langid
import torch
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

# Load model and tokenizer once (efficiently)
model_name = "facebook/mbart-large-50-many-to-many-mmt"
tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = MBartForConditionalGeneration.from_pretrained(model_name).to(device)

LANGUAGE_CODES = {
    "en": "en_XX", "de": "de_DE", "es": "es_XX", "fr": "fr_XX",
    "ru": "ru_RU", "zh-cn": "zh_CN", "ar": "ar_AR", "it": "it_IT",
    "pt": "pt_XX", "hi": "hi_IN", "ja": "ja_XX", "ko": "ko_KR"
}

def translate_with_mbart(text: str, src_lang: str, tgt_lang: str, max_length: int = 512) -> str:
    """
    Translate a single text string using MBart.
    """
    tokenizer.src_lang = src_lang
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length).to(device)
    translated_ids = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.lang_code_to_id[tgt_lang],
        max_new_tokens=150,
        num_beams=4
    )
    return tokenizer.decode(translated_ids[0], skip_special_tokens=True)

def extract_keyword_sentences(
        text: str,
        keywords: List[str],
        translate_to: Optional[str] = None
    ) -> Dict[str, Dict]:
    """
    Extract sentences containing keywords from text, optionally translating them.
    Returns a dict keyed by keyword with original and translated sentences.
    """
    results: Dict[str, Dict] = {}

    # Detect source language
    detected_lang, _ = langid.classify(text)
    src_lang_code = LANGUAGE_CODES.get(detected_lang, "en_XX")
    tgt_lang_code = LANGUAGE_CODES.get(translate_to.lower(), "en_XX") if translate_to else None

    # Split text into sentences (simple regex)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    for keyword in keywords:
        keyword_lower = keyword.lower()
        matches = []

        # Translate the keyword itself if needed
        keyword_translation = (
            translate_with_mbart(keyword, src_lang_code, tgt_lang_code)
            if translate_to else None
        )

        for sent in sentences:
            if keyword_lower in sent.lower():
                match = {"sentence": sent.strip()}

                # Translate sentence if requested
                if translate_to:
                    translation = translate_with_mbart(sent, src_lang_code, tgt_lang_code)
                    match["translation"] = translation

                matches.append(match)

        if matches:
            results[keyword] = {
                "translation": keyword_translation,
                "context": matches
            }

    return results
