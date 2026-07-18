"""
ChromaDB interface for storing and retrieving MD&A chunks.

Uses the nomic-embed embeddings from embedding.py directly (not
ChromaDB's built-in embedding functions), so we keep full control over
the prefixing behavior (search_document/search_query) that nomic-embed
requires.
"""

import logging
from typing import Any

import chromadb

from config import config
from cross_encoder import rerank
from embedding import embed_documents, embed_query
from hybrid_search import _tokenize, bm25_scores, build_bm25, rrf_merge
from query_expansion import expand_query

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "mda_filings"


def get_client() -> Any:
    """Persistent local ChromaDB client — data survives between runs."""
    return chromadb.PersistentClient(path=config.db_path)


def get_collection(client: Any) -> Any:
    """
    Get or create the MD&A collection. Explicitly configured for cosine
    distance since our embeddings are normalized (embedding.py uses
    normalize_embeddings=True) — cosine similarity is the correct match
    for that, not the L2 default ChromaDB otherwise uses.
    """
    return client.get_or_create_collection(
        name=_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(
    collection: Any,
    chunks: list[str],
    ticker: str,
    accession_number: str,
    form: str,
    filing_date: str,
    metadatas: list[dict] | None = None,
) -> None:
    """
    Embed and store a list of chunks from one filing, with metadata
    that lets us trace each chunk back to its source filing later
    (needed for citing "why did X happen" answers back to a real 10-Q/10-K).

    Uses *upsert* with deterministic IDs (ticker + accession + index), so
    running build_index twice simply overwrites existing chunks instead of
    duplicating them — idempotent by design.

    If metadatas is provided, use it directly instead of building default.
    """
    if not chunks:
        return

    embeddings = embed_documents(chunks)
    ids = [f"{ticker}_{accession_number}_{i}" for i in range(len(chunks))]
    if metadatas is None:
        metadatas = [
            {
                "ticker": ticker,
                "accession_number": accession_number,
                "form": form,
                "filing_date": filing_date,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )


def query(
    collection: Any,
    query_text: str,
    top_k: int = None,
    min_relevance: float = None,
    ticker_filter: str | None = None,
    expand: bool = False,
) -> list[dict]:
    if top_k is None:
        top_k = config.retrieval_top_k
    if min_relevance is None:
        min_relevance = config.retrieval_min_relevance

    where = {"ticker": ticker_filter} if ticker_filter else None

    lookup = expand_query(query_text) if expand else query_text

    results = collection.query(
        query_embeddings=[embed_query(lookup)],
        n_results=top_k,
        where=where,
    )

    output = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
        strict=True,
    ):
        relevance = 1 - distance
        if relevance >= min_relevance:
            output.append({
                "text": doc,
                "metadata": meta,
                "relevance": relevance,
            })

    return output


def _keyword_boost(query_text: str, chunk_text: str) -> float:
    words = _tokenize(query_text)
    stopwords = {"the", "a", "an", "is", "are", "was", "were", "how", "why",
                 "what", "did", "do", "does", "in", "of", "to", "at", "for",
                 "and", "or", "change", "changes", "affect"}
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    if not keywords:
        return 0.0
    chunk_lower = chunk_text.lower()
    matches = sum(1 for w in keywords if w in chunk_lower)
    return matches / len(keywords)


def _retrieve_dense(
    collection: Any,
    query_text: str,
    lookup: str,
    min_relevance: float,
) -> list[dict]:
    results = collection.query(
        query_embeddings=[embed_query(lookup)],
        n_results=config.retrieval_n_candidates,
    )

    candidates = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
        strict=True,
    ):
        relevance = 1 - distance
        if relevance >= min_relevance:
            c = {"text": doc, "metadata": meta, "relevance": relevance}
            if config.keyword_boost_enabled:
                c["keyword_boost"] = _keyword_boost(query_text, doc)
            if config.forward_looking_penalty_enabled:
                c["forward_looking_penalty"] = _forward_looking_penalty(doc)
            candidates.append(c)

    return candidates


def _bm25_cache_key(ticker_filter: str | None) -> str:
    return ticker_filter or "__ALL__"


_BM25_CACHE: dict[str, tuple] = {}
_BM25_MAX_CACHE = 8


