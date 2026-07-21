# Blog Post Draft — "Building a Multi-Sector RAG Pipeline with 79.5% Weighted Faithfulness"

## Metadata

| Field | Value |
|-------|-------|
| **Title** | Building a Multi-Sector RAG Pipeline That Actually Generalizes — 79.5% Faithfulness on 7 Companies, 4 Sectors |
| **Subtitle** | Prompt fixes, structured output, and the 71% error I almost missed |
| **Platform** | Medium + dev.to |
| **Audience** | ML engineers, data scientists, finance AI practitioners |
| **Est. read time** | 8-10 minutes |

---

## Final Draft

**Hook**

> "71% of the errors in my financial RAG system came from one source: the LLM couldn't tell which fiscal year a number belonged to."

I ran a systematic error classification on my pipeline. Claude evaluated every generated claim. The finding: correctly retrieved numbers were attached to the wrong time period in 71% of failures. The LLM saw "revenue $10B" and "FY2024" in the same context window — but couldn't reliably pair them.

That single error class was the difference between a demo and a portfolio project.

**The Error That Changed Everything**

I built a RAG system to answer financial questions from SEC filings — specifically Management's Discussion & Analysis (MD&A) sections. The goal: turn a 4-hour manual variance analysis into a 3-minute query with traceable citations.

The error analysis revealed three patterns:

| Error Mode | Frequency | Example |
|------------|-----------|---------|
| Period Cross-Contamination | 71% | Source: "FY2024 revenue = $10B, FY2023 = $9B" → LLM: "revenue increased to $10B in FY2023" |
| Metric Conflation | 12% | Source: "comparable store sales +5%" → LLM: "total revenue +5%" |
| Number Transposition | 8% | Source: "0.6%" → LLM: "6%" |

The most surprising finding: 71% of errors weren't about hallucination or missing data. They were about correctly retrieved numbers attached to the wrong context. The model understood the numbers — it just couldn't consistently bind them to their fiscal periods.

**The Fix: Three Layers of Intervention**

Prompting alone wasn't enough. The fix required three layers:

**Layer 1 — Prompt rules.** Four rules became the backbone of the system prompt:

1. EXACT METRIC NAMES: "comparable store sales" ≠ "total revenue"
2. PERIOD INTEGRITY: Every number must cite its fiscal period
3. VERIFY DIRECTION: If source says "increased from 25% to 26%", don't write "decreased to 25%"
4. USE WHAT YOU HAVE: If data is missing, say so — don't fill gaps

**Layer 2 — Retrieval fixes.** The cross-encoder re-ranker added +0.28 recall@10 — the single biggest retrieval gain. Cases like "CMG G&A expenses" went from rank 17 to rank 1. Four questions that previously returned zero relevant chunks were fully recovered.

**Layer 3 — Model swap.** The original pipeline used Qwen2.5-VL-7B — a vision variant wasting parameter budget on image encoders. Swapping to Qwen2.5-7B-Instruct (text-only) added +4.5pp faithfulness, unlocking the full 7B capacity for text reasoning.

**Architecture & Ablation**

The pipeline evolved through systematic ablation — each component measured independently:

| Pipeline | recall@10 | MRR |
|----------|-----------|-----|
| Baseline (dense only) | 0.51 | 0.272 |
| + Query Expansion | 0.45 | 0.330 |
| + Hybrid (BM25 + RRF) | 0.47 | 0.347 |
| + Cross-Encoder | 0.75 | 0.486 |
| + Index rebuild (chunk fix) | 0.81 | 0.540 |
| Full Pipeline | 0.81 | 0.540 |

The cross-encoder was dominant — recall@10 jumped from 0.47 → 0.75. It lifted recall@1 from 0.14 → 0.23 (+64%).

**End-to-end faithfulness progression (restaurant, 20 questions):**

| Phase | Intervention | Strict |
|-------|-------------|--------|
| Baseline | After initial prompt fixes | 65.8% |
| Phase 1 | Metric + number transposition + causal proximity fixes | 69.6% |
| Model swap | VL → non-VL | 74.24% |
| Total | | +8.44pp |

**From 3 Restaurants to 4 Sectors**

