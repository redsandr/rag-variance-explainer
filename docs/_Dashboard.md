---
tags: [rag-project, dbs-portfolio, moc, index]
status: active
---

# RAG Variance Explainer — Dashboard

**North star:** Multi-sektor RAG platform dengan faithfulness 75%+ → evolusi jadi AI-native platform (MCP + REST + SDK).

---

## Vault Structure

```
Project 2/
├── _Dashboard.md                     ← Kamu di sini
├── _analysis/                        ← Analisis & blueprint
│   └── 09. Improvement Blueprint    ← Dari 7 trending repos
├── _planning/                        ← Roadmap & execution
│   ├── 00. RAG Project Plan         ← Problem validation, tech stack
│   ├── 01. RAG Roadmap              ← Phases 0–3 original
│   ├── 07. Roadmap & Execution Plan ← Primary execution doc
│   ├── 07b. Expansion & Roadmap 2.0 ← Expansion roadmap
│   └── 08. Priority Execution Plan  ← Priority-based tasks
└── _technical/                       ← Dokumentasi teknis
    ├── 02. Progress & Technical Doc ← Single source of truth
    ├── 03. Faithfulness Eval        ← Iterasi 3–6 history
    ├── 04. Prompt Engineering       ← Iterasi 8 prompt fixes
    ├── 05. Turn Weaknesses → Strength← Action plan
    └── 06. Cleanup & Security       ← Code quality, security
```

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Retrieval MRR | **0.54** |
| recall@10 | **0.81** |
| Faithfulness (strict) | **59.29%** (cross-sector) / **74.24%** (restaurant) |
| Faithfulness (weighted) | **73.45%** (cross-sector) / **75.32%** (restaurant) |
| Judge parse errors | **0** ✅ |
| Phase 2b — Code Lockdown | ✅ Complete |
| Phase 2b.8 — Dataset | ✅ Complete (JNJ+XOM, 1079 chunks) |
| Phase 2b.9 — GitHub Profile Polish | ✅ Complete (redesigned profile, landing page) |
| Phase 2b.10 — Error Handling Lockdown | ✅ Complete (42 tests, LLM retry tests, manual verification) |
| Companies | **7** (CMG, DRI, CBRL, WMT, TGT, JNJ, XOM) — 4 sectors |
| Chunks | **1079** dari **56** filings |
| Tests | **42** pytest + ruff (0) + mypy (0) + bandit (0) |
| CI | pytest --cov-fail-under=30 + mypy + ruff + bandit |
| Coverage | ~44% |
| Code quality | ruff (0) + mypy (0) + bandit (0) — pre-commit hooks |
| Model | Qwen2.5-7B-Instruct Q4_K.M (llama.cpp, 120s timeout) |
| Landing page | Next.js 14 + Tailwind, Vercel: [rag-variance-explainer.vercel.app](https://rag-variance-explainer.vercel.app) |

---

## File Index

### Planning (`_planning/`)

| # | File | Isi | Status |
|---|------|-----|--------|
| 00 | [[_planning/00. RAG Project Plan\|Project Plan]] | Problem validation, use cases, tech stack decisions | ✅ |
| 01 | [[_planning/01. RAG Roadmap\|Roadmap]] | Phases 0–3, per-eval breakdown, success metrics | ✅ |
| 07 | [[_planning/07. Roadmap & Execution Plan\|Roadmap & Execution]] | **Primary execution doc** — merged roadmap, multi-role breakdown | ✅ |
| 07b | [[_planning/07b. Expansion & Roadmap 2.0\|Expansion V2]] | Faithfulness fix → Retail → Benchmark → Blog | 🟡 |
| 08 | [[_planning/08. Priority Execution Plan\|Priority Plan]] | Priority-based tasks, due dates, role assignments | 🟡 |

### Technical (`_technical/`)

| # | File | Isi | Status |
|---|------|-----|--------|
| 02 | [[_technical/02. Progress & Technical Documentation\|Technical Docs]] | **Single source of truth** — arsitektur, eval results, refactoring history | ✅ |
| 03 | [[_technical/03. Faithfulness Eval — Iterasi 3\|Faithfulness Eval]] | Iterasi 3–6: fixes, results, failure analysis | ✅ |
| 04 | [[_technical/04. Prompt Engineering & Evaluation Fixes\|Prompt Engineering]] | Iterasi 8: prompt fixes, LLM reset, 4 broken evals | ✅ |
| 05 | [[_technical/05. Turn Weaknesses Into Strengths\|Weaknesses → Strengths]] | Rencana aksi: scaling, deployment, exposure, testing | 🟡 |
| 06 | [[_technical/06. Professional Cleanup & Security Audit\|Cleanup & Security]] | Code quality fixes, git history sanitization, config sync | ✅ |

### Analysis (`_analysis/`)

| # | File | Isi | Status |
|---|------|-----|--------|
| 09 | [[_analysis/09. Improvement Blueprint from Trending Repos\|Improvement Blueprint]] | **NEW** — Analisis 7 trending repos, gap analysis, implementation roadmap | ✅ |

---

## Quick Navigation

```
Cari teknis detail?       → _technical/02. Progress & Technical Documentation
Cari apa yang harus dikerjain? → _planning/07. Roadmap & Execution Plan
Cari history eval?        → _technical/03. Faithfulness Eval
Cari prompt fixes?        → _technical/04. Prompt Engineering
Cari improvement plan?    → _analysis/09. Improvement Blueprint
Bingung mulai dari mana?  → _Dashboard.md (ini)
```

---

## State Project

| Aspek | Detail |
|-------|--------|
| **North star** | Multi-sektor RAG platform → AI-native RAG platform (MCP + REST + SDK) |
| **Tahap** | Phase 2b — Code Lockdown ✅ Complete. Phase 2b.8-10 — Dataset + Polish + Error Handling ✅. Next: **Phase A — Surface Strategy** (MCP + REST API) |
| **Faithfulness** | Restaurant: **74.24% strict / 75.32% weighted**. Cross-sector (40q): **59.29% strict / 73.45% weighted** |
| **Perusahaan** | **7** (CMG, DRI, CBRL, WMT, TGT, JNJ, XOM) — 4 sectors |
| **Retail recall** | **WMT recall@10 = 1.00**, **TGT recall@10 = 1.00** — zero degradation |
| **Overall recall** | **recall@10 = 0.81**, **MRR = 0.54** — 0 retrieval gaps |
| **Code quality** | ruff (0) + mypy (0) + bandit (0) — 42 tests ✅ |
| **Target berikut** | 🔴 MCP Server (Priority #1) → REST API → Agent Skills → Docker → Blog + Deploy |

---

## Lihat Juga

- [GitHub Repo](https://github.com/redsandr/rag-variance-explainer) — source code
- [[readme|README]] (root repo) — overview, setup, architecture
