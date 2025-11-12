"""
format_for_embeddings.py

Converts chunked JSON data into a JSONL format ready for embedding ingestion.
Each chunk gets a unique ID and optional metadata.
"""

import json
import os
from tqdm import tqdm

def format_chunks_for_embeddings(input_path: str, output_path: str, source_name: str = None):
    """
    Args:
        input_path: Path to chunked JSON (from data_chunking.py)
        output_path: Path to save JSONL file
        source_name: Optional string to include in metadata (e.g., original file name)
    """
    with open(input_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with open(output_path, "w", encoding="utf-8") as f_out:
        for i, chunk in enumerate(tqdm(chunks, desc="Formatting for embeddings")):
            chunk_id = f"{source_name}_chunk_{i+1}" if source_name else f"chunk_{i+1}"
            record = {
                "id": chunk_id,
                "text": chunk.get("chunk", ""),
                "metadata": {
                    "source": source_name or "unknown",
                    "chunk_index": i+1
                }
            }
            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Formatting complete. {len(chunks)} chunks saved to {output_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Format chunked text for embedding ingestion.")
    parser.add_argument("input_path", help="Path to chunked JSON file")
    parser.add_argument("output_path", help="Path to save JSONL file")
    parser.add_argument("--source_name", default=None, help="Optional source name for metadata")
    args = parser.parse_args()

    format_chunks_for_embeddings(args.input_path, args.output_path, args.source_name)
