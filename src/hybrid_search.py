from __future__ import annotations

import hashlib
import re

from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from rank_bm25 import BM25Okapi
    HAS_BM25_LIB = True
except ImportError:
    HAS_BM25_LIB = False


def _tokenize(text: str) -> list[str]:
    return re.findall(r'\w+', text.lower())


def _content_key(text: str) -> str:
    return text[:120] + hashlib.md5(text.encode(), usedforsecurity=False).hexdigest()


def build_bm25(corpus: list[str]) -> BM25Okapi | TfidfVectorizer:
    tokenized = [_tokenize(d) for d in corpus]
    if HAS_BM25_LIB:
        return BM25Okapi(tokenized)
    vec = TfidfVectorizer(
        tokenizer=_tokenize,
        lowercase=False,
        use_idf=True,
        sublinear_tf=True,
    )
    vec.fit(corpus)
    return vec


def bm25_scores(bm25: BM25Okapi | TfidfVectorizer, query: str, corpus: list[str]) -> list[float]:
    tokens = _tokenize(query)
    if HAS_BM25_LIB:
        return bm25.get_scores(tokens)
    from sklearn.metrics.pairwise import cosine_similarity
    qv = bm25.transform([query])
    dv = bm25.transform(corpus)
    return cosine_similarity(qv, dv)[0].tolist()


def rrf_merge(
    dense_list: list[dict],
    bm25_list: list[dict],
    k: int = 60,
    top_k: int | None = None,
) -> list[dict]:
    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for rank, r in enumerate(dense_list):
        key = _content_key(r["text"])
        items[key] = r
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)

    for rank, r in enumerate(bm25_list):
        key = _content_key(r["text"])
        if key not in items:
            items[key] = r
        scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)

    ranked = sorted(scores.keys(), key=lambda t: scores[t], reverse=True)
    if top_k:
        ranked = ranked[:top_k]

    out = []
    for key in ranked:
        item = dict(items[key])
        item["hybrid_score"] = scores[key]
        out.append(item)
    return out
