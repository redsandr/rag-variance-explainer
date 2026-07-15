# Faithfulness Evaluation — LLM Output Quality

**Date:** 2026-07-14
**Method:** Manual review of 20 LLM-generated answers against retrieved context chunks
**Backend:** llama.cpp (Qwen 2.5 Coder 14B Q4_K_M)

## Summary

| Metric | Result |
|---|---|
| Total questions | 20 |
| Faithful (no hallucination) | 16 |
| Retrieval miss (golden chunk not retrieved) | 4 |
| Hallucination | 0 |

## Per-Question Results

| # | Question | Faithful | Notes |
|---|----------|----------|-------|
| eval-001 | CMG labor costs | ✅ | Specific numbers match context (0.2% decrease, 1.1% wage inflation, CA $20 minimum wage) |
| eval-002 | DRI marketing | ⚠️ | Retrieval miss — golden chunk `_6` not retrieved, answer too short |
| eval-003 | CMG wage inflation | ✅ | Detailed, sources match |
| eval-004 | CMG revenue | ⚠️ | Retrieval miss — golden chunk `_1` not retrieved, risk factor chunks dominate |
| eval-005 | CBRL operating costs | ✅ | Numbers match context |
| eval-006 | CMG food costs | ❌ | Retrieval miss — golden chunks `_6` not retrieved, forward-looking chunks (`_2`) dominate |
| eval-007 | CMG comp sales | ✅ | Numbers match context |
| eval-008 | CMG development | ⚠️ | Retrieval miss — golden `_4` not retrieved |
| eval-009 | CMG G&A | ✅ | Detailed breakdown matches context |
| eval-010 | DRI revenue | ✅ | Numbers match context |
| eval-011 | DRI food costs | ✅ | Numbers match context |
| eval-012 | Olive Garden segment | ✅ | Numbers match context |
| eval-013 | DRI same-restaurant sales | ✅ | Very detailed, per-brand breakdown |
| eval-014 | Chuy's acquisition | ✅ | Numbers match context |
| eval-015 | CBRL revenue | ✅ | Numbers match context |
| eval-016 | CBRL COGS | ✅ | Numbers match context |
| eval-017 | CBRL labor | ⚠️ | Golden chunks retrieved but answer weak |
| eval-018 | CBRL store operating | ✅ | Numbers match context |
| eval-019 | CBRL business model | ✅ | Numbers match context |
| eval-020 | CBRL G&A | ✅ | Numbers match context |
