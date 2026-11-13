"""Real embedding provider adapter using SentenceTransformers multilingual model."""
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from typing import Protocol
import numpy as np


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class MyEmbedder:
    """SentenceTransformer embedding provider adapter (multilingual, 384 dimensions)."""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> None:
        self.model_name = model_name
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(model_name, local_files_only=True)
        except Exception as e:
            # Fallback without local_files_only flag if unsupported
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(model_name)
            
        test_vec = self._model.encode("test", convert_to_numpy=True)
        self.dimensions = int(test_vec.shape[0])

    def embed_documents(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """Generate normalized dense embeddings for a list of document chunks."""
        if not texts:
            return []
        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def embed_query(self, question: str) -> list[float]:
        """Generate a normalized dense embedding vector for a query."""
        if not question:
            raise ValueError("Query string cannot be empty.")
        vector = self._model.encode(
            question,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return vector.tolist()
