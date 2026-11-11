# NLI claim verification evaluation

The current NLI verdict is an experimental signal, not approval of a financial answer. A matched quote proves text presence, not the claim's period, calculation, or cause.

`data/nli_claim_eval.json` contains 16 agent-drafted claim and evidence pairs across five tickers and four sectors. Labels distinguish supported, refuted, and not enough information. The cases include reported figures, calculated amounts, percentage points, wrong periods, wrong directions, metric confusion, reported causes, and invented causes. Source IDs point to local indexed filing chunks. The short evidence fields are analyst summaries of those chunks, **not guaranteed verbatim filing quotations**. No independent reviewer has checked the labels against original SEC filings. The set is a smoke test and must not be used to tune a threshold or claim model accuracy.

The dataset also records a primary-document URL for each indexed source, located via its SEC accession directory. URL identification alone is not validation of the text or the labels. Automated Python access initially returned HTTP 403 without a configured `SEC_USER_AGENT`; no filing content was silently substituted from the local index.

After a real `SEC_USER_AGENT` was configured, `python src/review_nli_sources.py` fetched the five original filings without an LLM. Eight-token window overlap between each indexed passage and its SEC HTML text was CMG 37/37, DRI 48/48, WMT 46/46, JNJ 40/41, and XOM 30/35. These ratios measure sampled text overlap after whitespace and punctuation normalization, **not** the share of a filing reviewed or claim accuracy. Direct inspection of the relevant original spans confirmed the reported CMG labor-cost figures and narrative, DRI marketing narrative, WMT comparable-sales figure and explanation, JNJ European growth components, and XOM compressed-margin driver. Claims asserting missing evidence still need a broader source review, and labels remain agent-drafted, not independently reviewed.

Run from the repository root with the local index and installed NLI model:

```powershell
.\venv\Scripts\python.exe src/eval_nli_claims.py --device cpu
```

The command prints its dataset version, model, threshold, per-case predicted labels, and confusion counts. It compares short evidence summaries with the entire indexed passage. It does not call the RAG LLM, write result files, or change application settings. `false_accept` means a refuted or not-enough-info claim was predicted as supported; `false_reject` means a supported claim was not predicted as supported. A refuted claim predicted as neutral is also an error in the three-way confusion count.

The first run on 2026-11-11 used `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` on CPU at threshold 0.40. On the 16 draft cases, short summaries yielded 9 correct, 0 false accepts, and 5 false rejects. Full indexed passages yielded 10 correct, 4 false accepts, and 0 false rejects. These numbers compare two input shapes on an unreviewed small set; they are **not estimates of real-world reliability**. Full-passage errors included an unsupported Darden marketing amount, a wrong-period Chipotle amount, and a wrong Johnson & Johnson operational growth rate being accepted. The model's 512-token maximum input length is one possible source of context loss, not a proven explanation for each error.

Before changing verification or shipping a quality claim:

1. Have an independent reviewer check each evidence item and label against its original SEC filing, with accession, filing URL, and exact supporting spans. Correct or exclude ambiguous examples. Freeze a versioned development set and an untouched holdout spanning tickers, sectors, periods, numerical, causal, and conflicting-evidence claims.
2. Measure evidence retrieval separately from claim verification. Add cases where the cited passage is plausible but incomplete or contradicted elsewhere in the same filing. Keep missing evidence separate from refutation.
3. Evaluate candidate evidence windows and verifier models on the development set. Report the three-way confusion matrix, false accepts, false rejects, and results by claim type. Select a threshold only there; evaluate the selected configuration once on the holdout.
4. Review arithmetic and period semantics separately. NLI scores alone do not prove subtraction, units, fiscal periods, or causal attribution. Run end-to-end checks against human-labeled answers only after the claim-level checks are stable.

The three-way evidence labels follow [FEVER](https://aclanthology.org/N18-1074/). Claim-level checks follow the atomic-fact framing of [FActScore](https://arxiv.org/abs/2305.14251). [RAGTruth](https://arxiv.org/abs/2401.00396) documents unsupported and contradictory statements in RAG output. The [NLI model card](https://huggingface.co/MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli) reports general NLI benchmark results, not SEC-specific accuracy.
