"""
MCP server for RAG Variance Explainer.

Exposes the RAG pipeline as MCP tools consumable by AI agents
(Claude Code, Cursor, Cline, Windsurf, etc.).

Transport:
  stdio (default) — for local MCP clients
  --sse           — Streamable HTTP for remote clients

Usage:
  python src/server.py                          # stdio
  python src/server.py --sse                    # SSE on :8000
  python src/server.py --sse --port 8080        # custom port
"""

import argparse
import logging
import sys
from typing import Any

from constants import SECTORS, TICKERS
from rag import answer_question
from retrieval import get_client, get_collection, query_multi

logger = logging.getLogger(__name__)

try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.fastmcp.exceptions import ToolError
    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False

    class ToolError(RuntimeError):  # type: ignore[no-redef]
        pass

mcp: Any

if _MCP_AVAILABLE:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP(
    "RAG Variance Explainer",
    instructions="""Financial RAG pipeline that answers questions about SEC filings
(MD&A sections) from 7 companies across 4 sectors (Restaurant, Retail, Healthcare, Energy).

Tools:
- rag.answer: answer a question with citations from SEC filings
- rag.search: search chunks with relevance scores (no LLM generation)
- rag.list_companies: list available tickers with company names and sectors
- rag.list_questions: get suggested questions for a ticker or all companies
""",
    )
else:
    class _PlaceholderMCP:
        def __getattr__(self, name: str) -> Any:
            return lambda *a, **kw: None
        def tool(self, *a: Any, **kw: Any) -> Any:
            return lambda f: f
    mcp = _PlaceholderMCP()

_SUGGESTED_QUESTIONS: dict[str, list[str]] = {
    "CMG": [
        "How did Chipotle's revenue change in FY2024?",
        "What drove Chipotle's labor cost changes?",
        "How did Chipotle's comparable restaurant sales perform?",
    ],
    "DRI": [
        "How did Darden's total revenue change?",
        "What drove Darden's food and beverage costs?",
        "How did Olive Garden segment perform?",
    ],
    "CBRL": [
        "How did Cracker Barrel's revenue change?",
        "What drove Cracker Barrel's labor costs?",
        "How did Cracker Barrel's comparable store sales change?",
    ],
    "WMT": [
        "How did Walmart's revenue change in FY2025?",
        "What drove Walmart's gross margin changes?",
        "How did Walmart's e-commerce sales perform?",
    ],
    "TGT": [
        "How did Target's comparable sales change?",
        "What drove Target's gross margin rate changes?",
        "How did Target's inventory change?",
    ],
    "JNJ": [
        "How did Johnson & Johnson's revenue change?",
        "What drove J&J's operating income changes?",
        "How did J&J's pharmaceutical segment perform?",
    ],
    "XOM": [
        "How did ExxonMobil's earnings change?",
        "What drove ExxonMobil's upstream results?",
        "How did ExxonMobil's cash flow from operations change?",
    ],
}

_GENERIC_QUESTIONS: list[str] = [
    "How did revenue change across sectors?",
    "Which companies reported labor cost increases?",
    "Compare gross margin trends between sectors.",
]


def _format_source(r: dict, idx: int) -> str:
    meta = r["metadata"]
    score = r.get("hybrid_score", r.get("relevance", 0))
    return (
        f"[{idx}] {meta['ticker']} {meta['form']} filed {meta['filing_date']}\n"
        f"    Score: {score:.3f}\n"
        f"    {r['text'][:300]}{'...' if len(r['text']) > 300 else ''}"
    )


# ---- MCP Tools ----


@mcp.tool(
    name="rag.answer",
    description="Answer a financial question using SEC filing context. Returns a sourced answer with citations.",
)
def answer(
    question: str,
    ticker: str | None = None,
) -> str:
    if ticker:
        ticker = ticker.upper()
        if ticker not in TICKERS:
            available = ", ".join(sorted(TICKERS))
            raise ToolError(f"Unknown ticker '{ticker}'. Available: {available}")

    try:
        result = answer_question(question, ticker_filter=ticker)
    except Exception as exc:
        logger.exception("rag.answer failed")
        raise ToolError(f"Error generating answer: {exc}") from exc

    lines = [f"# {result['question']}", "", result["answer"], "", "## Sources"]
    for i, src in enumerate(result.get("sources", []), 1):
        lines.append("")
        lines.append(_format_source(src, i))
    return "\n".join(lines)


@mcp.tool(
    name="rag.search",
    description="Search SEC filing chunks by relevance. Returns chunks with scores — no LLM generation.",
)
def search(
    query: str,
    ticker: str | None = None,
    top_k: int = 5,
) -> str:
    if ticker:
        ticker = ticker.upper()
        if ticker not in TICKERS:
            available = ", ".join(sorted(TICKERS))
            raise ToolError(f"Unknown ticker '{ticker}'. Available: {available}")

    try:
        client = get_client()
        collection = get_collection(client)
        results = query_multi(collection, query, top_k=top_k, ticker_filter=ticker)
    except Exception as exc:
        logger.exception("rag.search failed")
        raise RuntimeError(f"Error searching: {exc}") from exc

    if not results:
        return "No relevant chunks found."

    parts = [f"## Top {len(results)} results for: {query}", ""]
    for i, r in enumerate(results, 1):
        parts.append(_format_source(r, i))
        parts.append("")
    return "\n".join(parts)


