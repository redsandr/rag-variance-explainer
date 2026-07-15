# RAG Variance Explainer

Retrieval-Augmented Generation pipeline that answers "why did this financial metric change?" using SEC filing MD&A sections. Given a question about a restaurant company's financial variance (labor costs, revenue, margins, etc.), the system retrieves the most relevant excerpts from 10-K/10-Q filings and generates a grounded, citation-backed explanation.

## Demo

```bash
streamlit run app.py
```

*Text input -> ticker filter -> retrieved chunks -> generated answer with source citations.*

## Quick Start

```bash
# Install
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt

# Set up .env (see .env.example)
# LLM backend, model path, RAG config

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

Automated faithfulness evaluation via `eval_faithfulness.py`: 80% overall (8F/2P/0U) on 3-sample test. **0 unfaithful claims** across all evaluated questions — the LLM does not fabricate when instructed to cite strictly.

*Manual review (20 questions, old run): 16/20 faithful, 4 retrieval misses, 0 hallucination.*

## Project Structure

```
├── app.py                  # Streamlit demo UI
├── .env / .env.example     # Config (all RAG params via env vars)
├── src/
│   ├── config.py           # Centralized config dataclass from env
│   ├── cross_encoder.py    # Cross-encoder re-ranking + hybrid scoring
│   ├── retrieval.py        # ChromaDB + query_multi pipeline
│   ├── query_expansion.py  # 20-group financial synonym expansion
│   ├── rag.py              # RAG orchestrator (retrieve -> generate)
│   ├── llm.py              # 3-backend LLM client (llama.cpp/Anthropic/OpenAI)
│   ├── embedding.py        # nomic-embed wrapper with prefixing
│   ├── chunking.py         # Structure-aware recursive chunking
│   ├── ingest.py           # SEC EDGAR fetcher + MD&A extraction
│   ├── build_index.py      # E2E pipeline: fetch -> chunk -> embed -> store
│   ├── eval_recall.py      # Retrieval recall@k evaluation
│   ├── eval_llm.py         # LLM output generation + caching
│   └── eval_faithfulness.py # LLM-as-judge faithfulness evaluation
├── data/
│   ├── eval_questions.json    # 20 ground-truth eval questions
│   ├── llm_outputs.json       # Cached LLM outputs
│   └── faithfulness_results.json # Automated faithfulness eval results
├── tests.py                # 7 pytest tests
└── readme.md               # This file
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

## TODO / Future Work

- [ ] Cross-encoder on GPU (install torch with CUDA)
- [ ] Improve table-heavy chunk embedding (restaurant counts, segment tables)
- [ ] More tickers / industries
