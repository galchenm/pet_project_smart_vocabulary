"""
This code automates the downloading of various open-source textual resources:

1. 📚 Project Gutenberg books (in plain text format)
2. 📄 arXiv academic papers (as PDF)
3. 📖 Short stories from public websites (via web scraping)

All downloaded files are saved into the `data/` folder. The script includes basic error handling
and supports filename sanitization for organized storage.

Dependencies:
- requests
- beautifulsoup4 (for short story scraping)
"""

import os
import requests
from bs4 import BeautifulSoup

# Create data folder
os.makedirs("data", exist_ok=True)

# --- 1. PROJECT GUTENBERG ---
def download_gutenberg_book(book_id, filename):
    """Download a book from Project Gutenberg.

    Args:
        book_id (int): The ID of the Gutenberg book.
        filename (str): The desired filename for the downloaded book.
    """
    urls = [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt"
    ]
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"data/{filename}.txt", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"[Gutenberg] Downloaded: {filename}")
            return
    print(f"[Gutenberg] Failed: {book_id}")

# --- 2. ARXIV ---
def download_arxiv_paper(arxiv_id, filename):
    """Download a paper from arXiv.

    Args:
        arxiv_id (str): The ID of the arXiv paper.
        filename (str): The desired filename for the downloaded paper.
    """
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"data/{filename}.pdf", "wb") as f:
            f.write(response.content)
        print(f"[arXiv] Downloaded: {filename}")
    else:
        print(f"[arXiv] Failed: {arxiv_id}")

# --- 3. SHORT STORY (web scraping) ---
def download_short_story(url, filename):
    """Download a short story from a website.

    Args:
        url (str): The URL of the short story.
        filename (str): The desired filename for the downloaded story.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        with open(f"data/{filename}.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[Short Story] Downloaded: {filename}")
    except Exception as e:
        print(f"[Short Story] Failed ({filename}): {e}")

