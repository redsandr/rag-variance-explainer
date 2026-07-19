"""
REST API for RAG Variance Explainer.

FastAPI application wrapping the RAG pipeline. Can run standalone or
alongside the existing Streamlit UI.

Usage:
  uvicorn src.api:app --reload
  python -m src.api                    # same via __main__ block
"""

import logging
import time
from contextlib import asynccontextmanager

try:
    from fastapi import FastAPI, HTTPException, Query
except ImportError:
    raise RuntimeError("Missing 'fastapi'. Install: pip install fastapi uvicorn") from None

from ingest import TICKERS

logger = logging.getLogger(__name__)

_SECTORS: dict[str, str] = {
    "CMG": "Restaurant",
    "DRI": "Restaurant",
    "CBRL": "Restaurant",
    "WMT": "Retail",
    "TGT": "Retail",
    "JNJ": "Healthcare",
    "XOM": "Energy",
}

_VERSION = "1.0.0"

# --- lifespan ---

_llm_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _llm_ready
    logger.info("RAG API starting — LLM will load on first request")
    _llm_ready = True
    yield
    logger.info("RAG API shutting down")


app = FastAPI(
    title="RAG Variance Explainer API",
    description="Query SEC filings (MD&A) across 7 companies, 4 sectors. "
    "Ask financial questions, search chunks, or list available companies.",
    version=_VERSION,
    lifespan=lifespan,
)


# --- helpers ---


def _validate_ticker(ticker: str | None) -> str | None:
    if ticker is None:
        return None
    t = ticker.upper().strip()
    if t not in TICKERS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown ticker '{ticker}'. Available: {', '.join(sorted(TICKERS))}",
        )
    return t


# --- endpoints ---


@app.get("/")
def root():
    return {
        "service": "RAG Variance Explainer",
        "version": _VERSION,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "POST /answer": "Answer a financial question with sourced citations",
            "POST /search": "Search chunks by relevance (no LLM)",
            "GET /companies": "List available companies with sectors",
            "GET /health": "Pipeline health check",
        },
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_ready": _llm_ready,
        "companies": len(TICKERS),
        "sectors": len(set(_SECTORS.values())),
    }


@app.get("/companies")
def list_companies():
    companies = []
    for ticker in sorted(TICKERS):
        companies.append({
            "ticker": ticker,
            "name": TICKERS[ticker],
            "sector": _SECTORS.get(ticker, "Unknown"),
        })
    return {
        "companies": companies,
        "total": len(companies),
        "sectors": sorted(set(_SECTORS.values())),
    }


@app.post("/search")
def search(
    query: str = Query(..., min_length=1, max_length=256, description="Search query"),
    ticker: str | None = Query(None, description="Filter by ticker (optional)"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results"),
):
    validated_ticker = _validate_ticker(ticker)

    from retrieval import get_client, get_collection, query_multi

    start = time.perf_counter()
    try:
        client = get_client()
        collection = get_collection(client)
        results = query_multi(collection, query, top_k=top_k, ticker_filter=validated_ticker)
    except Exception as exc:
        logger.exception("POST /search failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    elapsed = round(time.perf_counter() - start, 3)

    chunks = []
    for r in results:
        meta = r["metadata"]
        chunks.append({
            "text": r["text"],
            "ticker": meta.get("ticker"),
            "form": meta.get("form"),
            "filing_date": meta.get("filing_date"),
            "score": round(r.get("hybrid_score", r.get("relevance", 0)), 4),
        })

    return {
        "query": query,
        "ticker_filter": validated_ticker,
        "results": chunks,
        "total": len(chunks),
        "elapsed_seconds": elapsed,
    }


@app.post("/answer")
def answer(
    question: str = Query(..., min_length=1, max_length=256, description="Financial question"),
    ticker: str | None = Query(None, description="Filter by ticker (optional)"),
):
    validated_ticker = _validate_ticker(ticker)

    from rag import answer_question

    start = time.perf_counter()
    try:
        result = answer_question(question, ticker_filter=validated_ticker)
    except Exception as exc:
        logger.exception("POST /answer failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    elapsed = round(time.perf_counter() - start, 3)

    sources = []
    for r in result.get("sources", []):
        meta = r["metadata"]
        sources.append({
            "text": r["text"],
            "ticker": meta.get("ticker"),
            "form": meta.get("form"),
            "filing_date": meta.get("filing_date"),
            "score": round(r.get("hybrid_score", r.get("relevance", 0)), 4),
        })

    return {
        "question": result["question"],
        "answer": result["answer"],
        "sources": sources,
        "source_count": len(sources),
        "elapsed_seconds": elapsed,
    }


# --- CLI entrypoint ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
