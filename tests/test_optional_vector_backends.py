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


def _chroma_store_or_skip(collection_name: str, persist_directory: str):
    from shadowseed.vectorstore.chroma_store import ChromaVectorStore

    try:
        return ChromaVectorStore(
            collection_name=collection_name,
            persist_directory=persist_directory,
        )
    except RuntimeError as exc:
        pytest.skip(str(exc))


def test_chroma_persistent_store_hydrates_existing_metadata_if_installed(tmp_path):
    persist_directory = str(tmp_path / "chroma")
    first = _chroma_store_or_skip("shadowseed_test", persist_directory)
    first.add(
        "seed-1",
        np.array([1.0, 0.0], dtype=float),
        {"text": "Koloniale katoen als grondstof.", "weight": 0.2},
    )

    reopened = _chroma_store_or_skip("shadowseed_test", persist_directory)

    assert reopened.get_all_ids() == ["seed-1"]
    assert reopened.get_metadata("seed-1")["text"] == "Koloniale katoen als grondstof."
    assert reopened.search(np.array([1.0, 0.0], dtype=float), top_k=1)[0][0] == "seed-1"
