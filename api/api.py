# app/api.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
from words_context.context import extract_keyword_sentences
from text_processing.processing import extract_frequent_words

router = APIRouter()

class TextRequest(BaseModel):
    text: str

class TextResponse(BaseModel):
    analysis: List[dict]
    vocabulary: List[str]
    sentences: Optional[Dict[str, List[Dict]]] = None

@router.post("/analyze", response_model=TextResponse)
async def analyze_text(
    request: TextRequest,
    lang: Optional[str] = "de",
    top_pct: Optional[float] = 10,
    to_lang: Optional[str] = "en"
):
    analysis = extract_frequent_words(request.text, lang=lang, top_pct=top_pct)
    vocabulary = [word for word, freq in analysis]
    output = extract_keyword_sentences(request.text, vocabulary, translate_to=to_lang)

    return TextResponse(
        analysis=[{"word": word, "frequency": freq} for word, freq in analysis],
        vocabulary=vocabulary,
        sentences=output
    )
