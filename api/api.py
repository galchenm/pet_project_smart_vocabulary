# app/api.py
from fastapi import FastAPI, APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from words_context.context import extract_keyword_sentences
from text_processing.processing import extract_frequent_words
from translation_summary.mbart import summarize_and_translate  # your summarization function

router = APIRouter()

# Request model
class TextRequest(BaseModel):
    text: str
    summarize: Optional[bool] = False
    summary_translate_to: Optional[str] = "en"  # target language for summary

# Response model
class TextResponse(BaseModel):
    analysis: List[dict]
    vocabulary: List[str]
    sentences: Optional[Dict[str, List[Dict]]] = None
    summary: Optional[str] = None
    summary_translated_to: Optional[str] = None


@router.post("/analyze", response_model=TextResponse)
async def analyze_text(
    request: TextRequest,
    lang: Optional[str] = "de",
    top_pct: Optional[float] = 10,
    to_lang: Optional[str] = "en"  # translation for keywords
):
    try:
        # Extract frequent words
        analysis = extract_frequent_words(request.text, lang=lang, top_pct=top_pct)
        vocabulary = [word for word, freq in analysis]

        # Extract keyword sentences with translations
        output = extract_keyword_sentences(request.text, vocabulary, translate_to=to_lang)
        output_clean = {k: v for k, v in (output or {}).items()}

        # Optional summarization
        summary_result = None
        summary_lang = None
        if request.summarize:
            summary_data = summarize_and_translate(
                text=request.text,
                translate_to=request.summary_translate_to,
                keywords=vocabulary
            )
            summary_result = summary_data["final_summary"]
            summary_lang = summary_data["translated_to"]

        return TextResponse(
            analysis=[{"word": word, "frequency": freq} for word, freq in analysis],
            vocabulary=vocabulary,
            sentences=output_clean,
            summary=summary_result,
            summary_translated_to=summary_lang
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Create FastAPI app
app = FastAPI(title="Text Analysis & Summarization API")
app.include_router(router)
