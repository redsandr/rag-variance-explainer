import pytest

from src.chunking import chunk_document, count_tokens
from src.prompts import build_judge_prompt, build_judge_prompt_compact
from src.query_expansion import expand_query
from src.rag import build_context
from src.retrieval import _forward_looking_penalty, _keyword_boost


def test_chunk_respects_token_size_not_character_size() -> None:
    text = "COGS SG&A EBITDA YoY QoQ " * 300
    chunks = chunk_document(text, chunk_size=500, chunk_overlap=0)

    for chunk in chunks:
        token_count = count_tokens(chunk)
        assert token_count <= 500, (
            f"Chunk has {token_count} tokens, expected <= 500"
        )


def test_chunk_overlap_produces_shared_content() -> None:
    text = "word " * 1000
    chunks = chunk_document(text, chunk_size=200, chunk_overlap=50)

    assert len(chunks) > 1

    tail_of_first = " ".join(chunks[0].split()[-10:])
    assert tail_of_first.split()[0] in chunks[1]


def test_empty_text_returns_no_chunks() -> None:
    assert chunk_document("") == []


def test_overlap_must_be_smaller_than_chunk_size() -> None:
    with pytest.raises(ValueError):
        chunk_document("some text", chunk_size=100, chunk_overlap=100)


def test_single_short_chunk_no_splitting_needed() -> None:
    text = "Revenue increased due to higher same-store sales."
    chunks = chunk_document(text, chunk_size=500, chunk_overlap=50)
    assert len(chunks) == 1
    assert chunks[0].strip() == text.strip()


def test_build_context_includes_relevance() -> None:
    results = [
        {
            "text": "Marketing expense decreased due to lower ad spend.",
            "metadata": {
                "ticker": "DRI",
                "form": "10-Q",
                "filing_date": "2026-03-27",
            },
            "relevance": 0.87,
        }
    ]
    context = build_context(results)
    assert "[DRI 10-Q filed 2026-03-27 | relevance: 0.87]" in context
    assert "Marketing expense decreased" in context


def test_build_context_empty_returns_fallback() -> None:
    assert build_context([]) == "No relevant filing excerpts were found."


def test_expand_query_adds_synonyms() -> None:
    expanded = expand_query("labor cost", n_extra_terms=3)
    assert "labor" in expanded or "labour" in expanded
    assert "cost" in expanded or "costs" in expanded


def test_expand_query_unknown_terms_unchanged() -> None:
    assert expand_query("quantum entanglement", n_extra_terms=5).rstrip() == "quantum entanglement"


def test_keyword_boost_finds_matches() -> None:
    boost = _keyword_boost("Why did labor costs increase", "Labor costs increased due to wage inflation")
    assert boost > 0


def test_keyword_boost_no_common_words() -> None:
    boost = _keyword_boost("quantum computing", "Revenue increased 10%")
    assert boost == 0.0


def test_forward_looking_penalty_single_match() -> None:
    penalty = _forward_looking_penalty("forward-looking statements could be adversely affected")
    assert penalty != 0


def test_forward_looking_penalty_double_match() -> None:
    penalty = _forward_looking_penalty("risk factors and forward-looking statements described above")
    from src.config import config
    assert penalty == config.forward_looking_penalty_weight * 2


def test_forward_looking_penalty_no_match() -> None:
    penalty = _forward_looking_penalty("Last quarter revenue was $100M")
    assert penalty == 0.0


def test_build_judge_prompt_includes_all_sections() -> None:
    sources = [
        {"metadata": {"ticker": "CMG", "form": "10-Q", "filing_date": "2026-03-31"}, "text": "Labor costs decreased."}
    ]
    prompt = build_judge_prompt("Why did labor costs change?", "Labor costs decreased due to efficiency.", sources)
    assert "Why did labor costs change?" in prompt
    assert "Labor costs decreased due to efficiency." in prompt
    assert "[CMG 10-Q filed 2026-03-31]" in prompt


