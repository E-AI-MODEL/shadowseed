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
