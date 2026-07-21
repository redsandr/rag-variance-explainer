# Tuning Report — 19 Jul 2026

## State Data Terkini

### Pipeline
| Aspek | Detail |
|-------|--------|
| **Companies** | 7 (CMG, DRI, CBRL, WMT, TGT, JNJ, XOM) — 4 sectors |
| **Filings** | 56 |
| **Chunks** | 1079 |
| **Model** | Qwen2.5-7B-Instruct Q4_K.M (llama.cpp, GPU) |
| **Tests** | 47 | ruff 0 | mypy 0 | bandit 0 |

### Retrieval (Ablation — 19 Jul 2026 re-run)
| Pipeline | recall@1 | recall@3 | recall@5 | recall@10 | MRR |
|----------|----------|----------|----------|-----------|-----|
| Baseline (dense only) | 0.06 | 0.22 | 0.35 | **0.56** | 0.299 |
| + Query Expansion | 0.11 | 0.30 | 0.41 | **0.50** | 0.382 |
| + Hybrid (BM25) | 0.12 | 0.38 | 0.44 | **0.55** | 0.448 |
| **+ Cross-Encoder** | **0.23** | **0.54** | **0.71** | **0.81** | 0.538 |
| + Forward-Looking Penalty | 0.23 | 0.54 | 0.71 | 0.81 | 0.538 |
| **Full Pipeline** | **0.23** | **0.54** | **0.71** | **0.81** | 0.538 |

**Delta vs pre-rebuild:**
- Baseline recall@10: 0.51 → **0.56** (+0.05) — chunk boundary fix membantu
- Full pipeline recall@10: 0.81 → **0.81** (sama, tapi eval now includes 7 cos instead of 5)

### Faithfulness (19 Jul 2026)
| Metrik | Restaurant (20 Q) | Cross-sector (40 Q) |
|--------|-------------------|---------------------|
| Strict | **74.24%** | **59.29%** |
| Weighted | 75.32% | 73.45% |
| Claims | 66 | 113 |
| Retrieval gaps | 0 | 1 |

### Error Classification (Cross-sector, 40 Q)
**22 questions with errors** (13 partial + 9 unfaithful + 1 retrieval gap)

| Error Type | Count | % | Description |
|-----------|-------|---|-------------|
| **Omission / incomplete** | 10 | ~15% | LLM leaves out key drivers from source |
| **Factual accuracy** | 9 | ~13% | Numbers in answer don't match source |
| **Misattribution** | 7 | ~10% | Wrong chunk/filing cited |
| **Period cross-contamination** | 5 | ~6% | Number attached to wrong fiscal period |
| **Irrelevance** | 3 | ~4% | Answer doesn't address question |
| **Number transposition** | 2 | ~3% | Decimal shift (0.6% → 6%) |
| **Direction error** | 2 | ~3% | Increase vs decrease wrong |
| **Hallucination** | 2 | ~3% | Info not in source |
| **Metric conflation** | 2 | ~3% | Wrong metric label |
| **Scope error** | 2 | ~3% | Answer scope doesn't match question |

**Shift from earlier eval (restaurant-only, 20 Q):**
- Period cross-contamination: 71% → **6%** ✅ Prompt fix berhasil
- Metric conflation: 12% → **3%** ✅ Model swap membantu
- New dominant: **omission** (15%), **factual accuracy** (13%), **misattribution** (10%)

### Gap Analysis

| Gap | Impact | Root Cause |
|-----|--------|------------|
| **1 retrieval gap** (eval-035) | 1/40 = 2.5% | Cross-company question, architectural limit |
| **Strict ≤ 60%** | Portfolio ceiling | 7B model, cross-sector harder eval |
| **Omission errors** | 15% | LLM doesn't report all drivers from source |
| **Factual accuracy** | 13% | Numbers mismatch — retrieval gives wrong chunk period |
| **Misattribution** | 10% | Source citation format in prompt |

### Tuning Priorities
1. **🔴 Omission** — prompt: enforce "report ALL relevant factors" 
2. **🔴 Factual accuracy** — strengthen `verify_answer()` cross-check
3. **🟡 Misattribution** — stricter source citation format
4. **🟢 Period cross-contamination** — already low, minor tweaks
5. **🟢 Retrieval gap** — architectural, needs larger model or multi-hop

---

*Generated 19 Jul 2026 from ablation re-run + faithfulness eval + manual error classification*
