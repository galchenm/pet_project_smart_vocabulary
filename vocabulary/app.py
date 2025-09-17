import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000"

st.title("Smart Vocabulary Manager")

# User ID input (common to all tabs)
user_id = st.text_input("User ID", "")

# Create tabs
tabs = st.tabs([
    "View Vocabulary",
    "Add / Update Word",
    "Batch Upload",
    "Delete Word",
    "Delete Sentences",
    "Update Translation"
])

# -----------------------------
# Tab 1: View Vocabulary
# -----------------------------
with tabs[0]:
    st.header("View Vocabulary")
    if st.button("Get Vocabulary"):
        if not user_id:
            st.error("User ID is required!")
        else:
            r = requests.get(f"{API_URL}/vocabulary/{user_id}")
            if r.ok:
                vocab_list = r.json().get("vocabulary", [])
                if vocab_list:
                    for item in vocab_list:
                        with st.expander(item["word"]):
                            st.write(f"Translation: {item['translation']}")
                            st.write(f"Sentences: {', '.join(item['sentences'])}")
                else:
                    st.info("No vocabulary found for this user.")
            else:
                st.error(f"Error: {r.text}")

# -----------------------------
# Tab 2: Add / Update Word
# -----------------------------
with tabs[1]:
    st.header("Add / Update Word")
    word = st.text_input("Word", key="word_input")
    translation = st.text_input("Translation", key="translation_input")
    sentences = st.text_area("Sentences (comma-separated)", key="sentences_input")
    if st.button("Add / Update Word"):
        if not user_id or not word:
            st.error("User ID and Word are required!")
        else:
            payload = {
                "user_id": user_id,
                "word": word,
                "translation": translation,
                "sentences": [s.strip() for s in sentences.split(",") if s.strip()]
            }
            r = requests.post(f"{API_URL}/vocabulary/", json=payload)
            if r.ok:
                st.success(r.json().get("message"))
            else:
                st.error(f"Error: {r.text}")

# -----------------------------
# Tab 3: Batch Upload
# -----------------------------
with tabs[2]:
    st.header("Batch Add / Update Words")
    batch_input = st.text_area(
        "Enter words in JSON format. Example:\n"
        '[{"user_id": "user1", "word": "hello", "translation": "hola", "sentences": ["Hi there"]}, {...}]'
    )
    if st.button("Batch Upload"):
        if not batch_input:
            st.error("Please provide JSON input")
        else:
            try:
                data = {"items": json.loads(batch_input)}
                r = requests.post(f"{API_URL}/vocabulary/batch/", json=data)
                if r.ok:
                    st.success(r.json().get("message"))
                else:
                    st.error(f"Error: {r.text}")
            except Exception as e:
                st.error(f"Invalid JSON: {e}")

# -----------------------------
# Tab 4: Delete Word
# -----------------------------
with tabs[3]:
    st.header("Delete Word")
    del_word = st.text_input("Word to delete", key="del_word_input")
    if st.button("Delete Word"):
        if not user_id or not del_word:
            st.error("User ID and Word are required!")
        else:
            payload = {"user_id": user_id, "word": del_word}
            r = requests.delete(f"{API_URL}/vocabulary/word/", json=payload)
            if r.ok:
                st.success(r.json().get("message"))
            else:
                st.error(f"Error: {r.text}")

# -----------------------------
# Tab 5: Delete Sentences
# -----------------------------
with tabs[4]:
    st.header("Delete Sentences")
    del_sent_word = st.text_input("Word to delete sentences from", key="del_sent_word_input")
    del_sentences = st.text_area("Sentences to delete (comma-separated)", key="del_sentences_input")
    if st.button("Delete Sentences"):
        if not user_id or not del_sent_word or not del_sentences:
            st.error("User ID, Word, and sentences are required!")
        else:
            payload = {
                "user_id": user_id,
                "word": del_sent_word,
                "sentences": [s.strip() for s in del_sentences.split(",") if s.strip()]
            }
            r = requests.delete(f"{API_URL}/vocabulary/sentences/", json=payload)
            if r.ok:
                st.success(r.json().get("message"))
            else:
                st.error(f"Error: {r.text}")

# -----------------------------
# Tab 6: Update Translation
# -----------------------------
with tabs[5]:
    st.header("Update Translation")
    upd_word = st.text_input("Word to update translation", key="upd_word_input")
    new_translation = st.text_input("New Translation", key="new_translation_input")
    if st.button("Update Translation"):
        if not user_id or not upd_word or not new_translation:
            st.error("User ID, Word, and new translation are required!")
        else:
            payload = {"user_id": user_id, "word": upd_word, "new_translation": new_translation}
            r = requests.put(f"{API_URL}/vocabulary/translation/", json=payload)
            if r.ok:
                st.success(r.json().get("message"))
            else:
                st.error(f"Error: {r.text}")
