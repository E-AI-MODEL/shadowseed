"""
Shadow Seed Learning 4.5 core manager.

This manager is the canonical Niveau-1 core for SSL 4.5. It keeps four ideas
explicit:

- a seed is atomic;
- trace measures presence;
- weight measures influence;
- promotion requires the Validation Gate.

The manager now also keeps explicit configuration, normalization results and
validation-event logs so benchmark runs can be reconstructed more honestly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Iterable
import math
import re

import numpy as np

from shadowseed.core_config import SSLCoreConfig
from shadowseed.seed_normalization import normalize_detection_candidates

if TYPE_CHECKING:
    from shadowseed.vector_constellation import VectorConstellation


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

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["embedding"] = self.embedding.tolist()
        data["status"] = self.status.value
        return data


@dataclass
class Constellation:
    members: list[str]
    centroid: list[float]
    combined_weight: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SeedEvent:
    event_type: str
    seed_id: str
    detail: dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationGateResult:
    seed_id: str
    status_before: str
    status_after: str
    weight_before: float
    weight_after: float
    occurrence_count: int
    evidence_count: int
    internal_recognition_passed: bool
    external_evidence_passed: bool
    contradiction_free: bool
    external_evidence_applied: bool
    contradiction_applied: bool
    promoted: bool
    verdict: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SSLManager:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        half_life_turns: float | None = None,
        dedup_threshold: float | None = None,
        promotion_threshold: float | None = None,
        dormant_threshold: float | None = None,
        validation_increment: float | None = None,
        contradiction_penalty: float | None = None,
        max_trace: float | None = None,
        reactivation_increment: float | None = None,
        embedding_fn: Callable[[str], np.ndarray] | None = None,
        vector_constellation: VectorConstellation | None = None,
        config: SSLCoreConfig | None = None,
    ):
        self._embedding_fn = embedding_fn
        self.model_name = model_name
        self._embedder = None
        self.seeds: dict[str, ShadowSeed] = {}
        self.config = SSLCoreConfig(
            half_life_turns=config.half_life_turns if config and half_life_turns is None else (half_life_turns if half_life_turns is not None else SSLCoreConfig().half_life_turns),
            dedup_threshold=config.dedup_threshold if config and dedup_threshold is None else (dedup_threshold if dedup_threshold is not None else SSLCoreConfig().dedup_threshold),
            promotion_threshold=config.promotion_threshold if config and promotion_threshold is None else (promotion_threshold if promotion_threshold is not None else SSLCoreConfig().promotion_threshold),
            dormant_threshold=config.dormant_threshold if config and dormant_threshold is None else (dormant_threshold if dormant_threshold is not None else SSLCoreConfig().dormant_threshold),
            validation_increment=config.validation_increment if config and validation_increment is None else (validation_increment if validation_increment is not None else SSLCoreConfig().validation_increment),
            contradiction_penalty=config.contradiction_penalty if config and contradiction_penalty is None else (contradiction_penalty if contradiction_penalty is not None else SSLCoreConfig().contradiction_penalty),
            max_trace=config.max_trace if config and max_trace is None else (max_trace if max_trace is not None else SSLCoreConfig().max_trace),
            reactivation_increment=config.reactivation_increment if config and reactivation_increment is None else (reactivation_increment if reactivation_increment is not None else SSLCoreConfig().reactivation_increment),
            min_occurrences_for_gate=config.min_occurrences_for_gate if config else SSLCoreConfig().min_occurrences_for_gate,
            min_evidence_for_gate=config.min_evidence_for_gate if config else SSLCoreConfig().min_evidence_for_gate,
            min_trace_for_gate=config.min_trace_for_gate if config else SSLCoreConfig().min_trace_for_gate,
            max_seed_words=config.max_seed_words if config else SSLCoreConfig().max_seed_words,
        )
        self.half_life_turns = self.config.half_life_turns
        self.dedup_threshold = self.config.dedup_threshold
        self.promotion_threshold = self.config.promotion_threshold
        self.dormant_threshold = self.config.dormant_threshold
        self.validation_increment = self.config.validation_increment
        self.contradiction_penalty = self.config.contradiction_penalty
        self.max_trace = self.config.max_trace
        self.reactivation_increment = self.config.reactivation_increment
        self.vector_constellation = vector_constellation
        self.validation_log: list[ValidationGateResult] = []
        self.event_log: list[SeedEvent] = []

    def _record_event(self, event_type: str, seed_id: str, **detail: Any) -> None:
        self.event_log.append(SeedEvent(event_type=event_type, seed_id=seed_id, detail=detail))

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
        """Heuristic filter. Human review is still needed."""
        lowered = text.lower().strip()
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
        overly_generic_short_forms = {
            "security ontbreekt",
            "privacy ontbreekt",
            "schaalbaarheid ontbreekt",
            "kolonialisme ontbreekt",
            "context ontbreekt",
            "internationale context ontbreekt",
        }
        has_many_separators = sum(sep in lowered for sep in separators) >= 2
        has_broad_terms = any(term in lowered for term in broad_terms)
        word_count = len(re.findall(r"\w+", text))
        if lowered.rstrip(".") in overly_generic_short_forms:
            return False
        return not has_many_separators and not has_broad_terms and word_count <= SSLCoreConfig().max_seed_words

    def normalize_detection_candidates(self, candidates: Iterable[str]) -> list[str]:
        return normalize_detection_candidates(list(candidates))

    def _sync_vector_seed(self, seed_id: str) -> None:
        if self.vector_constellation is not None:
            self.vector_constellation.sync_seed(self.seeds[seed_id])

    def ingest_detection_candidates(
        self,
        candidates: Iterable[str],
        trigger_keywords: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        normalized = self.normalize_detection_candidates(list(candidates))
        accepted: list[dict[str, str]] = []
        rejected: list[dict[str, str]] = []
        for candidate in normalized:
            try:
                seed_id = self.add_or_update_seed(candidate, trigger_keywords=trigger_keywords)
                accepted.append({"seed_id": seed_id, "text": candidate})
            except ValueError:
                rejected.append({"text": candidate, "reason": "not_atomic"})
        return {
            "input_count": len(list(candidates)) if not isinstance(candidates, list) else len(candidates),
            "normalized_candidates": normalized,
            "accepted": accepted,
            "rejected": rejected,
        }

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
                self._record_event(
                    "deduplicated",
                    seed_id,
                    similarity=sim,
                    occurrence_count=seed.occurrence_count,
                    trace=seed.trace,
                )
                self._sync_vector_seed(seed_id)
                return seed_id

        seed_id = f"ss_{len(self.seeds) + 1:03d}"
        self.seeds[seed_id] = ShadowSeed(
            id=seed_id,
            text=text,
            embedding=new_emb,
            trigger_keywords=list(trigger_keywords or []),
            trace=self.config.trace_start,
        )
        self._record_event("created", seed_id, text=text)
        self._sync_vector_seed(seed_id)
        return seed_id

    def decay_traces(self, turns_passed: int = 1) -> None:
        for seed_id, seed in self.seeds.items():
            if seed.status == SeedStatus.EXPIRED:
                continue

            before_trace = seed.trace
            seed.trace *= math.exp(-turns_passed / self.half_life_turns)
            seed.updated_at = datetime.now().isoformat()

            if seed.trace < self.dormant_threshold and seed.weight == 0.0:
                seed.status = SeedStatus.DORMANT
            elif seed.trace < 0.5 and seed.status not in {
                SeedStatus.PROMOTED,
                SeedStatus.DORMANT,
            }:
                seed.status = SeedStatus.DECAYING
            self._record_event(
                "trace_decayed",
                seed_id,
                turns_passed=turns_passed,
                trace_before=before_trace,
                trace_after=seed.trace,
                status=seed.status.value,
            )
            self._sync_vector_seed(seed_id)

    def run_validation_gate_detailed(
        self,
        seed_id: str,
        external_evidence: bool = False,
        contradiction: bool = False,
    ) -> ValidationGateResult:
        seed = self.seeds[seed_id]
        status_before = seed.status.value
        weight_before = seed.weight

        if external_evidence:
            seed.evidence_count += 1

        internal_recognition_passed = (
            seed.occurrence_count >= self.config.min_occurrences_for_gate
            and seed.trace > self.config.min_trace_for_gate
        )
        external_evidence_passed = seed.evidence_count >= self.config.min_evidence_for_gate
        contradiction_free = not contradiction

        if contradiction:
            seed.weight = max(0.0, seed.weight - self.contradiction_penalty)
            seed.occurrence_count = 1
            seed.status = SeedStatus.NEW
            seed.updated_at = datetime.now().isoformat()
            result = ValidationGateResult(
                seed_id=seed_id,
                status_before=status_before,
                status_after=seed.status.value,
                weight_before=weight_before,
                weight_after=seed.weight,
                occurrence_count=seed.occurrence_count,
                evidence_count=seed.evidence_count,
                internal_recognition_passed=internal_recognition_passed,
                external_evidence_passed=external_evidence_passed,
                contradiction_free=False,
                external_evidence_applied=external_evidence,
                contradiction_applied=True,
                promoted=False,
                verdict="contradicted",
            )
            self.validation_log.append(result)
            self._record_event("contradicted", seed_id, weight_after=seed.weight)
            self._sync_vector_seed(seed_id)
            return result

        promoted = False
        verdict = "blocked"
        if internal_recognition_passed and external_evidence_passed and contradiction_free:
            seed.weight = min(1.0, seed.weight + self.validation_increment)
            seed.status = (
                SeedStatus.PROMOTED
                if seed.weight >= self.promotion_threshold
                else SeedStatus.ACTIVE
            )
            seed.updated_at = datetime.now().isoformat()
            promoted = seed.status == SeedStatus.PROMOTED
            verdict = "promoted" if promoted else "validated"
            self._record_event(
                "validated",
                seed_id,
                promoted=promoted,
                weight_after=seed.weight,
                evidence_count=seed.evidence_count,
            )
        else:
            self._record_event(
                "validation_blocked",
                seed_id,
                internal_recognition_passed=internal_recognition_passed,
                external_evidence_passed=external_evidence_passed,
                contradiction_free=contradiction_free,
            )

        result = ValidationGateResult(
            seed_id=seed_id,
            status_before=status_before,
            status_after=seed.status.value,
            weight_before=weight_before,
            weight_after=seed.weight,
            occurrence_count=seed.occurrence_count,
            evidence_count=seed.evidence_count,
            internal_recognition_passed=internal_recognition_passed,
            external_evidence_passed=external_evidence_passed,
            contradiction_free=contradiction_free,
            external_evidence_applied=external_evidence,
            contradiction_applied=False,
            promoted=promoted,
            verdict=verdict,
        )
        self.validation_log.append(result)
        self._sync_vector_seed(seed_id)
        return result

    def run_validation_gate(
        self,
        seed_id: str,
        external_evidence: bool = False,
        contradiction: bool = False,
    ) -> bool | None:
        result = self.run_validation_gate_detailed(
            seed_id,
            external_evidence=external_evidence,
            contradiction=contradiction,
        )
        if result.verdict == "contradicted":
            return False
        if result.verdict in {"validated", "promoted"}:
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
                self._record_event(
                    "reactivated",
                    seed_id,
                    similarity=sim,
                    keyword_hit=keyword_hit,
                    trace=seed.trace,
                )
                self._sync_vector_seed(seed_id)
                reactivated.append(seed_id)

        return reactivated

    def find_uncertain_region(
        self,
        text: str,
        threshold: float = 0.85,
        include_promoted: bool = False,
    ) -> list[dict[str, Any]]:
        """Find vector-near seeds for a new prompt or context."""
        if self.vector_constellation is None:
            return []
        query_emb = self.get_embedding(text)
        matches = self.vector_constellation.search_similar_seeds(query_emb, threshold=threshold)
        uncertain = []
        for seed_id, score, metadata in matches:
            seed = self.seeds.get(seed_id)
            if seed is None:
                continue
            if not include_promoted and seed.status == SeedStatus.PROMOTED:
                continue
            if seed.weight == 0.0:
                uncertain.append(
                    {
                        "seed_id": seed_id,
                        "similarity": score,
                        "text": seed.text,
                        "status": seed.status.value,
                        "weight": seed.weight,
                        "metadata": metadata,
                    }
                )
        return uncertain

    def apply_external_feedback(
        self,
        feedback_text: str,
        context: str,
        positive: bool = True,
        threshold: float = 0.75,
    ) -> list[dict[str, Any]]:
        if self.vector_constellation is None:
            return []
        feedback_emb = self.get_embedding(f"FEEDBACK: {feedback_text} OP: {context}")
        matches = self.vector_constellation.search_similar_seeds(feedback_emb, threshold=threshold)
        updates = []
        for seed_id, score, _metadata in matches:
            if seed_id not in self.seeds:
                continue
            if positive:
                result = self.run_validation_gate(seed_id, external_evidence=True)
            else:
                result = self.run_validation_gate(seed_id, contradiction=True)
            self.vector_constellation.record_feedback(
                seed_id=seed_id,
                feedback=feedback_text,
                is_correction=positive,
                similarity=score,
            )
            updates.append(
                {
                    "seed_id": seed_id,
                    "similarity": score,
                    "gate_result": result,
                    "seed": self.seeds[seed_id].to_dict(),
                }
            )
        return updates

    def expire_vector_only_open_seeds(self, max_age_days: int = 30) -> list[str]:
        if self.vector_constellation is None:
            return []
        expired = self.vector_constellation.housekeeping(max_age_days=max_age_days)
        for seed_id in expired:
            if seed_id in self.seeds:
                self.seeds[seed_id].status = SeedStatus.EXPIRED
                self.seeds[seed_id].updated_at = datetime.now().isoformat()
                self._record_event("expired", seed_id, max_age_days=max_age_days)
        return expired

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

    def to_dict(self) -> dict[str, Any]:
        return {
            "config": self.config.to_dict(),
            "seeds": [seed.to_dict() for seed in self.seeds.values()],
            "constellations": [item.to_dict() for item in self.find_constellations()],
            "validation_log": [item.to_dict() for item in self.validation_log],
            "event_log": [item.to_dict() for item in self.event_log],
            "vector_constellation": (
                self.vector_constellation.to_dict()
                if self.vector_constellation is not None
                else None
            ),
        }
