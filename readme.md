# RAG Variance Explainer

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.43-FF4B4B?logo=streamlit)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/chromadb-0.6-FC6D26?logo=chroma)](https://www.trychroma.com)
[![llama.cpp](https://img.shields.io/badge/llama.cpp-GGUF-1E88E5)](https://github.com/ggerganov/llama.cpp)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![CI](https://github.com/redsandr/rag-variance-explainer/actions/workflows/test.yml/badge.svg)](https://github.com/redsandr/rag-variance-explainer/actions)

**Retrieval-Augmented Generation pipeline** that answers *"why did this financial metric change?"* using real SEC filing MD&A sections. Ask plain-language questions about restaurants **and** retail — labor costs, revenue drivers, margin changes, inventory, e-commerce — and get sourced, citation-backed explanations from 10-K/10-Q filings across **5 companies, 2 sectors**.

Target: turn a 4-hour manual variance review into a 3-minute query.

---

## Demo

```bash
streamlit run app.py
```

Dark-themed fintech dashboard with interactive question input, AI-sourced answers, color-coded source chunks, and side-by-side cross-encoder comparison mode.

> **📖 Full documentation:** [docs/](docs/) — problem validation, architecture decisions, evaluation iterations, technical notes, and roadmap.

---

## Features

- **RAG pipeline** — query expansion → ChromaDB retrieval → cross-encoder re-ranking → grounded LLM generation
- **Multi-backend LLM** — llama.cpp (local GPU, 7B), Anthropic, or OpenAI — swappable via `.env`
- **SEC EDGAR ingestion** — auto-fetches MD&A text from 10-K/10-Q filings (Chipotle, Darden, Cracker Barrel, **Walmart, Target**)
- **Retrieval accuracy** — MRR **0.66** (+28% baseline), recall@10 **0.70** (restaurant); **recall@10 = 1.00** (retail)
- **Cross-sector generalization** — pipeline scaled from 3 restaurant to **5 companies across 2 sectors** with **zero recall degradation** (retail recall@10 = 1.00)
- **Faithfulness evaluation** — strict **74.24%** (+8.44pp from baseline), weighted **75.32%** — LLM-as-judge with Claude calibration
- **Cross-encoder re-ranking** — `MiniLM-L-6` with hybrid scoring (CE 0.9 + BI 0.1 + forward-looking penalty)
- **Financial glossary** — 35 synonym groups for query expansion (COGS = Cost of Sales = Cost of Revenue, plus retail: inventory turnover, shrinkage, e-commerce)
- **Streamlit dashboard** — OLED dark mode, KPI metrics, glassmorphism cards, SVG icons, accessibility-ready

---

## Quick Start

### Option A — Local model (llama.cpp, ~4.7 GB)
```bash
# Windows
python -m venv venv && venv\Scripts\activate
# Linux / macOS
python -m venv venv && source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Download Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf → models/
python src/build_index.py
streamlit run app.py
```

### Option B — OpenAI API (no download)
```bash
# Windows
python -m venv venv && venv\Scripts\activate
# Linux / macOS
python -m venv venv && source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```
Then set in `.env`:
```
LLM_BACKEND=openai
OPENAI_API_KEY=sk-...
```
```bash
python src/build_index.py
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
| LLM (default) | `Qwen2.5-7B-Instruct-Q4_K_M` GGUF (RTX 5060, ~2-3s/gen) |
| Data source | SEC EDGAR HTML 10-K/10-Q (MD&A section) |
| Companies | CMG (Chipotle), DRI (Darden), CBRL (Cracker Barrel), **WMT (Walmart), TGT (Target)** |

---

## Evaluation

### Retrieval Recall@k

40 ground-truth questions across **5 companies, 2 sectors** (20 restaurant + 20 retail). Three-stage pipeline: **bi-encoder + glossary → cross-encoder → forward-looking penalty**.

#### Restaurant (CMG, DRI, CBRL)

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

#### Retail (WMT, TGT) — Cross-Sector Generalization

| Ticker | recall@1 | recall@3 | recall@5 | recall@10 | MRR |
|--------|----------|----------|----------|-----------|-----|
| **WMT** (Walmart) | 0.36 | **0.86** | **1.00** | **1.00** | **0.64** |
| **TGT** (Target) | **0.43** | **0.86** | **1.00** | **1.00** | **0.65** |
| **Cross-retail** | 0.33 | 0.75 | **1.00** | **1.00** | **0.65** |

Pipeline generalizes to retail with **zero degradation** — retail recall@10 outperforms restaurant baseline. Cross-sector validation confirms architecture is domain-agnostic, not overfit to restaurant terminology.

### Faithfulness (LLM-as-Judge)

| Phase | Model | Strict | Weighted | Delta |
|-------|-------|--------|----------|-------|
| Baseline | Qwen2.5-VL-7B | 65.8% | 78.9% | — |
| Phase 7e (3 fixes + model swap) | Qwen2.5-7B-Instruct | **74.24%** | **75%** | **+8.44pp** |
| Phase 7f (prompt + parser fix) | Qwen2.5-7B-Instruct | — | **75.32%** | +0.32pp |

Three targeted fixes drove the improvement:
1. **Number transposition** — `verify_answer()` integration catches decimal shifts & year mismatches
2. **Metric conflation** — `MetricVerifier` cross-checks metric labels against source chunk metadata
3. **Causal proximity** — `tag_chunk()` metric enrichment filters retrieval to semantically relevant chunks

Key prompt engineering wins:
- **Period integrity rule** — eval-001 50%→100%, eval-015 20%→67%
- **seed=42** — deterministic output, eval-003 0%→100%
- **Model swap** VL→non-VL — +4.54pp (full 7B capacity for text reasoning)

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
    ├── eval_questions.json    # 40 ground-truth questions (20 restaurant + 20 retail)
    ├── llm_outputs.json       # Cached LLM outputs
    └── faithfulness_results.json
```

---

## Recent Updates

- **Retail expansion** — WMT (Walmart) + TGT (Target) indexed, retail glossary added, recall@10 = **1.00** — cross-sector generalization proven
- **Faithfulness fix** — 74.24% strict (+8.44pp), 75.32% weighted. Model swap VL→non-VL, +4.54pp from text-dedicated capacity
- **Prompt engineering** — period integrity rule (+7pp), seed=42, anti-hallucination checklist, direction verification
- **Cross-encoder re-ranking** — MiniLM-L-6 with hybrid scoring, MRR 0.52 → **0.66** (+28%)
- **Multi-backend LLM** — Swappable via `.env`: llama.cpp (local), Anthropic, or OpenAI
- **Code quality** — `pyproject.toml` packaging, 32 tests, CI pipeline, shared prompts & CSS modules

> Full change history in [docs/](docs/).

## CI

GitHub Actions runs `pytest tests.py -v` on every push and PR (Ubuntu, Python 3.11).

---

## License

MIT
