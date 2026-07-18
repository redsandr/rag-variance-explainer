---
tags: [rag-project, dbs-portfolio, moc, index]
status: active
---

# RAG Variance Explainer — Dashboard

**North star:** Turn 4-hour manual variance analysis into 3-minute query with traceable sources.

---

## File Index

| # | File | Isi | Status |
|---|------|-----|--------|
| 00 | [[00. RAG Project Plan\|Project Plan]] | Problem validation, use cases, tech stack decisions, pipeline status | ✅ |
| 01 | [[01. RAG Roadmap\|Roadmap]] | Phases 0–3, per-eval breakdown (20 questions), success metrics | ✅ |
| 02 | [[02. Progress & Technical Documentation\|Technical Docs]] | **Single source of truth** — arsitektur, evaluasi, refactoring history | ✅ |
| 03 | [[03. Faithfulness Eval — Iterasi 3\|Faithfulness Eval]] | Iterasi 3–6: fixes, results, failure analysis | ✅ |
| 04 | [[04. Prompt Engineering & Evaluation Fixes\|Prompt Engineering]] | Iterasi 8: prompt fixes, LLM reset, 4 broken evals | ✅ |
| 05 | [[05. Turn Weaknesses Into Strengths\|Weaknesses → Strengths]] | Rencana aksi: scaling, deployment, exposure, testing | 🟡 |
| 06 | [[06. Professional Cleanup & Security Audit\|Cleanup & Security]] | Code quality fixes, git history sanitization, HF token revoke, config sync | ✅ |
| 07 | [[07. Roadmap & Execution Plan\|Roadmap & Execution Plan]] | **Primary execution doc** — merged roadmap, multi-role breakdown, sequential steps | ✅ |
| 07b | [[07. Expansion & Roadmap 2.0\|Expansion & Roadmap V2]] | Faithfulness fix → Retail expansion → Benchmark & Blog | 🟡 |
| 08 | [[08. Priority Execution Plan\|Priority Plan]] | Priority-based execution, due dates, role assignments | 🟡 |

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
| Phase 2 — Retail Expansion | ✅ Complete |
| Phase 2b — Code Lockdown | ✅ Complete (ruff + mypy tooling, 59 lint fixes, app.py updated) |
| Companies | 5 (CMG, DRI, CBRL, WMT, TGT) |
| Chunks | 740 dari 40 filings |
| Tests | 32 pytest + ruff + mypy |
| Model | Qwen2.5-7B-Instruct Q4_K.M (llama.cpp) |

> Detail metrics → [[02. Progress & Technical Documentation#Evaluation Results]]

---

## Navigasi

```
00. Project Plan
      │
      ▼
01. Roadmap ──→ 02. Technical Docs
      │               │
      ▼               ▼
03. Faithfulness   04. Prompt Engineering
      │               │
      ▼               ▼
05. Turn Weaknesses Into Strengths
```

---

## Referensi

- [[readme|README]] (root repo) — overview, setup, architecture
- [GitHub Repo](https://github.com/redsandr/rag-variance-explainer) — source code
