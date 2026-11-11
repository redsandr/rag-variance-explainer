# CMG/JNJ: cost amount versus share of revenue

Status: operator-observed evaluation case; **not an independent holdout**. The operator ran the same question with and without reranking after the source-index prompt change. Both runs returned quote-matched answers for CMG and JNJ. No model was run while preparing this note.

Question: “Compare how Chipotle's labor costs changed for the three months ended June 30, 2024 and how Johnson & Johnson's Europe sales grew for the quarter ended March 29, 2026, respectively. Report each company's metric separately; do not treat them as the same metric or period.”

## Source checks reported by operator

- CMG, 10-Q filed 2024-07-25, accession `0001058090-24-000032`, labor-cost passage (retrieved chunk 6): three months ended June 30, 2024 versus June 30, 2023. Labor costs: **$716.6 million versus $611.7 million, +17.2%**. As a percentage of total revenue: **24.1% versus 24.3%, down 0.2 percentage points**. The operator located the ratio explanation in the linked SEC filing. These are opposite directions for different measures, not a contradiction.
- JNJ, 10-Q filed 2026-04-22, accession `0000200406-26-000087`, Europe-sales passage (retrieved chunk 1): fiscal first quarter 2026; **14.5%** total growth, including **2.7%** operational growth and **11.8%** positive currency impact. The operator located the statement in the linked SEC filing. The supplied adjacent table labels the fiscal first quarter as ended March 29, 2026.

The operator did not supply SEC URLs or archival copies here; the observations above are based on the pasted Streamlit passage and SEC-tab excerpts, not on an independently downloaded filing. Preserve the original excerpts and URLs if promoting this to a reviewed benchmark.

## Stage-by-stage assessment

| Stage | Observation |
| --- | --- |
| Retrieval | Both passages were available with and without reranking in this run. |
| Citation | Both generated answers had quote matches in their cited passages. Source numbers differed because passage order differed. |
| Numbers and units | JNJ 14.5% matches the excerpt, but it includes currency effects. CMG's “decreased 0.2% as a percentage of total revenue” describes a ratio, not the nominal cost, which increased 17.2%. |
| Completeness | Both answers omitted CMG's nominal cost increase even though the retrieved passage contained it. A reader asking how “labor costs changed” could mistake the ratio decline for a fall in spending. |

Expected answer when the passage contains both measures: “Chipotle's labor costs rose from $611.7 million to $716.6 million (up 17.2%) in the three months ended June 30, 2024 versus 2023, while their share of total revenue fell from 24.3% to 24.1% (down 0.2 percentage points). JNJ reported 14.5% growth in sales by companies in Europe in fiscal Q1 2026, including 2.7% operational growth and an 11.8% positive currency impact.” Each atomic statement still requires a matching quote and source index in structured output.

Decision: the generation prompt now asks for both dollar-cost and revenue-share directions **when the question is broad and the same-period evidence contains both**. This is prompt guidance, not a deterministic unit validator; the existing quote check alone cannot guarantee correct arithmetic, units, or completeness. Re-run this case and review new, independently selected questions before claiming improvement. Do not tune NLI against this case.

## First operator rerun after amount/ratio prompt change

Retrieval returned CMG chunk 6 at source index 0 and JNJ chunk 1 at source index 3. The result was **No verified finding**: diagnostic `claim=0 cited_source=0 quote_chars=247 ellipsis=True matches_other_sources=[]` and `Claim 0: quote not found (fuzzy) in chunk 0`. The structured claim text was not captured, so the exact mismatch is unknown; do not classify the arithmetic or completeness of this rejected answer. The verifier checks that the entire normalized quote occurs contiguously in its cited passage. Rather than accept a stitched quotation or reassign a source, the structured-output prompt now requests one short verbatim contiguous excerpt per quote, with separate claims for separate spans. This is a model-dependent hypothesis, not a verified fix; the operator must rerun it.

## Second operator rerun and scope reset

The next run returned the same failure signature (`claim=0`, cited source 0, 247 quote characters, ellipsis, no other source matches), with CMG chunk 6 and JNJ chunk 1 still retrieved. The app does not cache answers: its Streamlit caches hold the LLM client and index statistics, while `_analyze()` invokes `answer_question()` on every submission. This does **not** prove the model ignored the revised prompt; deterministic decoding and an unchanged generation pattern are also possible. No generated quote was saved, so the exact mismatch remains unknown.

The task is reliable, independently checkable financial answers across questions, **not** passing this one question by accepting unsupported quotations. [ALCE (Gao et al., EMNLP 2023)](https://arxiv.org/abs/2305.14627) measures answer correctness and citation quality separately, and reports incomplete citation support even for strong systems; it does not validate this app's specific fix. In [ALCE issue #26](https://github.com/princeton-nlp/ALCE/issues/26#issuecomment-2115139194), the project collaborator says malformed citation formats should be penalized rather than silently normalized in their evaluation. This forum discussion supports keeping citation failures visible, but does not diagnose this particular model's quote. The web search integration returned HTTP 402, so these directly fetched primary sources and local code/observations are the research basis; no wider search results are claimed.

Small follow-up: the amount-versus-ratio instruction is now general rather than a CMG-specific example, the structured quote instruction and schema both specify a single continuous verbatim span, and Streamlit displays the existing validation reason without showing the failed generated claim. Quote matching and source indexes remain fail-closed. None of these non-model changes demonstrate that the model will comply; record full operator outputs and evaluate retrieval, source index, quote validity, units, and completeness separately on independently chosen questions before making an accuracy claim.
