# RAG Variance Explainer — Claude Code Context

Financial RAG pipeline analyzing SEC filing MD&A sections from 7 companies
across 4 sectors. Runs entirely on-device via llama.cpp (no API keys needed).

## MCP Server (Primary Interface)

Configure in `claude.json`:
```json
{
  "mcpServers": {
    "rag-variance-explainer": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "/path/to/rag-variance-explainer"
    }
  }
}
```

### MCP Tools

- `rag.answer(question, ticker?)` — answer with sourced citations
- `rag.search(query, ticker?, top_k?)` — raw chunks with scores
- `rag.list_companies()` — 7 tickers with names + sectors
- `rag.list_questions(ticker?)` — suggested questions per company

### Example Workflows

**Single company query:**
→ "How did Chipotle's revenue change?"
→ `rag.list_companies()` → `rag.answer("How did revenue change?", "CMG")`

**Cross-company comparison:**
→ "Compare Walmart and Target inventory trends"
→ `rag.answer("How did inventory change?", "WMT")` + `rag.answer(...`, "TGT")`

## REST API (Alternative)

```bash
uvicorn src.api:app --port 8000
curl -X POST "http://localhost:8000/answer?question=How+did+CMG+revenue+change%3F&ticker=CMG"
```

## Quick Reference

| Command | What |
|---------|------|
| `make test` | pytest 47 tests |
| `make lint` | ruff check |
| `make typecheck` | mypy |
| `make mcp` | start MCP server (stdio) |
| `make api` | start FastAPI on :8000 |
| `make run` | start Streamlit UI |

## Key Files

| File | Purpose |
|------|---------|
| `src/rag.py` | `answer_question()` — end-to-end pipeline |
| `src/retrieval.py` | `query_multi()` — dense + BM25 + cross-encoder |
| `src/llm.py` | `LLMClient` — llama.cpp / OpenAI / Anthropic |
| `src/server.py` | MCP server |
| `src/api.py` | FastAPI REST wrapper |
| `src/config.py` | All config via env vars |
| `tests.py` | 47 tests |
| `conftest.py` | Auto-mocks LLM in tests |

## Evaluation

- recall@10: 0.81, MRR: 0.54
- Faithfulness: 59.29% strict (cross-sector), 74.24% (restaurant)
- 1079 chunks across 56 filings
- 42 tests, ruff 0, mypy 0, bandit 0

## Important

- `conftest.py` patches all LLM init methods — tests never call real LLMs
- LLM loads lazily on first use (cold start ~5-15s)
- `.env` file required for API keys (OpenAI/Anthropic backends)
