import numpy as np
import pytest

from shadowseed.benchmark.vectorstore_smoke import run_vectorstore_smoke


@pytest.mark.parametrize("backend", ["faiss", "chroma"])
def test_optional_vector_backend_smoke_if_installed(tmp_path, backend):
    try:
        output = run_vectorstore_smoke(str(tmp_path / f"{backend}.json"), backend=backend)
    except RuntimeError as exc:
        pytest.skip(str(exc))

    assert output.exists()
    assert backend in output.read_text(encoding="utf-8")


def test_chroma_persistent_store_hydrates_existing_metadata_if_installed(tmp_path):
    try:
        from shadowseed.vectorstore.chroma_store import ChromaVectorStore
    except RuntimeError as exc:
        pytest.skip(str(exc))

    first = ChromaVectorStore(
        collection_name="shadowseed_test",
        persist_directory=str(tmp_path / "chroma"),
    )
    first.add(
        "seed-1",
        np.array([1.0, 0.0], dtype=float),
        {"text": "Koloniale katoen als grondstof.", "weight": 0.2},
    )

    reopened = ChromaVectorStore(
        collection_name="shadowseed_test",
        persist_directory=str(tmp_path / "chroma"),
    )

    assert reopened.get_all_ids() == ["seed-1"]
    assert reopened.get_metadata("seed-1")["text"] == "Koloniale katoen als grondstof."
    assert reopened.search(np.array([1.0, 0.0], dtype=float), top_k=1)[0][0] == "seed-1"
