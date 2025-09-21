import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Build Vocabulary",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

if 'analysis' not in st.session_state or st.session_state.analysis is None:
    st.warning("No analysis results available. Please run text analysis first.")
    st.stop()

if __name__ == "__main__":
    st.title("Build Vocabulary")

    result = st.session_state.analysis
    vocab = result["vocabulary"]

    st.subheader("Vocabulary List")
    df = pd.DataFrame(vocab, columns=["Word"])
    st.dataframe(df)

    # Download as CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Vocabulary CSV",
        data=csv,
        file_name="vocabulary.csv",
        mime="text/csv"
    )
