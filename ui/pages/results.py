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

# Ensure session_state keys exist
if 'text' not in st.session_state or not st.session_state.text:
    st.warning("No text submitted yet. Please go to the Homepage to submit text.")
    st.stop()

if 'to_lang' not in st.session_state:
    st.session_state.to_lang = "en"

if __name__ == "__main__":
    st.title("Results of Text Analysis")

    st.write("Here are the results of the text you submitted:")
    st.write(st.session_state.text)
    st.write(
        f"Target translation language: {st.session_state.to_lang} "
        f"({LANGUAGE_CODES.get(st.session_state.to_lang, 'en_XX')})"
    )

    # Optional summarization
    summarize = st.checkbox("Summarize text using frequent words")

    payload = {
        "text": st.session_state.text,
        "summarize": summarize,
        "summary_translate_to": st.session_state.to_lang if summarize else None
    }

    try:
        response = requests.post(
            "http://127.0.0.1:8000/analyze",  # single endpoint handles analysis + summary
            json=payload,
            params={
                "top_pct": 10,
                "lang": "de",
                "to_lang": LANGUAGE_CODES.get(st.session_state.to_lang, "en_XX")
            }
        )

        if response.status_code == 200:
            result = response.json()

            # Make sure result is a dict
            if isinstance(result, dict):
                st.session_state.analysis = result

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

                # --- Optional Summary ---
                summary_data = result.get("summary")
                if summarize and isinstance(summary_data, dict):
                    st.subheader("Summary")
                    st.write(summary_data.get("final_summary", "No summary returned"))
                    st.caption(f"Summary translated to: {summary_data.get('translated_to', st.session_state.to_lang)}")
            else:
                st.error("API returned unexpected response format.")

        else:
            st.error(f"API Error: {response.text}")

    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
