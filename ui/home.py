import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Homepage",
    page_icon="🏡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Language codes mapping
LANGUAGE_CODES = {
    "en": "en_XX", "de": "de_DE", "es": "es_XX", "fr": "fr_XX",
    "ru": "ru_RU", "zh": "zh_CN", "zh-cn": "zh_CN", "ar": "ar_AR",
    "it": "it_IT", "pt": "pt_XX", "hi": "hi_IN", "ja": "ja_XX", "ko": "ko_KR"
}

# --- Initialize permanent keys ---
if 'text' not in st.session_state:
    st.session_state.text = ""
if 'to_lang' not in st.session_state:
    st.session_state.to_lang = "en"  # default target language
if 'summarize' not in st.session_state:
    st.session_state.summarize = False

# --- Initialize temporary keys ---
if '_text_area' not in st.session_state:
    st.session_state['_text_area'] = st.session_state.text
if '_summarize' not in st.session_state:
    st.session_state['_summarize'] = st.session_state.summarize


def keep(key):
    """Copy from temporary widget key to permanent key"""
    st.session_state[key] = st.session_state[f"_{key}"]


def unkeep(key):
    """Copy from permanent key to temporary key"""
    st.session_state[f"_{key}"] = st.session_state[key]


if __name__ == "__main__":

    st.title("Homepage")

    # Text area for main text (keep/unkeep pattern)
    st.text_area(
        "Enter text to analyze:",
        value=st.session_state['_text_area'],
        on_change=keep,
        args=("text",),  # <- map to permanent "text"
        key="_text_area"
    )

    # Checkbox for summary (keep/unkeep pattern)
    st.checkbox(
        "Run a summary on the provided text",
        value=st.session_state['_summarize'],
        on_change=keep,
        args=("summarize",),  # <- map to permanent "summarize"
        key="_summarize"
    )

    # Text input for target translation language (permanent key)
    st.text_input(
        "Target translation language (e.g., 'en', 'de', 'fr'):",
        placeholder="Type language code here",
        key="to_lang"
    )

    # Submit button
    if st.button("Submit"):
        # Apply keep/unkeep to sync text + summarize
        st.session_state.text = st.session_state['_text_area']
        unkeep("text")
        st.session_state.summarize = st.session_state['_summarize']
        unkeep("summarize")

        st.success(
            f"Text submitted successfully! "
            f"Translation target: {st.session_state.to_lang} | "
            f"Summarize: {st.session_state.summarize}"
        )
