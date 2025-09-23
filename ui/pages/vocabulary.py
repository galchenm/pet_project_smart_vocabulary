import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Build Vocabulary",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Check that analysis results exist
if 'analysis' not in st.session_state or st.session_state.analysis is None:
    st.warning("No analysis results available. Please run text analysis first.")
    st.stop()

# Initialize vocabulary table in session_state
if 'vocab_table' not in st.session_state:
    rows = []
    analysis = st.session_state.analysis
    for word, matches in analysis.get("sentences", {}).items():
        word_translation = analysis.get("translation", {}).get(word, "")
        if not matches:
            rows.append({
                "Word": word,
                "Word Translation": word_translation,
                "Context": "",
                "Context Translation": ""
            })
        else:
            for match in matches:
                rows.append({
                    "Word": word,
                    "Word Translation": word_translation,
                    "Context": match.get("sentence", ""),
                    "Context Translation": match.get("translation", "")
                })
    st.session_state.vocab_table = pd.DataFrame(rows)


def remove_word(word):
    st.session_state.vocab_table = st.session_state.vocab_table[st.session_state.vocab_table["Word"] != word]

def remove_context(idx):
    st.session_state.vocab_table = st.session_state.vocab_table.drop(idx).reset_index(drop=True)

if __name__ == "__main__":
    st.title("Build Vocabulary")

    st.subheader("Manage Vocabulary")

    df = st.session_state.vocab_table.copy()

    for idx, row in df.iterrows():
        st.markdown(f"**{row['Word']}**")
        if row['Word Translation']:
            st.caption(f"→ Word Translation: {row['Word Translation']}")
        st.write(f"- Context: {row['Context']}")
        if row['Context Translation']:
            st.caption(f"→ Context Translation: {row['Context Translation']}")
        col1, col2 = st.columns(2)
        if col1.button("Remove Word", key=f"word_{idx}"):
            remove_word(row['Word'])
        if col2.button("Remove This Example", key=f"context_{idx}"):
            remove_context(idx)

    st.subheader("Current Vocabulary Table")
    st.dataframe(st.session_state.vocab_table)

    # Download CSV
    csv = st.session_state.vocab_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Vocabulary CSV",
        data=csv,
        file_name="vocabulary.csv",
        mime="text/csv"
    )
