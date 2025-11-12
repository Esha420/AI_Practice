"""
preprocess.py

CLI: preprocess.py input_folder/ output.jsonl

Automates:
1. Data Cleaning
2. Chunking
3. Formatting for embeddings
"""

import os
import sys
import re
import json
from tqdm import tqdm
import spacy
import tiktoken
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from PyPDF2 import PdfReader
from docx import Document

# ---------------------------
# Setup
# ---------------------------
nltk.download("stopwords", quiet=True)
STOPWORDS = set(stopwords.words("english"))

nlp = spacy.load("en_core_web_sm")
encoding = tiktoken.get_encoding("cl100k_base")  # for token counting

# ---------------------------
# Utility Functions
# ---------------------------

def read_file(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif ext == ".pdf":
        reader = PdfReader(filepath)
        return " ".join(page.extract_text() or "" for page in reader.pages)
    elif ext == ".docx":
        doc = Document(filepath)
        return " ".join(p.text for p in doc.paragraphs)
    elif ext == ".json":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Concatenate text from list of dicts or strings
            if isinstance(data, list):
                texts = []
                for entry in data:
                    if isinstance(entry, dict):
                        texts.append(entry.get("text", ""))
                    else:
                        texts.append(str(entry))
                return " ".join(texts)
            return ""
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def clean_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = BeautifulSoup(text, "html.parser").get_text(separator=" ")
    text = re.sub(r"[^a-zA-Z0-9.,!?;:'\"()\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.lower()
    words = [w for w in text.split() if w not in STOPWORDS]
    return " ".join(words)

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

def chunk_text(text: str, max_tokens: int = 800, overlap: int = 100):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    chunks = []
    current_chunk = []
    current_length = 0

    for sent in sentences:
        sent_len = count_tokens(sent)
        if current_length + sent_len > max_tokens and current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(chunk_text)
            # overlap
            overlap_tokens = encoding.encode(chunk_text)[-overlap:]
            overlap_text = encoding.decode(overlap_tokens)
            current_chunk = [overlap_text]
            current_length = count_tokens(overlap_text)

        current_chunk.append(sent)
        current_length += sent_len

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# ---------------------------
# Main Preprocessing Function
# ---------------------------

def preprocess_folder(input_folder: str, output_path: str, max_tokens=800, overlap=100):
    results = []
    chunk_id = 1
    filepaths = [os.path.join(input_folder, f) for f in os.listdir(input_folder)
                 if os.path.isfile(os.path.join(input_folder, f))]

    for filepath in tqdm(filepaths, desc="Processing files"):
        source_name = os.path.basename(filepath)
        try:
            raw_text = read_file(filepath)
            cleaned = clean_text(raw_text)
            if not cleaned:
                continue
            chunks = chunk_text(cleaned, max_tokens=max_tokens, overlap=overlap)
            for i, chunk in enumerate(chunks):
                results.append({
                    "id": f"{source_name}_chunk_{i+1}",
                    "text": chunk,
                    "metadata": {
                        "source": source_name,
                        "chunk_index": i+1
                    }
                })
                chunk_id += 1
        except Exception as e:
            print(f"Skipping {filepath}: {e}")

    # Save as JSONL
    with open(output_path, "w", encoding="utf-8") as f:
        for record in results:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\nPreprocessing complete. {len(results)} chunks saved → {output_path}")

# ---------------------------
# CLI Entry
# ---------------------------

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python preprocess.py <input_folder> <output.jsonl>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_path = sys.argv[2]

    preprocess_folder(input_folder, output_path)
