import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Results of text analysis",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# MBart language codes
LANGUAGE_CODES = {
    "en": "en_XX", "de": "de_DE", "es": "es_XX", "fr": "fr_XX",
    "ru": "ru_RU", "zh": "zh_CN", "zh-cn": "zh_CN", "ar": "ar_AR",
    "it": "it_IT", "pt": "pt_XX", "hi": "hi_IN", "ja": "ja_XX", "ko": "ko_KR"
}

# --- Cached API calls ---
@st.cache_data(show_spinner="Fetching frequent words...")
def fetch_frequent_words(text, lang, top_pct, to_lang):
    response = requests.post(
        "http://127.0.0.1:8000/frequent-words",
        json={"text": text},
        params={"lang": lang, "top_pct": top_pct, "to_lang": to_lang}
    )
    response.raise_for_status()
    return response.json()

@st.cache_data(show_spinner="Generating summary...")
def fetch_summary(text, summary_translate_to):
    response = requests.post(
        "http://127.0.0.1:8000/summarize",
        json={"text": text, "summary_translate_to": summary_translate_to}
    )
    response.raise_for_status()
    return response.json()


# --- Main UI ---
if 'text' not in st.session_state or not st.session_state.text:
    st.warning("No text submitted yet. Please go to the Homepage to submit text.")
    st.stop()

if 'to_lang' not in st.session_state:
    st.session_state.to_lang = "en"

if 'summarize' not in st.session_state:
    st.session_state.summarize = False

if __name__ == "__main__":
    st.title("Results of Text Analysis")

    st.write("Here are the results of the text you submitted:")
    st.write(st.session_state.text)
    st.write(
        f"Target translation language: {st.session_state.to_lang} "
        f"({LANGUAGE_CODES.get(st.session_state.to_lang, 'en_XX')})"
    )

    try:
        # --- Always fetch frequent words (cached) ---
        result = fetch_frequent_words(
            st.session_state.text,
            lang="de",
            top_pct=10,
            to_lang=st.session_state.to_lang
        )

        if isinstance(result, dict):
            # --- Word Frequencies ---
            df = pd.DataFrame(result.get("analysis", []))
            st.subheader("Word Frequencies")
            st.dataframe(df)

            # --- Keyword Contexts ---
            st.subheader("Keyword Contexts")
            sentences = result.get("sentences", {})
            if isinstance(sentences, dict):
                for word, matches in sentences.items():
                    st.markdown(f"**{word}**")
                    for match in matches or []:
                        st.write(f"- {match.get('sentence', '')}")
                        if match.get("translation"):
                            st.caption(f"→ {match.get('translation')}")

        else:
            st.error("API returned unexpected format for frequent words.")

        # --- Fetch summary only if requested ---
        if st.session_state.summarize:
            summary_data = fetch_summary(st.session_state.text, st.session_state.to_lang)
            if isinstance(summary_data, dict):
                st.subheader("Summary")
                st.write(summary_data.get("final_summary", "No summary returned"))
                st.caption(
                    f"Summary translated to: {summary_data.get('translated_to', st.session_state.to_lang)}"
                )
            else:
                st.error("API returned unexpected format for summary.")

    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
