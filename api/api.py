# app/api.py
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from words_context.context import extract_keyword_sentences
from text_processing.processing import extract_frequent_words
from translation_summary.mbart import summarize_and_translate  # summarization function


# ----------------------------
# Models
# ----------------------------
class FrequentWordsRequest(BaseModel):
    text: str
    lang: Optional[str] = "de"
    top_pct: Optional[float] = 10
    to_lang: Optional[str] = "en"  # target language for keyword translations


class FrequentWordsResponse(BaseModel):
    analysis: List[Dict[str, Any]]   # [{"word": "...", "frequency": 5}, ...]
    vocabulary: List[str]
    sentences: Optional[Dict[str, Dict[str, Any]]] = None
    # {
    #   "Haus": {
    #       "translation": "house",
    #       "context": [
    #           {"sentence": "Das Haus ist groß.", "translation": "The house is big."},
    #           {"sentence": "Ich gehe ins Haus."}
    #       ]
    #   }
    # }


class SummarizationRequest(BaseModel):
    text: str
    summary_translate_to: Optional[str] = "en"


class SummarizationResponse(BaseModel):
    summary: str
    summary_translated_to: Optional[str] = None


# ----------------------------
# Routers
# ----------------------------
router = APIRouter()


@router.post("/frequent-words", response_model=FrequentWordsResponse)
async def get_frequent_words(request: FrequentWordsRequest):
    try:
        # Extract frequent words
        analysis = extract_frequent_words(
            request.text,
            lang=request.lang,
            top_pct=request.top_pct
        )
        vocabulary = [word for word, freq in analysis]

        # Extract keyword sentences (includes keyword translations now)
        output = extract_keyword_sentences(
            text=request.text,
            keywords=vocabulary,
            translate_to=request.to_lang
        )

        return FrequentWordsResponse(
            analysis=[{"word": word, "frequency": freq} for word, freq in analysis],
            vocabulary=vocabulary,
            sentences=output
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize", response_model=SummarizationResponse)
async def summarize_text(request: SummarizationRequest):
    try:
        summary_data = summarize_and_translate(
            text=request.text,
            translate_to=request.summary_translate_to
        )
        return SummarizationResponse(
            summary=summary_data["final_summary"],
            summary_translated_to=summary_data["translated_to"]
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# FastAPI app
# ----------------------------
app = FastAPI(title="Text Analysis & Summarization API")
app.include_router(router)
