"""Store and search vectors using persistent Qdrant embedded engine."""
import uuid
from pathlib import Path
from typing import Any
import qdrant_client
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from .models import Chunk


class QdrantVectorStore:
    """Persistent on-disk Vector Store using Qdrant client."""

    def __init__(self, db_path: str = "./starter/results/qdrant_db", dimensions: int = 384) -> None:
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.dimensions = dimensions
        self.client = qdrant_client.QdrantClient(path=str(self.db_path))

    def create_schema(self, strategy: str) -> None:
        """Create or reset collection for a given strategy."""
        collection_name = f"collection_{strategy.lower()}"
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=self.dimensions, distance=Distance.COSINE)
            )

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Write chunks and vectors with stable IDs; ensure idempotent re-ingestion."""
        if len(chunks) != len(vectors):
            raise ValueError(f"Mismatch: {len(chunks)} chunks vs {len(vectors)} vectors.")

        collection_name = f"collection_{strategy.lower()}"
        self.create_schema(strategy)

        points: list[PointStruct] = []
        for chunk, vector in zip(chunks, vectors):
            # Generate deterministic UUID5 from chunk_id for stable, collision-free identity
            point_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
            payload = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "source": chunk.source,
                "page": chunk.page,
                "text": chunk.text,
                **chunk.metadata
            }
            points.append(
                PointStruct(
                    id=point_uuid,
                    vector=vector,
                    payload=payload
                )
            )

        # Upsert in batches of 64
        batch_size = 64
        for i in range(0, len(points), batch_size):
            self.client.upsert(
                collection_name=collection_name,
                points=points[i:i + batch_size]
            )

    def search(
        self,
        strategy: str,
        query_vector: list[float],
        top_k: int = 3,
        filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Filter metadata, rank by cosine similarity, and return top-k matches."""
        collection_name = f"collection_{strategy.lower()}"

        query_filter = None
        if filters:
            must_conditions = []
            for k, v in filters.items():
                must_conditions.append(
                    FieldCondition(key=k, match=MatchValue(value=v))
                )
            if must_conditions:
                query_filter = Filter(must=must_conditions)

        # Perform query points search
        res = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True
        )

        hits: list[dict[str, Any]] = []
        for point in res.points:
            p = point.payload or {}
            hits.append({
                "chunk_id": p.get("chunk_id", str(point.id)),
                "document_id": p.get("document_id", ""),
                "source": p.get("source", ""),
                "page": p.get("page", 0),
                "section": p.get("section", ""),
                "text": p.get("text", ""),
                "score": float(point.score),
                "metadata": p
            })

        return hits
