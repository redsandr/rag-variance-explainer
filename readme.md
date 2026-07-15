# RAG Variance Explainer

Retrieval-Augmented Generation pipeline that answers "why did this financial metric change?" using SEC filing MD&A sections. Given a question about a restaurant company's financial variance (labor costs, revenue, margins, etc.), the system retrieves the most relevant excerpts from 10-K/10-Q filings and generates a grounded, citation-backed explanation.

## Demo

```bash
streamlit run app.py
```

Dark-themed Streamlit UI with source cards and color-coded relevance scores.

## Quick Start

```bash
# Install
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt

# Set up .env (see .env.example)
# LLM backend, model path, RAG config

# Download a model (e.g. Qwen2.5-VL-7B-Instruct Q4_K_M)
# Place .gguf in models/

# Build the ChromaDB index
python src/build_index.py

# Run the demo
streamlit run app.py
```

## Architecture

```
User Question
    |
    v
  query_expansion (5 synonyms, 20 financial groups)
    |
    v
  ChromaDB + nomic-embed (bi-encoder) -- top 20 candidates
    |
    v
  forward_looking_penalty (configurable patterns/weight)
    |
    v
  cross-encoder re-ranking (MiniLM-L-6, hybrid score: 0.9*CE + 0.1*BI + penalty + boost)
    |
    v
  top_k chunks -> LLMClient (llama.cpp / Anthropic / OpenAI) -> grounded answer + citations
```

- **Embedding**: `nomic-embed-text-v1.5` (768-dim, normalized) with `search_document`/`search_query` prefixes
- **Re-ranking**: `cross-encoder/ms-marco-MiniLM-L-6-v2` with hybrid scoring
- **Vector Store**: ChromaDB, cosine distance, metadata-rich (ticker, form, filing date)
- **Chunking**: Structure-aware recursive splitting via `tiktoken` (500-token chunks, 50-token overlap)
- **Config**: `src/config.py` reads all thresholds/weights/model names from env vars — no hardcoded magic numbers
- **Ingestion**: SEC EDGAR HTML 10-K/10-Q filings, MD&A section extraction via BeautifulSoup + regex
- **LLM Backend**: llama.cpp (local GPU, 7B model) or Anthropic/OpenAI API via `LLM_BACKEND=.env`

## Model

Default: `Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf` (4.68 GB, ~2-3s per generation on RTX 5060).

Configure path in `.env`:
```
LLAMA_CPP_MODEL_PATH=models/Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf
LLM_BACKEND=llama_cpp
```

Context window: 8192 tokens (`n_ctx` in `src/llm.py`).

## Evaluation Results

### Retrieval Recall@k

20 ground-truth questions across CMG (7), DRI (6), CBRL (7). Three-stage retrieval pipeline: bi-encoder + glossary expansion -> cross-encoder re-ranking -> forward-looking penalty.

| Recall | Baseline | query_multi | + cross-encoder | Delta (baseline -> final) |
|--------|----------|-------------|-----------------|--------------------------|
| recall@1 | 0.18 | 0.14 | **0.23** | **+0.05** |
| recall@3 | 0.24 | 0.42 | **0.45** | **+0.21** |
| recall@5 | 0.33 | 0.51 | **0.52** | **+0.19** |
| recall@8 | 0.38 | 0.67 | 0.66 | +0.28 |
| recall@10 | 0.55 | 0.71 | 0.70 | +0.15 |
| recall@20 | 0.86 | 0.91 | 0.91 | +0.05 |
| **MRR** | **0.52** | **0.57** | **0.66** | **+0.14** |

Hardest-case turnaround:

| Case | Before | After | Fix |
|------|--------|-------|-----|
| CMG G&A (eval-009) | rank 17, recall@10=0.00 | **rank 1, recall@10=0.67** | Cross-encoder re-ranking |
| CBRL labor (eval-017) | rank 17, recall@10=0.00 | **rank 1, recall@10=1.00** | Cross-encoder re-ranking |
| DRI marketing (eval-002) | rank 14, recall@10=0.00 | **rank 8, recall@10=1.00** | Forward-looking penalty |
| recall@10=0 cases | 4/20 | **0/20** | Combined pipeline |

### Faithfulness (LLM-as-Judge)

