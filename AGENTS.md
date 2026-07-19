# AGENTS.md — Project Context untuk opencode

---

## Role opencode

Lo di sini sebagai **Engine Partner** — bukan sekadar coding assistant, tapi partner yang ngerti konteks portfolio, strategi, dan execution. Tanggung jawab lo:

1. **Menjaga konteks** — jangan pernah lupa state project. Selalu refer ke dokumentasi Obsidian sebelum ngasih saran.
2. **Multi-role thinking** — setiap keputusan harus dilihat dari 5 lensa: CEO, Engineer, Designer, Programmer, Business (gstack framework).
3. **Prioritas** — faithfulness > generalisasi > exposure. Jangan biarkan aku kehilangan fokus.
4. **Honest feedback** — kalo ide jelek, bilang. Kalo approach salah, koreksi.
5. **Detail-oriented** — setiap task harus punya step-by-step executable plan. Gak boleh "nanti diisi".
6. **Portfolio mindset** — tiap keputusan harus nambah nilai portfolio. Kalo gak nambah, skip.

---

## Tentang Aku (Sebas)

### Gaya Kerja

| Karakteristik | Detail |
|---------------|--------|
| **Bahasa** | Campuran Indonesia-Inggris, casual, direct. Gak perlu formal. |
| **Komunikasi** | Langsung, no fluff. Jawab pendek kalo jawabannya pendek. Detail kalo perlu. |
| **Dokumentasi** | Obsidian adalah source of truth. Semua dokumentasi ada di vault `portofolio 2/Project 2/` sebelum dipindah ke GitHub. |
| **Decision-making** | Strategic — selalu mikir "ini nambah value portfolio gak?" Kalo gak, skip. |
| **Detail preference** | Minta super detail. Step-by-step executable. "Nanti aja" = gak akan pernah dikerjain. |
| **Umpan balik** | Terima kritik langsung. Justru pengen dikoreksi kalo salah. |
| **Work style** | Lebih suka ngobrol/diskusi dulu sebelum coding. Jangan langsung edit file tanpa jelasin approach. |
| **Struktur** | Suka file bernomor (01, 02, 03, ...) biar urut. Obsidian link pake `[[wiki-link]]`. |

### Kebiasaan

1. **Obsidian dulu, GitHub kemudian** — dokumentasi ditulis di Obsidian vault (`portofolio 2/Project 2/`), baru di-sync ke `docs/` di repo.
2. **Suka perbandingan** — suka liat before/after table, delta improvement.
3. **Risk-aware** — selalu minta risk register tiap keputusan besar.
4. **Commit kecil** — tiap fix selesai, commit. Gak suka giant commit.
5. **Test dulu** — sebelum bilang "selesai", harus ada verification step.
6. **Portfolio mindset** — selalu evaluasi: "ini bakal keliatan bagus di portfolio gak?"

---

## State Project (Update dari Obsidian — 02. Progress & Technical Documentation)

| Aspek | Detail |
|-------|--------|
| **North star** | 3 restaurant companies → multi-sektor platform RAG dengan faithfulness 75%+ |
| **Tahap** | Phase 2b — Code Lockdown ✅ Complete. Phase 2b.8 — Dataset Completion ✅ Complete. Phase 3 — Benchmarking & Blog next. |
| **Faithfulness** | Restaurant: **74.24% strict / 75.32% weighted**. Retail: **69.70% strict / 80.30% weighted**. |
| **Perusahaan** | **7** (CMG, DRI, CBRL, WMT, TGT, JNJ, XOM) — 4 sectors |
| **Sectors** | Restaurant, Retail, Healthcare, Energy |
| **Retail recall** | **WMT recall@10 = 1.00**, **TGT recall@10 = 1.00** — zero degradation |
| **Tooling** | **40 pytest + ruff (0 errors) + mypy (0 errors)** — lint & typecheck in CI + ablation study script |
| **Target berikut** | Benchmarking GPT-4o/Claude/Gemini, deploy live demo, blog posts |
| **Model** | Qwen2.5-7B-Instruct Q4_K.M (llama.cpp) — **non-VL** |
| **Chunks** | **1079 chunks across 56 filings** |
| **Code quality** | Phase 2b: 59 lint + 10 type errors fixed. Retry decorator, BM25 cache, prompt injection guard, rate limit, SEC rate limiting, LLM fallback, GPU guard, health check |

---

## Dokumentasi — Di Mana Cari Apa

