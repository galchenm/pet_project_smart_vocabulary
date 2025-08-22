import pytest
from fastapi.testclient import TestClient
from .vocabulary import app 

client = TestClient(app)

vocab_item = {
    "user_id": "test_user",
    "word": "AI",
    "translation": "ИИ",
    "sentences": ["Artificial intelligence is transforming industries."]
}

batch_items = {
    "items": [
        {
            "user_id": "test_user",
            "word": "AI",
            "translation": "ИИ",
            "sentences": ["Artificial intelligence is transforming industries."]
        },
        {
            "user_id": "test_user",
            "word": "Ethics",
            "translation": "Этика",
            "sentences": ["Ethical considerations are important in AI."]
        }
    ]
}

delete_words_batch = {
    "user_id": "test_user",
    "words": ["AI", "Ethics"]
}

def test_add_vocab():
    response = client.post("/vocabulary/", json=vocab_item)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_get_vocab():
    response = client.get(f"/vocabulary/{vocab_item['user_id']}")
    assert response.status_code == 200
    data = response.json()
    assert any(w["word"] == "AI" for w in data["vocabulary"])

def test_update_translation():
    response = client.put("/vocabulary/translation/", json={
        "user_id": "test_user",
        "word": "AI",
        "new_translation": "Искусственный интеллект"
    })
    assert response.status_code == 200
    data = response.json()
    assert "Translation updated" in data["message"]

def test_batch_insert():
    response = client.post("/vocabulary/batch/", json=batch_items)
    assert response.status_code == 200
    data = response.json()
    assert "2 words saved/updated" in data["message"]

def test_batch_delete():
    response = client.delete("/vocabulary/words/batch/", json=delete_words_batch)
    assert response.status_code == 200
    data = response.json()
    assert "2 words deleted" in data["message"]