def _get_bm25_index(cache_key: str, collection: Any) -> tuple:
    if cache_key in _BM25_CACHE:
        return _BM25_CACHE[cache_key]
    if len(_BM25_CACHE) >= _BM25_MAX_CACHE:
        _BM25_CACHE.pop(next(iter(_BM25_CACHE)))
    get_kw = {}
    if cache_key != "__ALL__":
        get_kw["where"] = {"ticker": cache_key}
    all_docs = collection.get(**get_kw)
    texts = all_docs["documents"]
    metas = all_docs["metadatas"]
    bm25 = build_bm25(texts)
    entry = (bm25, texts, metas)
    _BM25_CACHE[cache_key] = entry
    return entry


def _retrieve_bm25(
    collection: Any,
    lookup: str,
    ticker_filter: str | None,
) -> list[dict]:
    cache_key = _bm25_cache_key(ticker_filter)
    bm25, all_texts, all_metas = _get_bm25_index(cache_key, collection)
    bm25_raw = bm25_scores(bm25, lookup, all_texts)
    paired = sorted(zip(bm25_raw, all_texts, all_metas, strict=True), key=lambda x: -x[0])
    candidates = []
    for score, text, meta in paired:
        candidates.append({"text": text, "metadata": meta, "relevance": score})
    candidates = [c for c in candidates if c["relevance"] > 0]
    return candidates[:config.retrieval_n_candidates]


def _fill_missing_fields(candidates: list[dict], query_text: str) -> None:
    for c in candidates:
        if "keyword_boost" not in c:
            c["keyword_boost"] = _keyword_boost(query_text, c["text"])
        if "forward_looking_penalty" not in c:
            c["forward_looking_penalty"] = _forward_looking_penalty(c["text"])


def query_multi(
    collection: Any,
    query_text: str,
    top_k: int = None,
    min_relevance: float = None,
    ticker_filter: str | None = None,
) -> list[dict]:
    """Multi-stage retrieval: dense → optional BM25 hybrid → cross-encoder rerank.

    Dense retrieval (nomic-embed) is the primary pass. If
    *hybrid_search_enabled*, BM25 scores supplement dense via RRF merge.
    If *cross_encoder_enabled*, final reranking refines the ranking.
    Falls back gracefully if cross-encoder is unavailable.
    """
    if top_k is None:
        top_k = config.retrieval_top_k
    if min_relevance is None:
        min_relevance = config.retrieval_min_relevance

    lookup = expand_query(query_text) if config.expansion_enabled else query_text

    dense = _retrieve_dense(collection, query_text, lookup, min_relevance)
    if not dense:
        return []

    if config.hybrid_search_enabled:
        bm25 = _retrieve_bm25(collection, lookup, ticker_filter)
        candidates = rrf_merge(dense, bm25, top_k=None)
        _fill_missing_fields(candidates, query_text)
    else:
        candidates = dense

    _add_metric_boost(candidates, query_text)

    if config.cross_encoder_enabled:
        try:
            return rerank(query_text, candidates, top_k=top_k)
        except Exception as e:
            logger.warning("Cross-encoder failed, falling back to dense-only: %s", e)

    for c in candidates:
        base = c.get("hybrid_score", c.get("relevance", 0))
        boost = c.get("keyword_boost", 0) * config.keyword_boost_weight if config.keyword_boost_enabled else 0
        metric_boost = c.get("metric_boost", 0)
        penalty = c.get("forward_looking_penalty", 0) if config.forward_looking_penalty_enabled else 0
        c["_sort_score"] = base + boost + metric_boost + penalty
    candidates.sort(key=lambda x: x["_sort_score"], reverse=True)

    return candidates[:top_k]


METRIC_BOOST_CONFIG = {
    "match_weight": 0.2,
}


def _add_metric_boost(chunks: list[dict], query: str) -> None:
    from post_process import _METRIC_TRIGGERS

    query_metric_hints = []
    for trigger in _METRIC_TRIGGERS:
        if trigger.lower() in query.lower():
            query_metric_hints.append(trigger)

    if not query_metric_hints:
        return

    for chunk in chunks:
        chunk_metric = chunk.get("metadata", {}).get("metric", "")
        if not chunk_metric or chunk_metric == "general":
            chunk["metric_boost"] = 0.0
            continue
        matched = any(
            hint.lower() in chunk_metric.lower()
            for hint in query_metric_hints
        )
        chunk["metric_boost"] = METRIC_BOOST_CONFIG["match_weight"] if matched else 0.0


def _forward_looking_penalty(chunk_text: str) -> float:
    chunk_lower = chunk_text.lower()
    matches = sum(1 for p in config.forward_looking_patterns if p in chunk_lower)
    if matches >= 2:
        return config.forward_looking_penalty_weight * 2
    if matches == 1:
        return config.forward_looking_penalty_weight
    return 0.0