Automated evaluation via `eval_faithfulness.py`: for each question, the RAG pipeline generates an answer, then the same LLM judges each factual claim against the source chunks.

**Latest full run (20 questions, Qwen2.5-VL-7B):**
```
Strict:   59.7% (40F / 20P / 7U)
Weighted: 74.6%  (partial weighted 0.5)
```

| Metric | Value |
|--------|-------|
| Total claims evaluated | 67 |
| Faithful | 40 |
| Partially faithful | 20 |
| Unfaithful | 7 |
| Parse failures | 4 (overflow — fixed with n_ctx=8192) |
| Retrieval gaps | 1 (eval-006: food costs not found) |

**Scoring:** `faithfulness_score` is computed programmatically from verdict counts (`faithful / total`) — strict score displayed alongside weighted score (partial = 0.5). Results include both in output JSON.

**Known patterns:**
- Multi-period / multi-quarter questions tend toward PARTIAL (judge flags period mismatches)
- Retrieval gaps logged separately as `retrieval_gap` (not counted in faithfulness)
- Checkpoint saving after each question — partial results preserved if interrupted

## Project Structure

```
├── app.py                          # Streamlit demo UI (dark theme)
├── .streamlit/config.toml          # Dark theme config
├── .env / .env.example             # Config (all RAG params via env vars)
├── AGENTS.md                       # Agent instructions
├── Makefile                        # install, test, run, eval-* targets
├── models/                         # .gguf model files (gitignored)
├── .github/workflows/test.yml      # CI: pytest on push/PR
├── src/
│   ├── config.py                   # Centralized config dataclass from env
│   ├── cross_encoder.py            # Cross-encoder re-ranking + hybrid scoring
│   ├── retrieval.py                # ChromaDB + query_multi pipeline
│   ├── query_expansion.py          # 20-group financial synonym expansion
│   ├── glossary.py                 # Per-company XBRL tag mappings
│   ├── rag.py                      # RAG orchestrator (retrieve -> generate)
│   ├── llm.py                      # 3-backend LLM client (llama.cpp/Anthropic/OpenAI)
│   ├── embedding.py                # nomic-embed wrapper with prefixing
│   ├── chunking.py                 # Structure-aware recursive chunking
│   ├── ingest.py                   # SEC EDGAR fetcher + MD&A extraction
│   ├── build_index.py              # E2E pipeline: fetch -> chunk -> embed -> store
│   ├── eval_recall.py              # Retrieval recall@k evaluation
│   ├── eval_llm.py                 # LLM output generation + caching
│   └── eval_faithfulness.py        # LLM-as-judge faithfulness evaluation
├── data/
│   ├── eval_questions.json         # 20 ground-truth eval questions
│   ├── llm_outputs.json            # Cached LLM outputs
│   └── faithfulness_results.json   # Automated faithfulness eval results
├── tests.py                        # 7 pytest tests
└── README.md                       # This file
```

## RAG Config (all optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_CROSS_ENCODER_ENABLED` | `true` | Enable cross-encoder re-ranking |
| `RAG_CROSS_ENCODER_WEIGHT` | `0.7` | CE vs bi-encoder blend (0=pure BI, 1=pure CE) |
| `RAG_CROSS_ENCODER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Cross-encoder model |
| `RAG_CROSS_ENCODER_DEVICE` | `cpu` | `cpu` or `cuda` |
| `RAG_FORWARD_LOOKING_PENALTY_ENABLED` | `true` | Penalize risk factor chunks |
| `RAG_FORWARD_LOOKING_PATTERNS` | *(built-in list)* | Comma-separated penalty phrases |
| `RAG_EXPANSION_N_TERMS` | `5` | Glossary synonym count per query |
| `RAG_TOP_K` | `5` | Final chunks returned to LLM |
| `RAG_N_CANDIDATES` | `20` | Candidates before re-ranking |

## CI

GitHub Actions runs `pytest tests.py -v` on every push and PR (Ubuntu, Python 3.11, Node.js 24 runtime).

## TODO / Future Work

- [ ] Cross-encoder on GPU (install torch with CUDA)
- [ ] Improve table-heavy chunk embedding (restaurant counts, segment tables)
- [ ] More tickers / industries
- [ ] Reduce judge overstrictness on multi-period claims
