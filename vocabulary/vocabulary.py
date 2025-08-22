import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="User Vocabulary API")

class VocabItem(BaseModel):
    user_id: str
    word: str
    translation: str
    sentences: List[str]

class DeleteSentencesItem(BaseModel):
    user_id: str
    word: str
    sentences: List[str]

class DeleteWordItem(BaseModel):
    user_id: str
    word: str

class UpdateTranslationItem(BaseModel):
    user_id: str
    word: str
    new_translation: str

class BatchVocabItems(BaseModel):
    items: List[VocabItem]
    
class BatchDeleteWords(BaseModel):
    user_id: str
    words: List[str]    

PG_CONN_PARAMS = {
    "host": "localhost",
    "port": 5432,
    "user": "admin",
    "password": "admin",
    "database": "SmartVocabulary"
}

def create_table_if_not_exists():
    conn = psycopg2.connect(**PG_CONN_PARAMS)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_vocabulary (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            word TEXT NOT NULL,
            translation TEXT NOT NULL,
            sentences TEXT[] NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(user_id, word)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def insert_or_update_vocab(item: VocabItem):
    conn = psycopg2.connect(**PG_CONN_PARAMS)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_vocabulary (user_id, word, translation, sentences)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, word) DO UPDATE
        SET translation = EXCLUDED.translation,
            sentences = array(SELECT DISTINCT unnest(user_vocabulary.sentences || EXCLUDED.sentences));
    """, (item.user_id, item.word, item.translation, item.sentences))
    conn.commit()
    cur.close()
    conn.close()

def get_user_vocab(user_id: str):
    conn = psycopg2.connect(**PG_CONN_PARAMS)
    cur = conn.cursor()
    cur.execute("""
        SELECT word, translation, sentences 
        FROM user_vocabulary 
        WHERE user_id = %s
        ORDER BY word;
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"word": r[0], "translation": r[1], "sentences": r[2]} for r in rows]

def delete_word(user_id: str, word: str):
    conn = psycopg2.connect(**PG_CONN_PARAMS)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM user_vocabulary
        WHERE user_id = %s AND word = %s;
    """, (user_id, word))
    conn.commit()
    cur.close()
    conn.close()

def delete_sentences(user_id: str, word: str, sentences_to_delete: List[str]):
    conn = psycopg2.connect(**PG_CONN_PARAMS)
    cur = conn.cursor()
    cur.execute("""
        SELECT sentences FROM user_vocabulary
        WHERE user_id = %s AND word = %s;
    """, (user_id, word))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        raise ValueError("Word not found")
    existing_sentences = row[0]
    updated_sentences = [s for s in existing_sentences if s not in sentences_to_delete]
    if updated_sentences:
        cur.execute("""
            UPDATE user_vocabulary
            SET sentences = %s
            WHERE user_id = %s AND word = %s;
        """, (updated_sentences, user_id, word))
    else:
        # Delete word if no sentences remain
        cur.execute("""
            DELETE FROM user_vocabulary
            WHERE user_id = %s AND word = %s;
        """, (user_id, word))
    conn.commit()
    cur.close()
    conn.close()

def update_translation(user_id: str, word: str, new_translation: str):
    conn = psycopg2.connect(**PG_CONN_PARAMS)
    cur = conn.cursor()
    cur.execute("""
        UPDATE user_vocabulary
        SET translation = %s
        WHERE user_id = %s AND word = %s;
    """, (new_translation, user_id, word))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise ValueError("Word not found")
    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
def startup_event():
    create_table_if_not_exists()

@app.post("/vocabulary/")
async def add_or_update_vocab_endpoint(item: VocabItem):
    try:
        insert_or_update_vocab(item)
        return {"status": "success", "message": f"Word '{item.word}' saved/updated for user {item.user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vocabulary/{user_id}")
async def get_user_vocab_endpoint(user_id: str):
    try:
        vocab_list = get_user_vocab(user_id)
        return {"user_id": user_id, "vocabulary": vocab_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/vocabulary/word/")
async def delete_word_endpoint(item: DeleteWordItem):
    try:
        delete_word(item.user_id, item.word)
        return {"status": "success", "message": f"Word '{item.word}' deleted for user {item.user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/vocabulary/sentences/")
async def delete_sentences_endpoint(item: DeleteSentencesItem):
    try:
        delete_sentences(item.user_id, item.word, item.sentences)
        return {"status": "success", "message": f"Specified sentences deleted for word '{item.word}' of user {item.user_id}"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/vocabulary/translation/")
async def update_translation_endpoint(item: UpdateTranslationItem):
    try:
        update_translation(item.user_id, item.word, item.new_translation)
        return {"status": "success", "message": f"Translation updated for word '{item.word}' of user {item.user_id}"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/vocabulary/batch/")
async def add_or_update_vocab_batch(batch: BatchVocabItems):
    try:
        for item in batch.items:
            insert_or_update_vocab(item)
        return {"status": "success", "message": f"{len(batch.items)} words saved/updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/vocabulary/words/batch/")
async def delete_words_batch(batch: BatchDeleteWords):
    try:
        for word in batch.words:
            delete_word(batch.user_id, word)
        return {"status": "success", "message": f"{len(batch.words)} words deleted successfully for user {batch.user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