def test_build_judge_prompt_compact_truncates_long_sources() -> None:
    long_text = "word " * 500
    sources = [
        {"metadata": {"ticker": "DRI", "form": "10-Q", "filing_date": "2026-01-01"}, "text": long_text}
    ]
    prompt = build_judge_prompt_compact("Test?", "Answer.", sources)
    assert len(prompt) < len(long_text) + 200


def test_build_judge_prompt_no_sources() -> None:
    prompt = build_judge_prompt("Question?", "Answer.", [])
    assert "(no sources)" in prompt


def test_build_judge_prompt_compact_no_sources() -> None:
    prompt = build_judge_prompt_compact("Question?", "Answer.", [])
    assert "(no sources)" in prompt


def test_parse_judge_response_valid_json() -> None:
    from src.eval_faithfulness import parse_judge_response
    raw = '{"claims": [{"claim": "Revenue grew 5%", "verdict": "FAITHFUL"}], "faithful_count": 1}'
    parsed = parse_judge_response(raw)
    assert parsed is not None
    assert parsed["faithful_count"] == 1


def test_parse_judge_response_code_fenced() -> None:
    from src.eval_faithfulness import parse_judge_response
    raw = '```json\n{"claims": [], "faithful_count": 0}\n```'
    parsed = parse_judge_response(raw)
    assert parsed is not None
    assert parsed["faithful_count"] == 0


def test_parse_judge_response_garbage_returns_none() -> None:
    from src.eval_faithfulness import parse_judge_response
    assert parse_judge_response("not json at all") is None


def test_has_answer_content_returns_true() -> None:
    from src.eval_faithfulness import _has_answer_content
    assert _has_answer_content("Revenue increased due to higher pricing")


def test_has_answer_content_no_info_returns_false() -> None:
    from src.eval_faithfulness import _has_answer_content
    assert not _has_answer_content("the provided filings do not discuss this topic")


def test_rrf_merge_interleaves_dense_and_bm25() -> None:
    from src.hybrid_search import rrf_merge
    dense = [{"text": f"dense_{i}"} for i in range(3)]
    bm25 = [{"text": f"bm25_{i}"} for i in range(3)]
    merged = rrf_merge(dense, bm25, top_k=4)
    assert len(merged) == 4
    assert all("hybrid_score" in m for m in merged)


def test_rrf_merge_empty_lists() -> None:
    from src.hybrid_search import rrf_merge
    assert rrf_merge([], []) == []


def test_config_defaults() -> None:
    from src.config import RAGConfig
    cfg = RAGConfig()
    assert cfg.retrieval_top_k == 5
    assert cfg.cross_encoder_enabled is True
    assert cfg.hybrid_search_enabled is True
    assert cfg.llm_temperature == 0.1


def test_filing_document_url_format() -> None:
    from src.ingest import filing_document_url
    url = filing_document_url("0000010290", "0000010290-26-000001", "test.htm")
    assert "000001029026000001" in url  # dashes removed
    assert url.startswith("https://www.sec.gov/")


def test_parse_judge_response_trailing_comma_returns_none() -> None:
    from src.eval_faithfulness import parse_judge_response
    raw = '{"claims": [{"claim": "test", "verdict": "FAITHFUL"}], "faithful_count": 1,}'
    assert parse_judge_response(raw) is None


def test_parse_judge_response_empty_claims() -> None:
    from src.eval_faithfulness import parse_judge_response
    assert parse_judge_response("{}") is not None


def test_forward_looking_penalty_edge_zero_match() -> None:
    from src.retrieval import _forward_looking_penalty
    assert _forward_looking_penalty("") == 0.0


def test_expand_query_unknown_terms_adds_no_synonyms() -> None:
    from src.query_expansion import expand_query
    result = expand_query("quantum", n_extra_terms=20)
    assert result.rstrip() == "quantum"


