# RAG Variance Explainer — Documentation

Extended documentation for the project, covering problem validation, architecture decisions, evaluation iterations, and technical notes.

> **Mulai dari sini → [`_Dashboard.md`](_Dashboard.md)**

---

## Vault Structure

Obsidian vault at `C:\Users\Lenovo\Documents\portofolio 2\Project 2\`:

```
Project 2/
├── _Dashboard.md                          ← Index semua docs
├── _analysis/
│   └── 09. Improvement Blueprint          ← Trending repo analysis
├── _planning/
│   ├── 00. RAG Project Plan.md
│   ├── 01. RAG Roadmap.md
│   ├── 07. Roadmap & Execution Plan.md
│   ├── 07b. Expansion & Roadmap 2.0.md
│   └── 08. Priority Execution Plan.md
└── _technical/
    ├── 02. Progress & Technical Documentation.md
    ├── 03. Faithfulness Eval — Iterasi 3.md
    ├── 04. Prompt Engineering & Evaluation Fixes.md
    ├── 05. Turn Weaknesses Into Strengths.md
    └── 06. Professional Cleanup & Security Audit.md
```

---

## File Index

| # | File | Description |
|---|------|-------------|
| 00 | `00. RAG Project Plan.md` | Project scope, problem statement validated against real job listings |
| 01 | `01. RAG Roadmap.md` | Development phases and milestones |
| 02 | `02. Progress & Technical Documentation.md` | Comprehensive docs: architecture, eval results, refactoring history |
| 03 | `03. Faithfulness Eval — Iterasi 3.md` | Faithfulness evaluation methodology and results |
| 04 | `04. Prompt Engineering & Evaluation Fixes.md` | Prompt engineering iterations and calibration |
| 05 | `05. Turn Weaknesses Into Strengths.md` | Action plan: scaling, deployment, community outreach |
| 06 | `06. Professional Cleanup & Security Audit.md` | Security fixes, git history sanitization |
| 07 | `07. Roadmap & Execution Plan.md` | **Primary execution doc** — multi-role breakdown |
| 07b | `07b. Expansion & Roadmap 2.0.md` | Expansion roadmap (supersedes 05) |
| 08 | `08. Priority Execution Plan.md` | Priority-based execution, due dates |
| **09** | **`09. Improvement Blueprint from Trending Repos.md`** | **NEW** — 7 trending repo analysis + RVE gap analysis |

---

## Quick Links

| Link | Description |
|------|-------------|
| **README** (root) | Project overview, setup, architecture badges |
| **`_Dashboard.md`** | **Start here** — MOC/index with links + quick stats |
| `09. Improvement Blueprint from Trending Repos.md` | **NEW** — MCP, REST API, Agent Skills, Docker, multi-engine blueprint |
| `02. Progress & Technical Documentation.md` | Single source of truth teknis |
| `07. Roadmap & Execution Plan.md` | Primary execution document |

### Code Quality

- **Tests**: `tests.py` + `conftest.py` — **42 tests** (LLM backend, singleton, reset, rerank, build_index, chunking, retrieval, prompts, RRF merge, sanitize, retry decorator) + auto-mock fixture prevents real LLM calls
- **Pre-commit**: `.pre-commit-config.yaml` — ruff + mypy auto-run on commit
- **CI**: pytest + coverage, mypy (0 errors), ruff (0 errors), bandit (0 issues)
- **Scripts**: `scripts/update_readme_stats.py` — auto-generate corpus stats from ChromaDB