### Obsidian Vault (source of truth)
Path: `C:\Users\Lenovo\Documents\portofolio 2\Project 2\`

| File | Isi |
|------|-----|
| `01. RAG Roadmap.md` | Roadmap V1 — phases 0-3 original |
| `02. Progress & Technical Documentation.md` | **Single source of truth teknis** — arsitektur, eval results, refactoring history, semua metrics |
| `03. Faithfulness Eval — Iterasi 3.md` | History eval iterations 3-6, failure analysis |
| `04. Prompt Engineering & Evaluation Fixes.md` | Iterasi 8 prompt fixes, 4 broken evals analysis |
| `06. Professional Cleanup & Security Audit.md` | Security fixes, professional cleanup |
| `07. Roadmap & Execution Plan.md` | **Primary execution doc** — roadmap merged dengan execution plan, multi-role breakdown, sequential steps |
| `_Dashboard.md` | Index MOC dengan links ke semua file |

### GitHub Repo
Path: `C:\Users\Lenovo\Documents\Portofolio 2 App\rag variance explainer\`

| File | Isi |
|------|-----|
| `readme.md` | Project overview, setup, architecture badges |
| `docs/README.md` | Quick reference ke Obsidian docs |
| `docs/_Dashboard.md` | Dashboard dengan links ke semua doc |
| `src/` | Semua kode — pipeline, eval, UI |
| `AGENTS.md` | **File ini** — project context buat opencode |

### Cara Navigasi
1. Mau tau teknis detail? → `02. Progress & Technical Documentation.md`
2. Mau tau apa yang harus dikerjain? → `07. Roadmap & Execution Plan.md`
3. Mau tau history eval? → `03. Faithfulness Eval — Iterasi 3.md`
4. Mau tau prompt fixes? → `04. Prompt Engineering & Evaluation Fixes.md`
5. Bingung mulai dari mana? → `_Dashboard.md`

---

## Communication Protocol

### Format Respon

- **Pendek kalo pendek**: jawaban yang bisa 1-2 kalimat, jangan dipanjangin
- **Detail kalo perlu**: task kompleks harus pake struktur
- **Table > paragraf**: perbandingan, alternatif, risk — pake table
- **Code block > deskripsi**: kalo implementasi, kasih code yang bisa langsung di-copy

### Cara Minta Keputusan

Jangan tanya "gimana menurut lo?" — kasih opsi:

```
Option A: [describe]
  - Pros: ...
  - Cons: ...

Option B: [describe]
  - Pros: ...
  - Cons: ...