def test_sanitize_input_strips_control_chars() -> None:
    from src.rag import sanitize_input
    assert sanitize_input("hello\x00world") == "helloworld"
    assert sanitize_input("normal text") == "normal text"


def test_sanitize_input_truncates_long() -> None:
    from src.rag import sanitize_input, MAX_QUESTION_LENGTH
    long = "x" * (MAX_QUESTION_LENGTH + 100)
    assert len(sanitize_input(long)) == MAX_QUESTION_LENGTH


def test_keyword_boost_stopwords_ignored() -> None:
    from src.retrieval import _keyword_boost
    assert _keyword_boost("the a an in of to", "any text here") == 0.0


# --- LLM backend tests ---


def test_llm_unknown_backend_fallback_raises_runtime_error() -> None:
    from src.llm import LLMClient
    LLMClient.reset()
    with pytest.raises(RuntimeError, match="All LLM backends failed"):
        LLMClient(backend="nonexistent_backend")
    LLMClient.reset()


def test_llm_singleton_returns_same_instance() -> None:
    from src.llm import LLMClient
    LLMClient.reset()
    a = LLMClient.__new__(LLMClient)
    b = LLMClient.__new__(LLMClient)
    assert a is b
    LLMClient.reset()


def test_llm_reset_creates_new_instance() -> None:
    from src.llm import LLMClient
    LLMClient.reset()
    a = LLMClient.__new__(LLMClient)
    LLMClient.reset()
    b = LLMClient.__new__(LLMClient)
    assert a is not b


# --- Cross-encoder rerank tests ---


def test_rerank_empty_candidates_returns_empty() -> None:
    from src.cross_encoder import rerank
    assert rerank("test query", [], top_k=5) == []


def test_rerank_single_candidate_preserves_it() -> None:
    from unittest.mock import patch
    from src.cross_encoder import rerank

    candidate = {"text": "Revenue increased 10%", "metadata": {"ticker": "CMG"}, "relevance": 0.9}
    with patch("src.cross_encoder._get_model") as mock_get_model:
        mock_model = mock_get_model.return_value
        mock_model.predict.return_value = [0.95]
        result = rerank("revenue", [candidate], top_k=5)
    assert len(result) == 1
    assert result[0]["text"] == "Revenue increased 10%"
    assert "cross_encoder_score" in result[0]


# --- LLM error handling tests ---


def test_retry_decorator_succeeds_after_retry() -> None:
    from src.llm import _retry

    call_count = 0

    @_retry(max_attempts=3, base_delay=0.01)
    def flaky_fn():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("transient error")
        return "success"

    assert flaky_fn() == "success"
    assert call_count == 3


def test_retry_decorator_exhausts_attempts() -> None:
    from src.llm import _retry

    call_count = 0

    @_retry(max_attempts=3, base_delay=0.01)
    def always_fails():
        nonlocal call_count
        call_count += 1
        raise ValueError("permanent error")

    with pytest.raises(ValueError, match="permanent error"):
        always_fails()
    assert call_count == 3


# --- MCP server tests ---


def test_mcp_server_has_four_tools() -> None:
    from src.server import mcp

    tools = mcp._tool_manager.list_tools()
    names = [t.name for t in tools]
    assert len(names) == 4
    assert "rag.answer" in names
    assert "rag.search" in names
    assert "rag.list_companies" in names
    assert "rag.list_questions" in names


def test_mcp_list_companies_returns_all_tickers() -> None:
    from src.server import list_companies

    result = list_companies()
    assert "CMG" in result
    assert "XOM" in result
    assert "7 companies" in result
    assert "Restaurant" in result
    assert "Energy" in result


# --- build_index tests ---


def test_build_index_empty_db_handles_gracefully() -> None:
    from unittest.mock import patch
    import src.build_index as bi

    with (
        patch("src.build_index.get_client") as mock_client,
        patch("src.build_index.get_collection") as mock_collection,
        patch("src.build_index.TICKERS", {}),
    ):
        mock_collection.return_value.count.return_value = 0
        bi.build_index()


