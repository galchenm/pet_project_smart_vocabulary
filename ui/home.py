import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Homepage",
    page_icon="🏡",
    layout="centered",
    initial_sidebar_state="expanded"
)

if 'text' not in st.session_state:
    st.session_state.text = ""

# Workaround from: https://stackoverflow.com/questions/74968179/session-state-is-reset-in-streamlit-multipage-app


def keep(key):
    # Copy from temporary widget key to permanent key
    st.session_state[key] = st.session_state[f"_{key}"]


def unkeep(key):
    # Copy from permanent key to temporary widget key
    st.session_state[f"_{key}"] = st.session_state[key]


if __name__ == "__main__":

    st.title("Homepage")
    st.text_area("Enter text:", value=st.session_state.text, on_change=keep, args=("text_area",), key="text_area")

    if st.button("Submit"):
        st.session_state.text = st.session_state.text_area
        st.success("Text submitted successfully!")
        unkeep("text_area")
