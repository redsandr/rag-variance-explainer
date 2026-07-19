# Skill: RAG Financial Variance Explainer

Query SEC filings (MD&A sections) across 7 companies, 4 sectors using a
local RAG pipeline. No API keys needed — runs entirely on-device via llama.cpp.

## Available Tools (MCP)

| Tool | What it does |
|------|-------------|
| `rag.answer(question, ticker?)` | Answer with citations from SEC filings |
| `rag.search(query, ticker?, top_k?)` | Return raw chunks with relevance scores |
| `rag.list_companies()` | List all 7 tickers with names + sectors |
| `rag.list_questions(ticker?)` | Get suggested questions per company |

## Companies Supported

| Ticker | Company | Sector |
|--------|---------|--------|
| CMG | Chipotle Mexican Grill | Restaurant |
| DRI | Darden Restaurants | Restaurant |
| CBRL | Cracker Barrel | Restaurant |
| WMT | Walmart | Retail |
| TGT | Target | Retail |
| JNJ | Johnson & Johnson | Healthcare |
| XOM | Exxon Mobil | Energy |

## Workflows

### Analyze a company metric

When user asks about a specific financial metric (revenue, costs, margins):

1. Call `rag.list_questions(ticker)` to check available context
2. Call `rag.answer(question, ticker)` for sourced answer
3. Present answer with citations; note the source filing and date

### Cross-company comparison

When user asks to compare metrics across companies:

1. Call `rag.list_companies()` to confirm which tickers are available
2. For each relevant ticker, call `rag.answer(question, ticker)`
3. Present comparison table with per-company answers

### Raw data exploration

When user wants to see source chunks without LLM interpretation:

1. Call `rag.search(query, ticker, top_k=10)` for raw chunks
2. Present chunks with scores and source metadata

## Notes

- LLM loads lazily on first `rag.answer` call (~5-15s cold start)
- 120s timeout per generation (configurable via `LLM_TIMEOUT`)
- Works entirely offline — no API calls to external services
