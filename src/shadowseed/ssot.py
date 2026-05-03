"""Single Source of Truth manager for SSL 4.5.

The SSOT manager indexes trusted document text in a separate vectorstore. It can
then validate open weightless seeds against that trusted store. The SSOT store
is separate from the seed vectorstore:

- seed vectorstore: uncertain regions and shadow seeds;
- SSOT vectorstore: trusted document chunks supplied by the user or a pipeline.

SSLManager.seeds remains the source of truth for trace, weight, status and
Validation Gate decisions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any
import re

from shadowseed.manager import SSLManager, SeedStatus
from shadowseed.vectorstore.base import VectorStore


@dataclass
class SSOTDocument:
    doc_id: str
    source: str
    trust_level: str = "user_verified"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SSOTManager:
    def __init__(self, vector_store: VectorStore, ssl_manager: SSLManager):
        self.store = vector_store
        self.ssl = ssl_manager
        self.documents: dict[str, SSOTDocument] = {}

    @staticmethod
    def chunk_text(text: str, max_words: int = 80) -> list[str]:
        """Split trusted text into small searchable chunks."""
        words = re.findall(r"\S+", text.strip())
        if not words:
            return []
        chunks = []
        for start in range(0, len(words), max_words):
            chunk = " ".join(words[start : start + max_words]).strip()
            if chunk:
                chunks.append(chunk)
        return chunks

    def ingest_document(
        self,
        doc_text: str,
        doc_id: str,
        source: str = "user_upload",
        trust_level: str = "user_verified",
        chunk_words: int = 80,
    ) -> list[str]:
        """Index a trusted document in the SSOT vectorstore.

        Returns the inserted chunk ids. The method only stores SSOT facts. Seed
        validation is done explicitly through validate_open_seeds_against_ssot().
        """
        document = SSOTDocument(doc_id=doc_id, source=source, trust_level=trust_level)
        self.documents[doc_id] = document
        chunk_ids: list[str] = []
        for index, chunk in enumerate(self.chunk_text(doc_text, max_words=chunk_words), start=1):
            chunk_id = f"{doc_id}::chunk_{index:03d}"
            embedding = self.ssl.get_embedding(chunk)
            self.store.add(
                chunk_id,
                embedding,
                {
                    "doc_id": doc_id,
                    "chunk_index": index,
                    "text": chunk,
                    "source": source,
                    "trust_level": trust_level,
                    "status": "verified",
                    "created_at": document.created_at,
                },
            )
            chunk_ids.append(chunk_id)
        return chunk_ids

    def search(self, query_text: str, top_k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        query_embedding = self.ssl.get_embedding(query_text)
        return self.store.search(query_embedding, top_k=top_k)

    def retrieve_context(self, query_text: str, top_k: int = 3, threshold: float = 0.20) -> list[dict[str, Any]]:
        hits = self.search(query_text, top_k=top_k)
        return [
            {"chunk_id": chunk_id, "similarity": score, "metadata": metadata}
            for chunk_id, score, metadata in hits
            if score >= threshold
        ]

    def validate_open_seeds_against_ssot(
        self,
        threshold: float = 0.20,
        top_k: int = 3,
        max_evidence_per_seed: int = 2,
    ) -> list[dict[str, Any]]:
        """Use SSOT chunks as external evidence for open weightless seeds.

        The SSOT does not directly assign weight. It supplies external evidence;
        the Validation Gate still decides whether weight can grow.
        """
        validations: list[dict[str, Any]] = []
        for seed_id, seed in self.ssl.seeds.items():
            if seed.status in {SeedStatus.PROMOTED, SeedStatus.EXPIRED}:
                continue
            if seed.weight != 0.0:
                continue
            hits = self.store.search(seed.embedding, top_k=top_k)
            accepted_hits = [(chunk_id, score, meta) for chunk_id, score, meta in hits if score >= threshold]
            applied = []
            for chunk_id, score, metadata in accepted_hits[:max_evidence_per_seed]:
                result = self.ssl.run_validation_gate(seed_id, external_evidence=True)
                applied.append(
                    {
                        "chunk_id": chunk_id,
                        "similarity": score,
                        "gate_result": result,
                        "doc_id": metadata.get("doc_id"),
                        "source": metadata.get("source"),
                    }
                )
            if applied:
                validations.append(
                    {
                        "seed_id": seed_id,
                        "seed_text": seed.text,
                        "applied_evidence": applied,
                        "seed_after_validation": self.ssl.get_seed(seed_id).to_dict(),
                    }
                )
        return validations

    def to_dict(self) -> dict[str, Any]:
        return {
            "documents": [document.to_dict() for document in self.documents.values()],
            "chunk_ids": self.store.get_all_ids(),
        }