The original pipeline covered 3 restaurant chains (CMG, DRI, CBRL). The stress test: add Walmart and Target (retail), Johnson & Johnson (healthcare), ExxonMobil (energy) — 56 filings, 1079 chunks.

Midway through I hit a wall: recall@10 stuck at 0.75 with 4 questions returning zero relevant chunks. Root cause: chunk boundary drift. Each index rebuild shifted chunk IDs in ChromaDB — evaluation questions pointed at stale golden IDs. Fix: rebuilt the 4 stale mappings.

**Cross-sector results:**

| Metric | Restaurant | Cross-Sector |
|--------|-----------|--------------|
| recall@10 | 0.85 | 0.81 |
| MRR | 0.58 | 0.54 |
| Faithfulness (strict) | 74.24% | **68.85%** |
| Faithfulness (weighted) | 75.32% | **79.51%** |

Retail recall held at 1.00 for both WMT and TGT — zero degradation. The weighted score (79.51%) shows the model gets direction and magnitude right even when exact numbers aren't perfect.

Three targeted fixes drove the cross-sector improvement from 59.29% → 68.85% strict (+9.56pp):

1. Number transposition — verify_answer() catches decimal shifts & year mismatches
2. Metric conflation — cross-checks labels against source metadata
3. Prompt engineering — 3 new rules: omission guard, self-verify, citation format
4. Verify-scoring cleanup — LLM verification no longer appends warning text to answer

The pipeline is consumable through 4 surfaces:

| Surface | Tech |
|---------|------|
| Streamlit UI | app.py — visual dashboard |
| MCP Server | FastMCP — Claude Code, Cursor, Cline |
| REST API | FastAPI + Swagger |
| Agent Skills | opencode skill — AI coding agents |

Every error path is covered — retry with backoff, timeout (120s), input validation, rate limiting, graceful degradation. All verified with 111 pytest tests, ruff (0), mypy (0), bandit (0). CI gate at 65% coverage.

**What's Next: Targeting 80%+ Faithfulness**

The 7B model has a ceiling, but there's room to push past it with three research-backed techniques:

**1. Structured output (Pydantic grounding).** Define a schema: answer + decomposed claims + verbatim supporting quotes + explicit "can't answer" channel. Force the LLM into the schema via structured output APIs. Validate every quote is a substring of the retrieved context. Early research shows this closes most hallucination surfaces by construction.

**2. Claim decomposition + NLI verification.** Decompose each answer into atomic claims, then verify each claim independently against source chunks using a Natural Language Inference model (DeBERTa-v3). FinGround (arXiv 2604.23588) reduced hallucination rates by 78% using this pattern in financial QA.

**3. Program-of-Thought for arithmetic.** 38.8% of financial QA errors are arithmetic. FinAgent-RAG (arXiv 2605.05409) eliminates 88% of them by generating executable Python code instead of relying on LLM mental math. The model writes the code; a sandboxed interpreter runs it.

Current codebase: 111 tests, 65% coverage, deterministic seed=42 evaluations, cross-validated against Claude.

**Key Lessons**

1. Classify errors before fixing them. Period cross-contamination was 71% of errors. Optimizing for overall accuracy would have fixed the wrong thing.
2. Chunk boundaries are a silent killer. Every index rebuild can invalidate golden chunk IDs. Use chunk-content matching, not ID pinning.
3. Ablation proves what works. Cross-encoder added +0.28 recall — no amount of prompt engineering could replace that.
4. Local-first matters. Qwen2.5-7B entirely on-device via llama.cpp — no API costs, 120s timeout, swappable to OpenAI/Anthropic via .env toggle.
5. MCP is the new standard. Exposing RAG via MCP matters as much as the pipeline itself.

**Code & Resources**

- GitHub: https://github.com/redsandr/rag-variance-explainer
- Live demo: https://rag-variance-explainer.vercel.app
- MCP: python src/server.py (stdio) or --sse (HTTP)

**Call to Action**

Clone the repo. Pick a ticker (CMG for restaurant, WMT for retail, JNJ for healthcare, XOM for energy). Ask "How did revenue change?" The answer comes back with citations from actual SEC filings — no API key required.
