from shadowseed.manager import SSLManager
from shadowseed.seed_normalization import normalize_detection_candidates, split_broad_seed_text


def test_split_broad_seed_text_breaks_list_like_detection():
    parts = split_broad_seed_text("Security, privacy en schaalbaarheid ontbreken.")

    assert len(parts) == 3
    assert all(part.endswith("ontbreekt.") for part in parts)


def test_normalize_detection_candidates_expands_broad_candidate():
    normalized = normalize_detection_candidates([
        "Voeg een analysekader toe met aandacht voor security, privacy en schaalbaarheid"
    ])

    assert len(normalized) >= 3


def test_normalize_keeps_single_relational_seed_with_and_intact():
    normalized = normalize_detection_candidates([
        "Encryptie van medische data in rust en tijdens transport."
    ])

    assert normalized == ["Encryptie van medische data in rust en tijdens transport."]


def test_manager_ingest_detection_candidates_keeps_accept_reject_split():
    manager = SSLManager(embedding_fn=lambda _text: __import__("numpy").array([1.0, 0.0, 0.0]))
    result = manager.ingest_detection_candidates([
        "Koloniaal kapitaal als financieringsbron voor Britse fabrieksinvesteringen.",
        "Security, privacy en schaalbaarheid ontbreken.",
    ])

    assert len(result["accepted"]) == 1
    assert result["accepted"][0]["seed_id"] == "ss_001"
    assert len(result["rejected"]) == 3