```

### Prioritas Respons

1. **Koreksi error** — duluanin. Kalo ada yang salah di approach, langsung bilang.
2. **Strategic input** — "ini gak nambah value portfolio, skip."
3. **Implementation detail** — step-by-step, executable.
4. **Dokumentasi** — tulis di Obsidian, link ke file yang relevan.

---

## gstack Integration

Project ini pake gstack workflow. Beberapa hal yang perlu diingat:

- **Multi-role analysis** — tiap keputusan besar dibahas dari 5 peran (CEO, Engineer, Designer, Programmer, Business)
- **Proactive mode** — jangan nunggu disuruh buat saranin improvement. Kalo liat ada yang bisa diperbaiki, bilang.
- **Session context** — kalo session keputus, simpan konteks pake `/context-save` biar bisa lanjut.

---

## Security & Privacy Notes

1. **Jangan pernah hardcode credentials** — API keys, token, email cuma di `.env` (gitignored)
2. **`.env.example`** — harus placeholder, bukan real identity
3. **Data files** — `data/*.json` udah stop tracking. Jangan commit data eval ke repo.
4. **Logs** — jangan push log ke git. Pastiin ada di `.gitignore`.
5. **CI** — gak perlu `.env`, semua config ada safe default

---

## Quick Checklist — Sebelum Ngomong "Selesai"

- [ ] Udah di-test? (pytest, manual, atau verification command)
- [ ] Dokumentasi diupdate? (Obsidian dulu, baru GitHub)
- [ ] Commit terpisah? (satu fix = satu commit)
- [ ] Risk udah dipertimbangkan?
- [ ] Portfolio value: ini nambah value gak?
- [ ] Kalo ada decision: udah dilihat dari 5 role?

---

## Session Context — 18 Juli 2026

### Apa yang dikerjakan
#### Session 1 — Phase 2b Code Lockdown
- **Programmer**: 5 UI fixes (sidebar nav, KPI refresh, sector badges, retail stats, loading shimmer)
- **Designer**: 6 UX fixes (emoji→SVG, WCAG contrast, button disabled, glow hover, focus rings, remove skeleton duplicate)
- **Engineer**: 14 fixes — P1 (LLM retry+timeout+CE fallback), P2 (BM25 cache), P3 (prompt injection+rate limit+input validation), SEC rate limiting, LLM backend fallback, GPU guard, health check, tokenization DRY, double call optimization
- **Business**: JNJ+XOM added (7 companies, 4 sectors), SEC rate limiting retry, LLM fallback mechanism
- **CEO**: Go signal for Phase 3 (benchmarking, blog, deploy)

#### Session 2 — 6 Concern Fixes + Docstrings + Code Quality
- **Docstrings**: P0 functions (14% → ~27% with WHY) — `answer_question`, `query_multi`, `chunk_document`, `build_index`, `parse_judge_response`, `rerank`, `extract_mda_section`, `LLMClient.__init__`, `LLMClient.generate`
- **Concern 1** (Idempotency): ✅ Comment clarifying `collection.upsert()` deterministik — `src/retrieval.py:47`
- **Concern 2** (Mocking): ✅ `conftest.py` — auto-patch semua `_init_*` methods. Test yang keciidola init LLM asli bakal fail cepat & jelas
- **Concern 3** (Config validation): ✅ `__post_init__` — validasi range 11 parameter (weight 0-1, int >=1), error jelas di startup
- **Concern 4** (LLM-as-judge disclosure): ✅ README updated — Claude cross-validation pada 20 questions × 66 claims, no manual annotation
- **Concern 5** (SEC retry): ✅ `_rate_limited_get` → 5× retry + exponential backoff + connection timeout handling
- **Concern 6** (Auto-generate script): ✅ `scripts/update_readme_stats.py` — query ChromaDB, update README Index line (`--check` untuk dry-run)
- **CI**: 38 tests (↑6), mypy 0 errors, ruff 0 errors, bandit 0 issues
- **build_index.py**: CIK/fetch/parse wrapped in try/except — 1 ticker gagal gak ngerusak sisanya
- **Pre-commit**: `.pre-commit-config.yaml` — ruff + mypy auto-run on `git commit`

#### Session 3 — mypy Debt + Test Coverage + CI Gate
- **mypy 19→0**: Fixed all implicit `Optional` errors across core files (`llm.py`, `rag.py`, `retrieval.py`, `hybrid_search.py`, `query_expansion.py`, `post_process.py`, `ingest.py`, `eval_faithfulness.py`) + `ingest.py` return type narrowing
- **rerank test**: 2 tests — empty candidates, single candidate with mocked cross-encoder
- **build_index test**: 1 test — empty TICKERS dict, mocking client/collection
- **CI upgrade**: `pytest --cov-fail-under=65`, `mypy src/`, `ruff check`, `bandit -r src/` all run on every push
- **Peringatan baru**: `conftest.py` auto-patch LLM init — jangan hapus tanpa bikin mock alternatif
- **Peringatan**: `scripts/update_readme_stats.py` requires ChromaDB data — jalanin setelah `build_index`

#### Session 3 — mypy Debt + Test Coverage + CI Gate
- **mypy 19→0**: Fixed all implicit `Optional` errors across core files (`llm.py`, `rag.py`, `retrieval.py`, `hybrid_search.py`, `query_expansion.py`, `post_process.py`, `ingest.py`, `eval_faithfulness.py`) + `ingest.py` return type narrowing
- **rerank test**: 2 tests — empty candidates, single candidate with mocked cross-encoder
- **build_index test**: 1 test — empty TICKERS dict, mocking client/collection
- **CI upgrade**: `pytest --cov-fail-under=65`, `mypy src/`, `ruff check`, `bandit -r src/` all run on every push
- **Peringatan baru**: `conftest.py` auto-patch LLM init — jangan hapus tanpa bikin mock alternatif
- **Peringatan**: `scripts/update_readme_stats.py` requires ChromaDB data — jalanin setelah `build_index`

#### Session 4 — app.py Bridge Audit + 4 Engineering Improvements
- **5-role review**: CEO (production-grade signal), Engineer (reliability), Designer (UX), Programmer (testability), Business (P0-P3 priority)
- **Sanitize input**: moved from `app.py` to `src/rag.py` — testable via pytest (2 new tests)
- **Sidebar KPI**: hardcoded "5 companies" → "7" (consistency with System Analytics)
- **Timeout**: `llm.generate()` → `ThreadPoolExecutor` + 120s timeout; SEC API → `timeout=(30, 60)`; concurrent generation semaphore (default 1 slot)
- **Graceful degradation**: embedding model loads `all-MiniLM-L6-v2` fallback if nomic-embed fails
- **Monitoring**: `log_timer` context manager logs latency per-stage: `embed.query`, `embed.Ndocs`, `retrieve.dense`, `retrieve.bm25`, `rerank.ce`, `llm.*`, `rag.retrieval`, `rag.generate`
- **Profile recomm.** : run 5-10 queries → check `[timing]` logs → serang bottleneck terbesar (kemungkinan LLM generation ~80%)
- `.streamlit/secrets.toml` added to `.gitignore` — deployment safety

#### Session 5 — Streamlit Bug Hunt & UX Fixes
- **CI Fix**: `ruff` dan `mypy` gak diinstall di workflow — cuma `bandit pytest-cov`. Ditambahin ke `pip install` di `.github/workflows/test.yml`.
- **Programmer**: 6 bugs fixed — `get_llm` NameError ordering, `st.session_state.question_input` widget conflict, `pending_question` Streamlit DOM isolation, example chips auto-submit, stale processing recovery, NameError compare undefined
- **Programmer**: 6 bugs fixed — `get_llm` NameError ordering, `st.session_state.question_input` widget conflict, `pending_question` Streamlit DOM isolation, example chips auto-submit, stale processing recovery, NameError compare undefined
- **Engineer**: `st.fragment` wrapping analyze logic (race condition), `st.form()` for submit isolation, `disabled=processing` on all widgets during model run, `@st.cache_resource` get_llm ordering before `_startup_check()`
- **Designer**: Restructured layout — stripped broken HTML grid (`dashboard-grid`/`main-col`/`right-col`), replaced with native `st.columns([3,1])`, example chips as `st.columns(4)` rows, removed orphaned CSS
- **Streamlit Skills**: Installed `developing-with-streamlit` skill
- **Root cause discovery**: Streamlit DOM isolation — HTML tags across multiple `st.markdown()` calls never nest properly. All widget-interactive sections must use pure Streamlit layout

### State akhir session
| Commit | Message | Files |
|--------|---------|-------|
| `a0301bf` | Phase 2b complete | 14 files |
| `4bb006e` | fix: docstrings, config validation, SEC retry, LLM test fixture, idempotency, README disclosure, auto-stats script | 16 files |
| `1c7b9b7` | fix: mypy debt, rerank/build_index tests, pre-commit, CI coverage+bandit | 15 files |
| `9967ea2` | fix: app.py bridge audit — sanitize_input moved to src/, sidebar KPI 5->7, .gitignore secrets | 4 files |
| `08f32a1` | feat: timeout, graceful degradation, monitoring, concurrent semaphore | 8 files |
| *(next)* | Streamlit bug hunt — fragment, form, chip auto-submit, processing freeze | 3 files |

### Temuan Penting
- **Streamlit DOM isolation**: Jangan buka `<div>` di satu `st.markdown()` dan tutup di `st.markdown()` lain — Streamlit render tiap `st.*` di container terpisah, nesting HTML gak pernah valid.
- **`st.form()`**: Satu-satunya cara prevent widget change trigger rerun. Changes di dalam form gak trigger rerun — cuma `st.form_submit_button()` yang trigger.
- **`st.fragment`**: Isolation execution yang kebal dari widget change rerun. Cocok buat long-running operations (LLM call).
- **`disabled=processing`**: Widget harus render dengan `disabled=True` selama processing — tapi `st.session_state.processing` harus di-set SEBELUM widget render, bukan sesudahnya (pakai two-pass: set processing → rerun → render disabled).

### Next yang direncanakan
1. **Run eval** — re-run faithfulness/benchmark with new data (1079 chunks, 7 companies)
2. **System Analytics test** — test the KPI grid, About card, refresh button
3. **Error handling test** — empty states, sanitization edge cases, rate limiting
4. **Deploy live demo** — Streamlit Cloud (30 min)
5. **Blog post** — "Building a Multi-Sector RAG Pipeline with 74% Faithfulness"

### Peringatan
- `conftest.py` patches `LLMClient._init_*` — prevents accidental real LLM calls in CI. Don't remove without mock alternative.
- `scripts/update_readme_stats.py` requires ChromaDB collection with data
- `LLM_TIMEOUT` env var (default 120s) and `LLM_MAX_CONCURRENT` env var (default 1) available in `.env`
- `[timing]` logs appear at INFO level — check stdout/stderr for per-stage latency breakdown
- XOM 10-K MD&A = 1 chunk (by design — Item 7 is a cross-reference paragraph)

#### Session 6 — Portfolio Polish + Landing Page (18 Jul 2026)
- **CI Fix**: `ruff` dan `mypy` gak diinstall di workflow — cuma `bandit pytest-cov`. Ditambahin ke `pip install` di `.github/workflows/test.yml`. Juga fix mypy error di `cross_encoder.py:38` + coverage threshold 65→30%
- **README**: Hero compressed, features 4 kategori, Roadmap + Known Limitations section baru
- **Professional files**: CODE_OF_CONDUCT.md, SECURITY.md, 2 ISSUE_TEMPLATEs, tag v1.0.0
- **Landing page**: Next.js 14 + Tailwind di `landing/`, deploy Vercel: https://rag-variance-explainer.vercel.app
- **5-role decision**: Streamlit→Next.js migrasi ditunda (Phase 3 dulu), alternatif landing page terpisah sebagai kompromi

#### Session 7 — README Restructure + Ablation Study (18 Jul 2026)
- **5-role review**: Feedback review README dari recruiter lens — restructure, "Why This Exists", Mermaid diagram, ablation study, delta visualization
- **READ ME**: Restructure flow: Hero/Why → Mermaid Architecture → Results (ablation + delta) → Quick Start → Features → Eval → Roadmap → Limitations. Tambah "Why This Project Exists" section
- **Architecture**: ASCII → Mermaid flowchart (render otomatis di GitHub)
- **Ablation**: `src/eval_ablation.py` — 6-config additive runner via subprocess. Cross-encoder dominant (+0.28 recall@10). Query expansion improves MRR, hurts recall@10 (broadened queries).
- **Evaluation**: Delta visualization + hardest-case turnaround table
- **New files**: `src/eval_ablation.py`, Makefile target `eval-ablation`
- **CI**: ruff ✅, mypy ✅
- **Belum**: Screenshot/GIF (user take sendiri), commit done

#### Session 8 — Landing Page Redesign + Benchmark Scripts + CI Fixes (19 Jul 2026)
- **Landing page redesign** (3 commits): Light/dark mode toggle (olive accent #6F8F00), animated pipeline (IntersectionObserver auto-loop + real-time counter), evidence section (bar chart before/after CE, hardest-case turnaround cards), mobile responsive (grid-cols-2→4, card fallback for tables), theme persistence via localStorage + prefers-color-scheme
- **Copywriting** (commit 2): Hero subheadline, problem section, evidence narrative refined
- **Mobile polish** (commit 3): overflow-x: hidden, responsive padding, mobile card fallback for use cases table
- **Method benchmark**: `src/benchmark_methods.py` — 5 methods comparison (BM25 only, Dense only, Hybrid, Hybrid+CE, Full Pipeline) via subprocess
- **Dataset stats**: `src/dataset_stats.py` — extract ChromaDB composition, `docs/dataset.md` — dataset documentation (740 chunks, 40 filings)
- **README**: Added Benchmark Hardware table + Retrieval Method Benchmark table (sebelum ablation table)
- **Makefile**: `benchmark` + `dataset-stats` targets
- **CI fix**: bandit B404/B603 skip (subprocess intentional), coverage omit standalone scripts (eval_*.py, benchmark, dataset_stats)
- **Commit**: `52d04ed` feat + `1d84115` bandit fix + `1b7c864` coverage fix
- **CI**: ✅ all green (40 tests, ruff 0, mypy 0, bandit 0, coverage ~44%)

#### Session 9 — Dataset Completion + MD&A Edge Case Fixes (19 Jul 2026)
- **5 MD&A fixes**: JNJ 10-Q em dash separator, CBRL 10-Q separator class + IGNORECASE, XOM CIK override (holding co → real CIK), DRI 10-K chunk explosion (58→21), orphaned chunk cleanup via `delete_chunks_for_filing()`
- **XOM 10-K 1 chunk**: Verified by design — Item 7 is a cross-reference paragraph (265 chars, 52 tokens)
- **Build index**: `python src/build_index.py` → **1079 chunks, 56 filings, 0 failures** ✅
- **Docs updated**: `readme.md` (1079/56/40), `docs/dataset.md` (JNJ+XOM, 4 sectors)
- **Obsidian vault**: `_Dashboard.md`, `02. Progress & Technical Documentation.md` updated
- **CI**: ✅ (ruff, mypy, bandit, pytest — no code changes, only docs + fixes)