# --- API behavior tests ---

def test_api_root_returns_service_info() -> None:
    from src.api import app

    client = app.__class__
    assert app.title == "RAG Variance Explainer API"
    assert app.version == "1.0.0"


def test_api_companies_endpoint() -> None:
    from src.api import app

    for route in app.routes:
        if hasattr(route, "path") and route.path == "/companies" and "GET" in route.methods:
            assert route.path == "/companies"
            return
    raise AssertionError("GET /companies route not found")


def test_api_health_endpoint() -> None:
    from src.api import app

    for route in app.routes:
        if hasattr(route, "path") and route.path == "/health":
            assert "GET" in route.methods
            return
    raise AssertionError("GET /health route not found")


def test_api_search_returns_results() -> None:
    from unittest.mock import patch, MagicMock
    from src.api import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    mock_result = {
        "text": "Marketing expense decreased due to lower ad spend.",
        "metadata": {"ticker": "DRI", "form": "10-Q", "filing_date": "2026-03-27"},
        "hybrid_score": 0.87,
    }
    with (
        patch("src.api.get_client"),
        patch("src.api.get_collection"),
        patch("src.api.query_multi", return_value=[mock_result]),
    ):
        resp = client.post("/search", json={"query": "marketing costs", "top_k": 3})

    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "marketing costs"
    assert len(data["results"]) == 1
    assert data["results"][0]["ticker"] == "DRI"
    assert "elapsed_seconds" in data


def test_api_search_validates_ticker() -> None:
    from unittest.mock import patch
    from src.api import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    with (
        patch("src.api.get_client"),
        patch("src.api.get_collection"),
        patch("src.api.query_multi"),
    ):
        resp = client.post("/search", json={"query": "test", "ticker": "INVALID"})

    assert resp.status_code == 404
    assert "Unknown ticker" in resp.json()["detail"]


def test_api_answer_returns_answer() -> None:
    from unittest.mock import patch, MagicMock
    from src.api import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    mock_result = {
        "question": "Why did marketing costs change?",
        "answer": "Marketing costs decreased due to lower ad spend.",
        "sources": [
            {
                "text": "Marketing expense decreased.",
                "metadata": {"ticker": "DRI", "form": "10-Q", "filing_date": "2026-03-27"},
                "hybrid_score": 0.87,
            }
        ],
        "verification_errors": [],
    }
    with patch("src.api.answer_question", return_value=mock_result):
        resp = client.post("/answer", json={"question": "Why did marketing costs change?"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["question"] == "Why did marketing costs change?"
    assert data["answer"] == mock_result["answer"]
    assert data["source_count"] == 1
    assert "elapsed_seconds" in data


def test_api_answer_rejects_empty_question() -> None:
    from src.api import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    resp = client.post("/answer", json={"question": ""})
    assert resp.status_code == 422


def test_api_answer_handles_llm_failure() -> None:
    from unittest.mock import patch
    from src.api import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    with patch("src.api.answer_question", side_effect=RuntimeError("LLM unavailable")):
        resp = client.post("/answer", json={"question": "Why did costs change?"})

    assert resp.status_code == 500
    assert "LLM unavailable" in resp.json()["detail"]


def test_api_search_empty_query_rejected() -> None:
    from src.api import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    resp = client.post("/search", json={"query": ""})
    assert resp.status_code == 422


def test_api_companies_get_returns_list() -> None:
    from unittest.mock import patch
    from src.api import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    resp = client.get("/companies")
    assert resp.status_code == 200
    data = resp.json()
    assert "companies" in data
    assert len(data["companies"]) == 7
    assert data["companies"][0]["ticker"] == "CBRL"
    assert "sector" in data["companies"][0]


def test_api_health_returns_ok() -> None:
    from src.api import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
