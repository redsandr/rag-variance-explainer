---
tags: [rag-project, dbs-portfolio, moc, index]
status: active
---

# RAG Variance Explainer — Dashboard

**North star:** Turn 4-hour manual variance analysis into 3-minute query with traceable sources.

---

## Files

| # | File | Isi | Status |
|---|------|-----|--------|
| 00 | [Project Plan](00.%20RAG%20Project%20Plan.md) | Problem validation, use cases, tech stack decisions, pipeline status | ✅ |
| 01 | [Roadmap](01.%20RAG%20Roadmap.md) | Phases 0–3, per-eval breakdown (20 questions), success metrics | ✅ |
| 02 | [Technical Docs](02.%20Progress%20%26%20Technical%20Documentation.md) | **Single source of truth** — arsitektur, evaluasi, refactoring history phases 1–7g | ✅ |
| 03 | [Faithfulness Eval Iterasi](03.%20Faithfulness%20Eval%20%E2%80%94%20Iterasi%203.md) | Iterasi 3–6 faithfulness evaluation: fixes, results, failure analysis | ✅ |
| 04 | [Prompt Engineering](04.%20Prompt%20Engineering%20%26%20Evaluation%20Fixes.md) | Iterasi 8 prompt fixes, LLM reset, 4 broken evals analysis | ✅ |
| 05 | [Turn Weaknesses → Strengths](05.%20Turn%20Weaknesses%20Into%20Strengths.md) | Rencana aksi: scaling, deployment, exposure, user testing (superseded by 07) | 🟡 |
| 07 | [Roadmap & Execution Plan](07.%20Roadmap%20%26%20Execution%20Plan.md) | **Primary execution doc** — merged roadmap + multi-role breakdown | ✅ |
| 07b | [Expansion & Roadmap V2](07.%20Expansion%20%26%20Roadmap%202.0.md) | Faithfulness fix → Retail expansion → Benchmark & Blog | 🟡 |
| 08 | [Priority Plan](08.%20Priority%20Execution%20Plan.md) | Priority-based execution, due dates, role assignments | 🟡 |

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Retrieval MRR | **0.66** (+28% baseline) |
| recall@10 | **0.70** |
| Faithfulness (strict) | **64.56%** (Iterasi 11d) / **74.8%** (Claude) |
| Faithfulness (weighted) | **75.32%** ✅ (above target) |
| Judge parse errors | **0** ✅ |
| Phase 1 | ✅ Complete (merged to master) |
| Phase 2 — Retail Expansion | 🟡 In Progress (WMT + TGT) |
| Companies | 5 (CMG, DRI, CBRL, WMT, TGT) |
| Chunks | **740** from 40 filings |
| Tests | 32 pytest |
| Model | Qwen2.5-7B-Instruct Q4_K_M (llama.cpp) |

> Detail metrics → [Technical Docs → Evaluation Results](02.%20Progress%20%26%20Technical%20Documentation.md#Evaluation%20Results).

---

## Alur Navigasi

```
[Problem] ──→ 00. Project Plan
                  │
                  ▼
         01. Roadmap ──→ 02. Technical Docs (execution)
                  │               │
                  ▼               ▼
         03. Faithfulness    04. Prompt Engineering
                  │               │
                  ▼               ▼
         05. Turn Weaknesses Into Strengths ──→ [Next Actions]
```

---

## Referensi Eksternal

- [README](../readme.md) (root) — project overview, setup, architecture badges
- [GitHub Repo](https://github.com/redsandr/rag-variance-explainer)
