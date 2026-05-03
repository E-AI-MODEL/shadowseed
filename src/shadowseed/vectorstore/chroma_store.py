"""Optional Chroma vectorstore adapter.

Install with:

    pip install -e ".[vector-chroma]"

The adapter stores vectors and metadata in a Chroma collection while keeping the
same VectorStore interface used by the rest of SSL.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import numpy as np

from shadowseed.vectorstore.base import SearchResult, VectorStore


class ChromaVectorStore(VectorStore):
    def __init__(self, collection_name: str = "shadowseed", persist_directory: str | None = None) -> None:
        try:
            import chromadb  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Chroma is optional. Install it with: pip install -e '.[vector-chroma]'"
            ) from exc

        self.collection_name = collection_name
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name=f"{collection_name}_{uuid4().hex[:8]}" if persist_directory is None else collection_name
        )
        self._metadata: dict[str, dict[str, Any]] = {}
        self._embeddings: dict[str, np.ndarray] = {}

    @staticmethod
    def _normalize(embedding: np.ndarray) -> list[float]:
        vector = np.asarray(embedding, dtype=float)
        norm = np.linalg.norm(vector)
        if norm != 0:
            vector = vector / norm
        return vector.tolist()

    @staticmethod
    def _to_chroma_metadata(metadata: dict[str, Any]) -> dict[str, str | int | float | bool]:
        clean: dict[str, str | int | float | bool] = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                clean[key] = value
            else:
                clean[key] = str(value)
        return clean

    def add(self, id: str, embedding: np.ndarray, metadata: dict[str, Any]) -> None:
        vector = self._normalize(embedding)
        self.delete(id)
        self.collection.add(
            ids=[id],
            embeddings=[vector],
            metadatas=[self._to_chroma_metadata(metadata)],
            documents=[str(metadata.get("text", id))],
        )
        self._metadata[id] = dict(metadata)
        self._embeddings[id] = np.asarray(vector, dtype=float)

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[SearchResult]:
        if top_k <= 0 or not self._metadata:
            return []
        query = self._normalize(query_embedding)
        results = self.collection.query(
            query_embeddings=[query],
            n_results=min(top_k, len(self._metadata)),
            include=["metadatas", "distances"],
        )
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        output: list[SearchResult] = []
        for id, distance in zip(ids, distances):
            # Chroma returns distance. Convert to a bounded similarity-like score.
            similarity = 1.0 / (1.0 + float(distance))
            output.append((id, similarity, dict(self._metadata[id])))
        output.sort(key=lambda item: item[1], reverse=True)
        return output

    def update_metadata(self, id: str, metadata: dict[str, Any]) -> None:
        if id not in self._metadata:
            raise KeyError(f"Unknown vector id: {id}")
        self._metadata[id].update(metadata)
        self.collection.update(
            ids=[id],
            metadatas=[self._to_chroma_metadata(self._metadata[id])],
        )

    def get_metadata(self, id: str) -> dict[str, Any]:
        if id not in self._metadata:
            raise KeyError(f"Unknown vector id: {id}")
        return dict(self._metadata[id])

    def get_all_ids(self) -> list[str]:
        return list(self._metadata.keys())

    def delete(self, id: str) -> None:
        if id in self._metadata:
            try:
                self.collection.delete(ids=[id])
            except Exception:
                pass
        self._metadata.pop(id, None)
        self._embeddings.pop(id, None)
