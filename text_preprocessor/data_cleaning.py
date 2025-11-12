"""
data_cleaning.py

A script for cleaning raw text data:
- Removes HTML tags
- Removes special characters and excessive whitespace
- Normalizes casing (lowercase)
- Removes stopwords using NLTK
- Handles missing or null entries
"""

import os
import re
import json
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from tqdm import tqdm

# Download stopwords once
nltk.download('stopwords', quiet=True)
STOPWORDS = set(stopwords.words('english'))

def clean_text(text: str) -> str:
    """
    Cleans a given text string by removing HTML, punctuation,
    stopwords, and normalizing whitespace/case.
    """
    if not text or not isinstance(text, str):
        return ""

    # 1. Remove HTML tags
    text = BeautifulSoup(text, "html.parser").get_text(separator=" ")

    # 2. Remove special characters except sentence punctuation
    text = re.sub(r"[^a-zA-Z0-9.,!?;:'\"()\s]", " ", text)

    # 3. Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # 4. Normalize casing (lowercase)
    text = text.lower()

    # 5. Remove stopwords
    words = [w for w in text.split() if w not in STOPWORDS]
    cleaned = " ".join(words)

    return cleaned


def clean_dataset(input_path: str, output_path: str):
    """
    Cleans all text entries in a JSON or TXT dataset.
    Input:
        - input_path: file path containing text data
        - output_path: file path for cleaned data
    """
    cleaned_data = []

    # Determine file type
    ext = os.path.splitext(input_path)[1].lower()
    if ext == ".json":
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for entry in tqdm(data, desc="Cleaning JSON entries"):
                text = entry.get("text", "") if isinstance(entry, dict) else str(entry)
                cleaned_text = clean_text(text)
                if cleaned_text:
                    cleaned_data.append({"text": cleaned_text})
    elif ext == ".txt":
        with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for line in tqdm(lines, desc="Cleaning text lines"):
                cleaned_text = clean_text(line)
                if cleaned_text:
                    cleaned_data.append({"text": cleaned_text})
    else:
        raise ValueError("Unsupported file format. Use .json or .txt")

    # Save cleaned data
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

    print(f"Cleaning complete. {len(cleaned_data)} cleaned entries saved to {output_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean raw text data for NLP/RAG.")
    parser.add_argument("input_path", help="Path to input .json or .txt file")
    parser.add_argument("output_path", help="Path to save cleaned JSON file")
    args = parser.parse_args()

    clean_dataset(args.input_path, args.output_path)
