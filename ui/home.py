import streamlit as st

st.set_page_config(
    page_title="Homepage",
    page_icon="🏡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Permanent session state ---
for key, default in [('text', ''), ('summarize', False), ('to_lang', 'en')]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- Temporary widget keys ---
TEMP_KEYS = {
    "_text_area": "text",
    "_summarize": "summarize"
}

for temp_key, perm_key in TEMP_KEYS.items():
    if temp_key not in st.session_state:
        st.session_state[temp_key] = st.session_state[perm_key]

# --- Callbacks to sync temporary -> permanent ---
def keep_text():
    st.session_state['text'] = st.session_state['_text_area']

def keep_summarize():
    st.session_state['summarize'] = st.session_state['_summarize']

# --- Widgets ---
st.text_area(
    "Enter text to analyze:",
    value=st.session_state['_text_area'],
    key="_text_area",
    on_change=keep_text
)

st.checkbox(
    "Run a summary on the provided text",
    value=st.session_state['_summarize'],
    key="_summarize",
    on_change=keep_summarize
)

st.text_input(
    "Target translation language (e.g., 'en', 'de', 'fr'):",
    value=st.session_state.to_lang,
    key="to_lang"
)

# --- Submit ---
if st.button("Submit"):
    st.success(
        f"Submitted!\nText: {st.session_state.text}\n"
        f"Summarize: {st.session_state.summarize}\n"
        f"Target language: {st.session_state.to_lang}"
    )
