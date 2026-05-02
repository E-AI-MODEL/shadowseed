import numpy as np

from shadowseed.manager import SSLManager, SeedStatus


def fake_embedding(text: str) -> np.ndarray:
    if "Koloniaal kapitaal" in text:
        return np.array([1.0, 0.0, 0.0])
    if "Koloniale katoen" in text:
        return np.array([0.95, 0.05, 0.0])
    return np.array([0.0, 1.0, 0.0])


def test_add_update_and_validation_gate_smoke():
    manager = SSLManager(embedding_fn=fake_embedding, promotion_threshold=0.4)

    seed_id = manager.add_or_update_seed(
        "Koloniaal kapitaal als financieringsbron voor Britse fabrieksinvesteringen.",
        trigger_keywords=["kapitaal", "fabrieksinvesteringen"],
    )
    assert seed_id == "ss_001"
    assert manager.seeds[seed_id].weight == 0.0

    duplicate_seed_id = manager.add_or_update_seed(
        "Koloniaal kapitaal als financieringsbron voor Britse fabrieksinvesteringen."
    )
    assert duplicate_seed_id == seed_id

    manager.seeds[seed_id].occurrence_count = 3
    manager.run_validation_gate(seed_id, external_evidence=True)
    result = manager.run_validation_gate(seed_id, external_evidence=True)

    assert result is True
    assert manager.seeds[seed_id].status == SeedStatus.PROMOTED
    assert manager.seeds[seed_id].weight >= 0.4


def test_reactivate_dormant_seed_by_keyword():
    manager = SSLManager(embedding_fn=fake_embedding)
    seed_id = manager.add_or_update_seed(
        "Koloniale katoen als grondstof voor de Britse textielindustrie.",
        trigger_keywords=["katoen", "textiel"],
    )
    manager.seeds[seed_id].status = SeedStatus.DORMANT
    manager.seeds[seed_id].trace = 0.01

    reactivated = manager.reactivate_by_text("De katoenhandel voedde de textielindustrie.")
    assert reactivated == [seed_id]
    assert manager.seeds[seed_id].status == SeedStatus.NEW
