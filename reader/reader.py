"""
Reads text from various file formats.
"""

import fitz  # PyMuPDF for PDF reading
from ebooklib import epub
from bs4 import BeautifulSoup


def read_txt(path):
    """Reads text from a TXT file.

    Args:
        path (str): The file path to the TXT file.

    Returns:
        str: The extracted text from the TXT file.
    """
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def read_pdf(path):
    """Reads text from a PDF file.

    Args:
        path (str): The file path to the PDF file.

    Returns:
        str: The extracted text from the PDF file.
    """
    
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)

def read_epub(path):
    """Reads text from an EPUB file.

    Args:
        path (str): The file path to the EPUB file.

    Returns:
        str: The extracted text from the EPUB file.
    """
    book = epub.read_epub(path)
    text = ""
    for item in book.get_items():
        if item.get_type() == epub.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text += soup.get_text() + "\n"
    return text

def read_html_txt(path):  # from web-scraped .txt with HTML remnants
    """Reads text from an HTML file.

    Args:
        path (str): The file path to the HTML file.

    Returns:
        str: The extracted text from the HTML file.
    """
    with open(path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        return soup.get_text()


def extract_text(path):
    """Extract text from various file formats.

    Args:
        path (str): The file path to extract text from.

    Returns:
        str: The extracted text or an error message.
    """
    if not path:
        return "No file path provided."
    if path.endswith(".pdf"):
        return read_pdf(path)
    elif path.endswith(".txt"):
        return read_txt(path)
    elif path.endswith(".epub"):
        return read_epub(path)
    else:
        try:
            return read_html_txt(path)
        except:
            print(f"Unsupported format: {path}")
        return None