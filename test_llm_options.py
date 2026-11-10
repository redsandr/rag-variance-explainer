from unittest.mock import MagicMock, patch

from src import retrieval
from src.llm import LLMClient

INIT_LOCAL = LLMClient._init_llama_cpp


def test_local_llm_uses_cpu_safe_memory_defaults(monkeypatch, tmp_path) -> None:
    model = tmp_path / "model.gguf"
    model.write_bytes(b"GGUF")
    monkeypatch.setenv("LLAMA_CPP_MODEL_PATH", str(model))
    monkeypatch.delenv("LLAMA_CPP_N_GPU_LAYERS", raising=False)
    monkeypatch.delenv("LLAMA_CPP_N_BATCH", raising=False)
    monkeypatch.delenv("LLAMA_CPP_N_CTX", raising=False)

    with patch("llama_cpp.Llama") as loader:
        INIT_LOCAL(object.__new__(LLMClient))
        assert loader.call_args.kwargs["n_gpu_layers"] == 0
        assert loader.call_args.kwargs["n_batch"] == 32
        assert loader.call_args.kwargs["n_ctx"] == 8192


def test_cross_encoder_override_does_not_mutate_shared_config() -> None:
    candidates = [{"text": "Revenue changed.", "metadata": {"ticker": "CMG"}, "relevance": 0.8}]
    with (
        patch.object(retrieval.config, "cross_encoder_enabled", True),
        patch.object(retrieval.config, "hybrid_search_enabled", False),
        patch.object(retrieval.config, "expansion_enabled", False),
        patch.object(retrieval, "_retrieve_dense", return_value=candidates),
        patch.object(retrieval, "rerank", return_value=candidates) as rerank,
    ):
        retrieval.query_multi(MagicMock(), "revenue", cross_encoder_enabled=False)
        rerank.assert_not_called()
        assert retrieval.config.cross_encoder_enabled is True

        retrieval.query_multi(MagicMock(), "revenue", cross_encoder_enabled=True)
        rerank.assert_called_once()
        assert retrieval.config.cross_encoder_enabled is True
