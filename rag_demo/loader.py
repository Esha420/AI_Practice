# loader.py
import json
from typing import List, Dict, Optional

class ChunkLoader:
    """
    Class to load preprocessed chunks from a JSONL file.
    """

    def __init__(self, file_path: str):
        """
        Args:
            file_path (str): Path to JSONL file containing chunks.
        """
        self.file_path = file_path
        self.chunks: List[Dict] = []

    def load(self, filter_source: Optional[str] = None) -> List[Dict]:
        """
        Load chunks from the JSONL file.

        Args:
            filter_source (str, optional): If provided, only load chunks from this source.

        Returns:
            List[Dict]: List of chunks as dictionaries with keys 'id', 'text', 'metadata'.
        """
        loaded_chunks = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                chunk = json.loads(line)
                if filter_source:
                    if chunk.get("metadata", {}).get("source") == filter_source:
                        loaded_chunks.append(chunk)
                else:
                    loaded_chunks.append(chunk)

        self.chunks = loaded_chunks
        return self.chunks

    def get_chunk_by_id(self, chunk_id: str) -> Dict:
        """
        Retrieve a chunk by its unique ID.

        Args:
            chunk_id (str): ID of the chunk.

        Returns:
            Dict: Chunk dictionary.
        """
        for chunk in self.chunks:
            if chunk.get("id") == chunk_id:
                return chunk
        return {}