@mcp.tool(
    name="rag.list_companies",
    description="List all available companies with tickers, names, and industry sectors.",
)
def list_companies() -> str:
    lines = ["## Available Companies\n", "| Ticker | Company | Sector |"]
    lines.append("|--------|---------|--------|")
    for ticker in sorted(TICKERS):
        sector = SECTORS.get(ticker, "Unknown")
        lines.append(f"| {ticker} | {TICKERS[ticker]} | {sector} |")
    lines.append("")
    lines.append(f"**Total: {len(TICKERS)} companies across {len(set(SECTORS.values()))} sectors**")
    return "\n".join(lines)


@mcp.tool(
    name="rag.list_questions",
    description="Get suggested questions for a ticker or all companies. Use these as starting points for rag.answer.",
)
def list_questions(ticker: str | None = None) -> str:
    if ticker:
        ticker = ticker.upper()
        if ticker in _SUGGESTED_QUESTIONS:
            qs = _SUGGESTED_QUESTIONS[ticker]
            lines = [f"## Suggested Questions for {ticker} ({TICKERS[ticker]})\n"]
            for i, q in enumerate(qs, 1):
                lines.append(f"{i}. {q}")
            return "\n".join(lines)
        if ticker == "ALL":
            lines = ["## Suggested Questions for All Companies\n"]
            for t in sorted(_SUGGESTED_QUESTIONS):
                lines.append(f"\n### {t} ({TICKERS[t]})")
                for q in _SUGGESTED_QUESTIONS[t]:
                    lines.append(f"- {q}")
            lines.append("\n### Cross-company")
            for q in _GENERIC_QUESTIONS:
                lines.append(f"- {q}")
            return "\n".join(lines)
        available = ", ".join(sorted(TICKERS)) + ", ALL"
        raise ToolError(f"Unknown ticker '{ticker}'. Available: {available}")
    qs = _GENERIC_QUESTIONS
    lines = ["## Suggested Questions (Cross-company)\n"]
    for i, q in enumerate(qs, 1):
        lines.append(f"{i}. {q}")
    lines.append("\n_Use ticker='ALL' to see per-company questions._")
    return "\n".join(lines)


# ---- MCP Resources ----


@mcp.resource(
    "rag://companies",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def companies_resource() -> str:
    """List all available companies with tickers, names, and sectors."""
    import json
    data = [
        {"ticker": t, "name": TICKERS[t], "sector": SECTORS.get(t, "Unknown")}
        for t in sorted(TICKERS)
    ]
    return json.dumps(data, indent=2)


@mcp.resource(
    "rag://companies/{ticker}",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def company_resource(ticker: str) -> str:
    """Get details for a specific company by ticker."""
    import json
    t = ticker.upper()
    if t not in TICKERS:
        return json.dumps({"error": f"Unknown ticker '{t}'"}, indent=2)
    data = {
        "ticker": t,
        "name": TICKERS[t],
        "sector": SECTORS.get(t, "Unknown"),
    }
    return json.dumps(data, indent=2)


@mcp.resource(
    "rag://companies/{ticker}/questions",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def company_questions_resource(ticker: str) -> str:
    """Get suggested questions for a specific company."""
    import json
    t = ticker.upper()
    if t in _SUGGESTED_QUESTIONS:
        return json.dumps({"ticker": t, "questions": _SUGGESTED_QUESTIONS[t]}, indent=2)
    return json.dumps({"error": f"Unknown ticker '{t}'"}, indent=2)


@mcp.resource(
    "rag://stats",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
def stats_resource() -> str:
    """Get pipeline statistics: companies, sectors, total filings, chunks."""
    import json
    sectors = set(SECTORS.values())
    data = {
        "companies": len(TICKERS),
        "sectors": len(sectors),
        "sector_list": sorted(sectors),
        "chunks": None,
        "filings": None,
    }
    try:
        from retrieval import get_client, get_collection
        client = get_client()
        collection = get_collection(client)
        data["chunks"] = collection.count()
    except Exception:
        pass
    return json.dumps(data, indent=2)


# ---- CLI Entrypoint ----


def main() -> None:
    if not _MCP_AVAILABLE:
        print("Missing 'mcp' package. Install: pip install mcp", file=sys.stderr)
        sys.exit(1)
    parser = argparse.ArgumentParser(description="RAG Variance Explainer MCP Server")
    parser.add_argument("--sse", action="store_true", help="Run with SSE transport (default: stdio)")
    parser.add_argument("--port", type=int, default=8000, help="Port for SSE transport (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host for SSE transport (default: 127.0.0.1)")
    args = parser.parse_args()

    if args.sse:
        logger.info("Starting MCP server with SSE transport on %s:%d", args.host, args.port)
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        logger.info("Starting MCP server with stdio transport")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
