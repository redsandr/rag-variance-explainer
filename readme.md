# RAG Variance Explainer

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.43-FF4B4B?logo=streamlit)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/chromadb-0.6-FC6D26?logo=chroma)](https://www.trychroma.com)
[![llama.cpp](https://img.shields.io/badge/llama.cpp-GGUF-1E88E5)](https://github.com/ggerganov/llama.cpp)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![CI](https://github.com/redsandr/rag-variance-explainer/actions/workflows/test.yml/badge.svg)](https://github.com/redsandr/rag-variance-explainer/actions)

**Retrieval-Augmented Generation pipeline** that answers *"why did this financial metric change?"* using real SEC filing MD&A sections. Ask plain-language questions about restaurant companies' financial variances — labor costs, revenue drivers, margin changes — and get sourced, citation-backed explanations from 10-K/10-Q filings.

Target: turn a 4-hour manual variance review into a 3-minute query.

---

## Demo

```bash
streamlit run app.py
```

Dark-themed fintech dashboard with interactive question input, AI-sourced answers, color-coded source chunks, and side-by-side cross-encoder comparison mode.

![Dashboard Screenshot](docs/screenshot.png)
<!-- TODO: Add a screenshot showing the dashboard with a sample question, answer, and source cards -->

> **Quick links:** [Full project documentation](docs/) — problem validation, architecture decisions, evaluation iterations, and technical notes.

---

## Features

- **RAG pipeline** — query expansion → ChromaDB retrieval → cross-encoder re-ranking → grounded LLM generation
- **Multi-backend LLM** — llama.cpp (local GPU, 7B), Anthropic, or OpenAI — swappable via `.env`
- **SEC EDGAR ingestion** — auto-fetches MD&A text from 10-K/10-Q filings (Chipotle, Darden, Cracker Barrel)
- **Retrieval accuracy** — MRR **0.66** (+28% baseline), recall@10 **0.70** (4 failing cases → 0)
- **Faithfulness evaluation** — LLM-as-judge scoring, Claude calibration, period-integrity prompt engineering
- **Cross-encoder re-ranking** — `MiniLM-L-6` with hybrid scoring (CE 0.9 + BI 0.1 + forward-looking penalty)
- **Financial glossary** — 20 synonym groups for query expansion (COGS = Cost of Sales = Cost of Revenue)
- **Streamlit dashboard** — OLED dark mode, KPI metrics, glassmorphism cards, SVG icons, accessibility-ready

---

## Quick Start

```bash
# Setup
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Configuration
cp .env.example .env           # Set LLM backend, model path, RAG params

# Download model (Qwen2.5-VL-7B-Instruct Q4_K_M ~4.7 GB)
# Place .gguf in models/

# Build vector index (432 chunks from 24 filings)
python src/build_index.py

# Launch demo
streamlit run app.py
```

### Configuration

All parameters via env vars — no hardcoded magic numbers.

| Variable | Default | Description |
|---|---|---|
| `LLM_BACKEND` | `llama_cpp` | `llama_cpp`, `anthropic`, or `openai` |
| `RAG_CROSS_ENCODER_ENABLED` | `true` | Enable cross-encoder re-ranking |
| `RAG_CROSS_ENCODER_WEIGHT` | `0.7` | CE vs bi-encoder blend |
| `RAG_TOP_K` | `5` | Final chunks returned to LLM |
| `RAG_EXPANSION_N_TERMS` | `5` | Synonym count per query |
| `RAG_FORWARD_LOOKING_PENALTY_ENABLED` | `true` | Penalize risk-factor chunks |
| `RAG_LLM_MAX_TOKENS` | `2048` | Max generation tokens |
| `RAG_LLM_TEMPERATURE` | `0.1` | Generation temperature |

---

## Architecture

```
User Question
    |
    v
  query_expansion (5 synonyms, 20 financial groups)
    |
    v
  ChromaDB + nomic-embed (bi-encoder) → top 20 candidates
    |
    v
  forward_looking_penalty (configurable patterns/weight)
    |
    v
  cross-encoder re-ranking (MiniLM-L-6, hybrid score)
    |
    v
  top_k chunks → LLMClient → grounded answer + citations
```

| Component | Technology |
|---|---|
| Embedding | `nomic-embed-text-v1.5` (768-dim, normalized) |
| Vector store | ChromaDB, cosine distance, metadata-rich |
| Re-ranking | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Chunking | Structure-aware recursive split, 500-token chunks |
| LLM (default) | `Qwen2.5-VL-7B-Instruct-Q4_K_M` (RTX 5060, ~2-3s/gen) |
| Data source | SEC EDGAR HTML 10-K/10-Q (MD&A section) |
| Companies | CMG (Chipotle), DRI (Darden), CBRL (Cracker Barrel) |

---

## Evaluation

### Retrieval Recall@k

20 ground-truth questions across 3 companies. Three-stage pipeline: **bi-encoder + glossary → cross-encoder → forward-looking penalty**.

| Metric | Baseline | query_multi | + CE | Delta |
|---|---|---|---|---|
| recall@1 | 0.18 | 0.14 | **0.23** | +0.05 |
| recall@3 | 0.24 | 0.42 | **0.45** | +0.21 |
| recall@5 | 0.33 | 0.51 | **0.52** | +0.19 |
| recall@10 | 0.55 | 0.71 | 0.70 | +0.15 |
| **MRR** | **0.52** | **0.57** | **0.66** | **+0.14** |

Hardest-case turnaround:

| Case | Before | After | Fix |
|---|---|---|---|
| CMG G&A (eval-009) | rank 17, recall@10=0.00 | **rank 1, recall@10=0.67** | Cross-encoder re-ranking |
| CBRL labor (eval-017) | rank 17, recall@10=0.00 | **rank 1, recall@10=1.00** | Cross-encoder re-ranking |
| DRI marketing (eval-002) | rank 14, recall@10=0.00 | **rank 8, recall@10=1.00** | Forward-looking penalty |
| recall@10=0 cases | 4/20 | **0/20** | Combined pipeline |

### Faithfulness (LLM-as-Judge)

Automated eval across 149 claims from 20 questions (local Qwen 2.5 Coder 14B, truncated source chunks):

```
Strict:   65.8%  (98 faithful / 39 partial / 12 unfaithful)
Weighted: 78.9%  (partial weighted 0.5)
```

The automated judge penalizes truncation artifacts: Claude re-evaluation with **full source chunks** raises strict faithfulness to **74.8%** (95 faithful / 18 partial / 14 unfaithful), and Gemini's evaluation to **86.7%** (with a stricter 10-rule checklist). The gap between automated (65.8%) and human-eval (74.8–86.7%) is mostly truncation bias — the judge cannot see the full source to verify claims.

Known remaining issues:
- **Metric conflation** (4–5% of errors): model writes "comparable sales" where source says "total revenue" or vice versa
- **Number transposition** (2–3%): decimal shifts (0.6% → 6%), column year mismatches (FY2024 → FY2023)
- **Causal proximity** (~7%): model attributes driver from adjacent section to wrong metric

Key improvements via prompt engineering:
- **Period integrity rule** — eval-001 50%→100%, eval-015 20%→67%
- **seed=42** — deterministic output, eval-003 0%→100%
- **Anti-hallucination checklist** — strict number verification, no training data
- **Direction verification** — prevents self-contradictory claims

---

## Project Structure

```
├── pyproject.toml             # Package config with dependencies (pip install -e .)
├── app.py                     # Streamlit dashboard (DB-driven KPI)
├── .streamlit/config.toml     # Dark theme config
├── .env / .env.example        # Configuration
├── Makefile                   # install / test / run / eval-*
├── tests.py                   # 32 pytest tests (9 modules)
├── .github/workflows/test.yml # CI pipeline
├── docs/                      # Extended documentation (problem validation, iteration history)
├── src/
│   ├── rag.py                 # RAG orchestrator
│   ├── retrieval.py           # ChromaDB + multi-strategy retrieval
│   ├── cross_encoder.py       # Cross-encoder re-ranking
│   ├── hybrid_search.py       # BM25 + RRF merge
│   ├── query_expansion.py     # Financial synonym expansion
│   ├── llm.py                 # 3-backend LLM client
│   ├── config.py              # Centralized config (22 params from env vars)
│   ├── prompts.py             # RAG system prompt + judge prompts (3 variants) + helpers
│   ├── styles.css             # Dashboard stylesheet (imported by app.py)
│   ├── logging_config.py      # Shared logging setup
│   ├── ingest.py              # SEC EDGAR fetcher
│   ├── embedding.py           # nomic-embed wrapper
│   ├── chunking.py            # Structure-aware chunking
│   ├── build_index.py         # End-to-end index pipeline
│   └── eval_*.py              # Evaluation scripts
└── data/
    ├── eval_questions.json    # 20 ground-truth questions
    ├── llm_outputs.json       # Cached LLM outputs
    └── faithfulness_results.json
```

---

## Refactoring (Jul 2026)

- **`pyproject.toml`** — Proper package build (`pip install -e .`) removes fragile `sys.path.insert()` hacks from 5 files.
- **`src/prompts.py`** — Extracted 3 judge prompt variants (`_FULL`, `_MEDIUM`, `_COMPACT`) + `build_judge_prompt()` helpers into a single module.
- **`src/styles.css`** — 510 lines of inline CSS extracted from `app.py` into a standalone stylesheet.
- **Dead code removed** — `build_multi_queries()` (query_expansion.py), `check_reported_tags()` / `list_all_taxonomies_and_matching_tags()` (ingest.py), all demo `__main__` blocks.
- **Deferred imports** — `from retrieval import ...` and `from llm import LLMClient` lifted to top level in `rag.py`.

## CI

GitHub Actions runs `pytest tests.py -v` on every push and PR (Ubuntu, Python 3.11).

---

## License

MIT
