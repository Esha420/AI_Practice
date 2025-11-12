"""
data_chunking.py

Splits cleaned text into sentence-based chunks with overlapping context.
Output: JSON list of chunks like { "id": 1, "chunk": "..." }
"""

import json
import uuid
from tqdm import tqdm
import spacy
import tiktoken

# Load spaCy model for sentence segmentation
nlp = spacy.load("en_core_web_sm")

# Load tokenizer (for accurate token length counting)
encoding = tiktoken.get_encoding("cl100k_base")  # compatible with OpenAI embeddings

def count_tokens(text: str) -> int:
    """Count tokens in a string using tiktoken."""
    return len(encoding.encode(text))

def chunk_text(text: str, max_tokens: int = 800, overlap: int = 100):
    """
    Split text into sentence-based chunks with overlapping context.

    Args:
        text (str): The input text.
        max_tokens (int): Target max tokens per chunk (default 800).
        overlap (int): Number of overlapping tokens between chunks.

    Returns:
        List of chunks (strings).
    """
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    chunks = []
    current_chunk = []
    current_length = 0

    for sent in sentences:
        sent_len = count_tokens(sent)

        # If adding this sentence exceeds limit → finalize current chunk
        if current_length + sent_len > max_tokens and current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(chunk_text)

            # Overlap handling: keep last few tokens for next chunk
            overlap_tokens = encoding.encode(chunk_text)[-overlap:]
            overlap_text = encoding.decode(overlap_tokens)

            current_chunk = [overlap_text]  # start next chunk with overlap
            current_length = count_tokens(overlap_text)

        current_chunk.append(sent)
        current_length += sent_len

    # Add any remaining text as a final chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def chunk_file(input_path: str, output_path: str, max_tokens=800, overlap=100):
    """
    Reads cleaned text JSON and produces chunked JSON output.
    Input format: [{"text": "..."}, ...]
    Output format: [{"id": 1, "chunk": "..."}]
    """
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    chunk_id = 1

    for entry in tqdm(data, desc="Chunking documents"):
        text = entry.get("text", "").strip()
        if not text:
            continue
        chunks = chunk_text(text, max_tokens=max_tokens, overlap=overlap)
        for chunk in chunks:
            results.append({
                "id": chunk_id,
                "chunk": chunk
            })
            chunk_id += 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Chunking complete. {len(results)} chunks saved to {output_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Split cleaned text into overlapping chunks.")
    parser.add_argument("input_path", help="Path to cleaned JSON file (from data_cleaning.py)")
    parser.add_argument("output_path", help="Path to save chunked JSON file")
    parser.add_argument("--max_tokens", type=int, default=800, help="Max tokens per chunk")
    parser.add_argument("--overlap", type=int, default=100, help="Token overlap between chunks")
    args = parser.parse_args()

    chunk_file(args.input_path, args.output_path, args.max_tokens, args.overlap)
