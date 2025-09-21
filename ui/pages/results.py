import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Results of text analysis",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

if 'text' not in st.session_state or st.session_state.text == "":
    st.warning("No text submitted yet. Please go to the Homepage to submit text.")
    st.stop()

if __name__ == "__main__":
    st.title("Results of Text Analysis")

    st.write("Here are the results of the text you submitted:")
    st.write(st.session_state.text)

    if st.button("Run Analysis"):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/analyze",  # Your FastAPI backend
                json={"text": st.session_state.text},
                params={"top_pct": 10, "lang": "de", "to_lang": "en"}
            )
            if response.status_code == 200:
                result = response.json()
                st.session_state.analysis = result  # Save for reuse

                # Show frequency table
                df = pd.DataFrame(result["analysis"])
                st.subheader("Word Frequencies")
                st.dataframe(df)

                # Show contexts
                st.subheader("Keyword Contexts")
                for word, matches in result.get("sentences", {}).items():
                    st.markdown(f"**{word}**")
                    for match in matches:
                        st.write(f"- {match['sentence']}")
                        if "translation" in match:
                            st.caption(f"→ {match['translation']}")
            else:
                st.error(f"API Error: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to API: {e}")
