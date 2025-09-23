import re
from typing import List, Optional, Dict
import langid
import torch
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from translation_summary.translation import translate_text

# Load model and tokenizer once (put this outside the function for efficiency)
model_name = "facebook/mbart-large-50-many-to-many-mmt"
tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = MBartForConditionalGeneration.from_pretrained(model_name).to(device)

LANGUAGE_CODES = {
    "en": "en_XX", "de": "de_DE", "es": "es_XX", "fr": "fr_XX",
    "ru": "ru_RU", "zh-cn": "zh_CN", "ar": "ar_AR", "it": "it_IT",
    "pt": "pt_XX", "hi": "hi_IN", "ja": "ja_XX", "ko": "ko_KR"
}

def extract_keyword_sentences(
        text: str,
        keywords: List[str],
        translate_to: Optional[str] = None
    ) -> Dict[str, Dict]:
    results: Dict[str, Dict] = {}
    detected_lang, _ = langid.classify(text)
    src_lang_code = LANGUAGE_CODES.get(detected_lang, "en_XX")
    tgt_lang_code = LANGUAGE_CODES.get(translate_to.lower(), "en_XX") if translate_to else None

    # Split text into sentences (simple regex)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    for keyword in keywords:
        keyword_lower = keyword.lower()
        matches = []

        # Translate the keyword itself (not the whole text)
        keyword_translation = (
            translate_text(keyword, src_lang_code, tgt_lang_code)
            if translate_to else None
        )

        for sent in sentences:
            if keyword_lower in sent.lower():
                match = {"sentence": sent.strip()}

                if translate_to:
                    tokenizer.src_lang = src_lang_code
                    inputs = tokenizer(
                        sent,
                        return_tensors="pt",
                        truncation=True,
                        max_length=512
                    ).to(device)

                    translated_ids = model.generate(
                        **inputs,
                        forced_bos_token_id=tokenizer.lang_code_to_id[tgt_lang_code],
                        max_new_tokens=150,
                        num_beams=4
                    )
                    translation = tokenizer.decode(translated_ids[0], skip_special_tokens=True)
                    match["translation"] = translation

                matches.append(match)

        if matches:
            results[keyword] = {
                "translation": keyword_translation,
                "context": matches
            }

    return results
