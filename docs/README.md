# RAG Variance Explainer — Documentation

Extended documentation for the project, covering problem validation, architecture decisions, evaluation iterations, and technical notes.

> **Mulai dari sini → [`_Dashboard.md`](_Dashboard.md)**

| File | Description |
|------|-------------|
| `00. RAG Project Plan.md` | Project scope, problem statement validated against real job listings |
| `01. RAG Roadmap.md` | Development phases and milestones |
| `02. Progress & Technical Documentation.md` | Comprehensive docs: architecture, eval results, refactoring history (Phase 1–7, retail expansion) |
| `03. Faithfulness Eval — Iterasi 3.md` | Faithfulness evaluation methodology and results |
| `04. Prompt Engineering & Evaluation Fixes.md` | Prompt engineering iterations and calibration |
| `05. Turn Weaknesses Into Strengths.md` | Action plan: scaling, deployment, community outreach, user testing (superseded by 07) |
| `07. Roadmap & Execution Plan.md` | **Primary execution doc** — merged roadmap + detailed multi-role execution plan, sequential steps from Phases 1-4 with role discussions |
| `_Dashboard.md` | **Start here** — MOC/index with links to all files + quick stats |

---

## Quick Links

- **README** (root): project overview, setup, architecture
- **Tests**: `tests.py` + `conftest.py` — **38 tests** (LLM backend, singleton, reset, rerank, build_index, chunking, retrieval helpers, prompt builders, RRF merge) + auto-mock fixture prevents real LLM calls
- **Scripts**: `scripts/update_readme_stats.py` — auto-generate corpus stats from ChromaDB
- **Pre-commit**: `.pre-commit-config.yaml` — ruff + mypy auto-run on commit
- **CI**: pytest + coverage (`--cov-fail-under=65`), mypy (0 errors), ruff (0 errors), bandit (0 issues)
- **CI**: `.github/workflows/test.yml` — pytest on push/PR
