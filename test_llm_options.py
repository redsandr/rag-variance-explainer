from unittest.mock import MagicMock, patch

from src import retrieval
from src.llm import LLMClient, _retry

INIT_LOCAL = LLMClient._init_llama_cpp
INIT_SERVER = LLMClient._init_llama_server


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


def test_llama_server_uses_loopback_and_discovers_loaded_model(monkeypatch) -> None:
    monkeypatch.delenv("LLAMA_SERVER_MODEL", raising=False)
    with patch("openai.OpenAI") as client_factory:
        client_factory.return_value.models.list.return_value.data = [MagicMock(id="/models/qwen2.5-7b-instruct-q4_k_m.gguf")]
        client = object.__new__(LLMClient)
        INIT_SERVER(client)

    assert str(client_factory.call_args.kwargs["base_url"]) == "http://127.0.0.1:8080/v1"
    assert client_factory.call_args.kwargs["timeout"] == 300
    assert client_factory.call_args.kwargs["max_retries"] == 0
    client_factory.return_value.models.list.assert_called_once_with()
    assert client._model == "/models/qwen2.5-7b-instruct-q4_k_m.gguf"


def test_llama_server_rejects_empty_model_list(monkeypatch) -> None:
    monkeypatch.delenv("LLAMA_SERVER_MODEL", raising=False)
    with patch("openai.OpenAI") as client_factory:
        client_factory.return_value.models.list.return_value.data = []
        client = object.__new__(LLMClient)
        try:
            INIT_SERVER(client)
        except RuntimeError as exc:
            assert "no loaded model" in str(exc)
        else:
            raise AssertionError("Empty server must fail closed")


def test_llama_server_failure_never_loads_native_model() -> None:
    LLMClient.reset()
    with (
        patch("src.llm.LLMClient._init_llama_server", side_effect=RuntimeError("server unavailable")),
        patch("src.llm.LLMClient._init_llama_cpp") as native,
    ):
        try:
            LLMClient(backend="llama_server")
        except RuntimeError as exc:
            assert "server unavailable" in str(exc)
        else:
            raise AssertionError("Unavailable server must fail closed")
        native.assert_not_called()
    LLMClient.reset()


def test_llama_server_passes_structured_response_format() -> None:
    client = object.__new__(LLMClient)
    client._client = MagicMock()
    client._model = "rve-local"
    client._client.chat.completions.create.return_value.choices[0].message.content = '{"can_answer":false}'
    schema = {"type": "json_object", "schema": {"type": "object"}}

    assert client._generate_openai("Question", "System", 32, 0.1, schema) == '{"can_answer":false}'
    assert client._client.chat.completions.create.call_args.kwargs["response_format"] == schema


def test_bad_request_does_not_retry() -> None:
    calls = []

    class InvalidContextError(Exception):
        status_code = 400

    @_retry(max_attempts=3, base_delay=0.01)
    def generate():
        calls.append(1)
        raise InvalidContextError("Requested tokens exceed context window")

    try:
        generate()
    except InvalidContextError:
        pass
    else:
        raise AssertionError("Invalid request should fail immediately")
    assert calls == [1]


def test_native_context_overflow_does_not_retry() -> None:
    calls = []

    @_retry(max_attempts=3, base_delay=0.01)
    def generate():
        calls.append(1)
        raise ValueError("Requested tokens (4400) exceed context window of 4096")

    try:
        generate()
    except ValueError:
        pass
    else:
        raise AssertionError("Context overflow should fail immediately")
    assert calls == [1]
