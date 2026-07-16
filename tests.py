import pytest
from src.chunking import chunk_document, count_tokens
from src.rag import build_context
from src.query_expansion import expand_query
from src.retrieval import _keyword_boost, _forward_looking_penalty
from src.prompts import build_judge_prompt, build_judge_prompt_compact


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


def test_is_retrieval_gap_has_content_returns_true() -> None:
    from src.eval_faithfulness import _is_retrieval_gap
    assert _is_retrieval_gap("Revenue increased due to higher pricing")


def test_is_retrieval_gap_no_info_returns_false() -> None:
    from src.eval_faithfulness import _is_retrieval_gap
    assert not _is_retrieval_gap("the provided filings do not discuss this topic")
