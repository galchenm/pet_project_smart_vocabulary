import langid
import torch
import re
from transformers import (
    MBartForConditionalGeneration, MBart50TokenizerFast,
    BartForConditionalGeneration, BartTokenizer
)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Multilingual model for translation/paraphrasing
MT_MODEL_NAME = "facebook/mbart-large-50-many-to-many-mmt"
mt_tokenizer = MBart50TokenizerFast.from_pretrained(MT_MODEL_NAME)
mt_model = MBartForConditionalGeneration.from_pretrained(MT_MODEL_NAME).to(device)


LANGUAGE_CODES = {
    "en": "en_XX", "de": "de_DE", "es": "es_XX", "fr": "fr_XX",
    "ru": "ru_RU", "zh": "zh_CN", "zh-cn": "zh_CN", "ar": "ar_AR",
    "it": "it_IT", "pt": "pt_XX", "hi": "hi_IN", "ja": "ja_XX", "ko": "ko_KR"
}

def to_mbart_code(lang_code: str) -> str:
    return LANGUAGE_CODES.get(lang_code.lower(), "en_XX")


def translate_text(text, inp_src_lang, inp_tgt_lang, max_length=10240):
    """Translate text from src_lang to tgt_lang using mBART50."""
    
    src_lang = to_mbart_code(inp_src_lang)
    tgt_lang = to_mbart_code(inp_tgt_lang)

    if src_lang == tgt_lang:
        return text
    mt_tokenizer.src_lang = src_lang
    inputs = mt_tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length).to(device)
    translated_ids = mt_model.generate(
        **inputs,
        forced_bos_token_id=mt_tokenizer.lang_code_to_id[tgt_lang],
        num_beams=4,
        max_length=150
    )
    return mt_tokenizer.decode(translated_ids[0], skip_special_tokens=True)
