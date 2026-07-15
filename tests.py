import pytest
from src.chunking import chunk_document, count_tokens
from src.rag import build_context


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
