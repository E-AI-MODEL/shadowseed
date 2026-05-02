"""
Shadow Seed Learning 4.5

Benchmarkgerichte Niveau 1 implementatie, afgeleid van de publieke SSL 4.5 release.

Belangrijk:
    - een seed is atomisch
    - trace meet aanwezigheid
    - weight meet invloed
    - weight start altijd op 0.0
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Iterable
import math
import re

import numpy as np


class SeedStatus(str, Enum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    DECAYING = "DECAYING"
    DORMANT = "DORMANT"
    PROMOTED = "PROMOTED"
    EXPIRED = "EXPIRED"


@dataclass
class ShadowSeed:
    id: str
    text: str
    embedding: np.ndarray
    trigger_keywords: list[str] = field(default_factory=list)
    trace: float = 2.0
    weight: float = 0.0
    occurrence_count: int = 1
    evidence_count: int = 0
    status: SeedStatus = SeedStatus.NEW
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        data = asdict(self)
        data["embedding"] = self.embedding.tolist()
        data["status"] = self.status.value
        return data


@dataclass
class Constellation:
    members: list[str]
    centroid: list[float]
    combined_weight: float

    def to_dict(self) -> dict:
        return asdict(self)


class SSLManager:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        half_life_turns: float = 3,
        dedup_threshold: float = 0.85,
        promotion_threshold: float = 0.5,
        dormant_threshold: float = 0.05,
        validation_increment: float = 0.2,
        contradiction_penalty: float = 0.3,
        max_trace: float = 3.0,
        reactivation_increment: float = 2.0,
        embedding_fn: Callable[[str], np.ndarray] | None = None,
    ):
        self._embedding_fn = embedding_fn
        self.model_name = model_name
        self._embedder = None
        self.seeds: dict[str, ShadowSeed] = {}
        self.half_life_turns = half_life_turns
        self.dedup_threshold = dedup_threshold
        self.promotion_threshold = promotion_threshold
        self.dormant_threshold = dormant_threshold
        self.validation_increment = validation_increment
        self.contradiction_penalty = contradiction_penalty
        self.max_trace = max_trace
        self.reactivation_increment = reactivation_increment

    def _load_embedder(self):
        if self._embedder is not None:
            return self._embedder
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "Installeer sentence-transformers om SSLManager te gebruiken: "
                "pip install sentence-transformers"
            ) from exc
        self._embedder = SentenceTransformer(self.model_name)
        return self._embedder

    def get_embedding(self, text: str) -> np.ndarray:
        if self._embedding_fn is not None:
            return self._normalize_embedding(self._embedding_fn(text))
        embedder = self._load_embedder()
        return embedder.encode(text, normalize_embeddings=True)

    @staticmethod
    def _normalize_embedding(embedding: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm

    @staticmethod
    def is_atomic_seed(text: str) -> bool:
        """Heuristische check. Menselijke beoordeling blijft nodig."""
        lowered = text.lower()
        separators = [",", ";", " en ", " of ", "zoals", "bijvoorbeeld"]
        broad_terms = [
            "analysekader",
            "volledig",
            "oorzaken",
            "gevolgen",
            "contexten",
            "perspectieven",
            "meerdere",
        ]
        has_many_separators = sum(sep in lowered for sep in separators) >= 2
        has_broad_terms = any(term in lowered for term in broad_terms)
        word_count = len(re.findall(r"\w+", text))
        return not has_many_separators and not has_broad_terms and word_count <= 18

    def add_or_update_seed(
        self,
        text: str,
        trigger_keywords: Iterable[str] | None = None,
    ) -> str:
        if not self.is_atomic_seed(text):
            raise ValueError("Seed lijkt te breed. Splits eerst naar atomische seeds.")

        new_emb = self.get_embedding(text)

        for seed_id, seed in self.seeds.items():
            sim = float(np.dot(new_emb, seed.embedding))
            if sim >= self.dedup_threshold:
                seed.occurrence_count += 1
                seed.trace = min(seed.trace + 0.5, self.max_trace)
                if seed.status != SeedStatus.PROMOTED:
                    seed.status = SeedStatus.ACTIVE
                seed.updated_at = datetime.now().isoformat()
                return seed_id

        seed_id = f"ss_{len(self.seeds) + 1:03d}"
        self.seeds[seed_id] = ShadowSeed(
            id=seed_id,
            text=text,
            embedding=new_emb,
            trigger_keywords=list(trigger_keywords or []),
        )
        return seed_id

    def decay_traces(self, turns_passed: int = 1) -> None:
        for seed in self.seeds.values():
            if seed.status == SeedStatus.EXPIRED:
                continue

            seed.trace *= math.exp(-turns_passed / self.half_life_turns)
            seed.updated_at = datetime.now().isoformat()

            if seed.trace < self.dormant_threshold and seed.weight == 0.0:
                seed.status = SeedStatus.DORMANT
            elif seed.trace < 0.5 and seed.status not in {
                SeedStatus.PROMOTED,
                SeedStatus.DORMANT,
            }:
                seed.status = SeedStatus.DECAYING

    def run_validation_gate(
        self,
        seed_id: str,
        external_evidence: bool = False,
        contradiction: bool = False,
    ) -> bool | None:
        seed = self.seeds[seed_id]

        if external_evidence:
            seed.evidence_count += 1

        check1 = seed.occurrence_count >= 3 and seed.trace > 0.5
        check2 = seed.evidence_count >= 2
        check3 = not contradiction

        if contradiction:
            seed.weight = max(0.0, seed.weight - self.contradiction_penalty)
            seed.occurrence_count = 1
            seed.status = SeedStatus.NEW
            seed.updated_at = datetime.now().isoformat()
            return False

        if check1 and check2 and check3:
            seed.weight = min(1.0, seed.weight + self.validation_increment)
            seed.status = (
                SeedStatus.PROMOTED
                if seed.weight >= self.promotion_threshold
                else SeedStatus.ACTIVE
            )
            seed.updated_at = datetime.now().isoformat()
            return True

        return None

    def reactivate_by_text(self, text: str, threshold: float = 0.65) -> list[str]:
        query_emb = self.get_embedding(text)
        reactivated: list[str] = []

        for seed_id, seed in self.seeds.items():
            if seed.status != SeedStatus.DORMANT:
                continue

            sim = float(np.dot(query_emb, seed.embedding))
            keyword_hit = any(
                keyword.lower() in text.lower() for keyword in seed.trigger_keywords
            )

            if sim >= threshold or keyword_hit:
                seed.trace = min(seed.trace + self.reactivation_increment, self.max_trace)
                seed.status = SeedStatus.NEW
                seed.updated_at = datetime.now().isoformat()
                reactivated.append(seed_id)

        return reactivated

    def find_constellations(
        self, threshold: float = 0.70, min_members: int = 3
    ) -> list[Constellation]:
        promoted = [
            seed for seed in self.seeds.values() if seed.status == SeedStatus.PROMOTED
        ]
        constellations: list[Constellation] = []
        seen: set[tuple[str, ...]] = set()

        for index, seed in enumerate(promoted):
            cluster = [seed]
            for other in promoted[index + 1 :]:
                sim = float(np.dot(seed.embedding, other.embedding))
                if sim >= threshold:
                    cluster.append(other)

            if len(cluster) >= min_members:
                member_ids = tuple(sorted(item.id for item in cluster))
                if member_ids in seen:
                    continue
                seen.add(member_ids)
                centroid = np.mean([item.embedding for item in cluster], axis=0)
                constellations.append(
                    Constellation(
                        members=list(member_ids),
                        centroid=centroid.tolist(),
                        combined_weight=float(
                            np.mean([item.weight for item in cluster])
                        ),
                    )
                )

        return constellations

    def get_seed(self, seed_id: str) -> ShadowSeed:
        return self.seeds[seed_id]

    def to_dict(self) -> dict:
        return {
            "seeds": [seed.to_dict() for seed in self.seeds.values()],
            "constellations": [item.to_dict() for item in self.find_constellations()],
        }
