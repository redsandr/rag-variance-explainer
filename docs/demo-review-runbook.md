# Operator runbook: candidate SEC demo cases

**Goal:** choose several *independently reviewed* examples for the portfolio website, while keeping free-form SEC questions usable. These prompts are evaluation candidates, not hard-coded production rules or approved website copy. A quote match is not a check of numeric meaning, period, causality or completeness. Run models only as the operator; do not rebuild the existing local index for this review.

## Start from a stopped Streamlit app (Windows PowerShell)

Open Docker Desktop. In **PowerShell A**:

```powershell
docker ps -a --filter "name=rve-official-8b-rag-34l"
docker start rve-official-8b-rag-34l
Invoke-RestMethod http://127.0.0.1:8080/v1/models
```

`docker start` may say the container is already running. Stop and check Docker if the models endpoint does not respond; do not substitute the 7B launcher. Close any existing Streamlit process with Ctrl+C. In **PowerShell B**:

```powershell
cd "C:\Users\Lenovo\Documents\Portofolio 2 App\rag variance explainer"
$env:LLM_BACKEND = "llama_server"
$env:LLAMA_SERVER_MODEL = "rve-8b-official"
$env:LLAMA_SERVER_TIMEOUT = "600"
$env:RAG_LLM_MAX_TOKENS = "4096"
$env:EMBEDDING_DEVICE = "cpu"
$env:RAG_CROSS_ENCODER_DEVICE = "cpu"
$env:RAG_DIAGNOSTICS = "true"
$env:RAG_NLI_ENABLED = "false"
.\venv\Scripts\python.exe -m streamlit run app.py
```

Use the URL printed by Streamlit (normally `http://localhost:8501`). These environment settings apply only in this PowerShell window. They do not edit `.env`. **Do not share `.env` or your SEC user-agent value.** If the model endpoint lists a different model ID, verify the container setup before changing `LLAMA_SERVER_MODEL`.

## Run six distinct questions, one at a time

Choose **Company** as shown, set **Source passages** to `5`, leave **Compare retrieval with and without reranking** unchecked, then click **Analyze filings** once. Do not modify a question after seeing its output; log failures too. The earlier CMG/JNJ comparison is a separate development case and is **not** part of these six candidates.

| ID  | Company | Question to paste                                                                                                                                                                                                   | What to check in original filing                                                                                              |
| --- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| A   | CMG     | For the three months ended June 30, 2024, how did Chipotle's labor costs in dollars and as a share of total revenue change versus the comparable 2023 period, and which drivers did the filing explicitly identify? | Nominal versus share; period and all stated offsets.                                                                          |
| B   | CMG     | For the three months ended June 30, 2024, what changed in Chipotle's food, beverage and packaging costs as a percentage of total revenue, and what causes does its 10-Q explicitly give?                            | Exact metric, period and stated drivers; no invented decomposition.                                                           |
| C   | DRI     | According to Darden's fiscal 2025 filings, how did food and beverage costs as a percentage of sales change, and which factors are explicitly named in the cited period?                                             | First identify which fiscal period the retrieved passage covers; compare the linked original filing before accepting numbers. |
| D   | DRI     | In Darden's fiscal 2025 filings, what drove total sales changes, and which reported figures belong to the same period?                                                                                              | Sales versus same-restaurant sales; acquisitions versus organic growth; period integrity.                                     |
| E   | CBRL    | In Cracker Barrel's fiscal 2024 filings, what factors are given for changes in store operating expenses as a percentage of revenue?                                                                                 | Check actual period and metric in the retrieved filing; abstention is valid if evidence is absent.                            |
| F   | JNJ     | For Johnson & Johnson's fiscal first quarter ended March 29, 2026, how did sales by companies in Europe change, and how much was operational growth versus currency impact?                                         | Total versus operational growth and currency, plus period in the source filing.                                               |
|     |         |                                                                                                                                                                                                                     |                                                                                                                               |

These are *questions*, not pre-assigned correct answers. The existing `data/eval_questions.json` contains exploratory retrieval targets; do not treat its chunk IDs or notes as human-reviewed answer labels. A single question may be too broad; record that as an evaluation outcome rather than silently changing it. Six runs give variety, not a statistically meaningful reliability rate.

## Send and review the results

For **each** ID send the full status and answer (or refusal); all **Matched quotations** and source numbers; the relevant expanded **Filing passages** with their **Open SEC filing** URLs; the `[RAG-DIAG] retrieved=`, `source=` and `claim=` lines; and `Validation:` / `[StructuredOutput]` errors if present. Include the exact model ID reported by the Docker endpoint and whether reranking was on. Do not paste credentials or private documents.

Reviewer records **retrieval relevance, quote/source-index validity, numeric values and units, period integrity, causal support, completeness, and final decision** separately. For each candidate, save filing URL, accession, prompt, raw output, run date, reviewer, and what the original filing says. Mark `approved`, `needs correction`, or `rejected`; only `approved` copy can replace `Pending review` on the landing. Do not report pass percentages from this small, operator-selected set. To avoid overfitting, select additional company/metric pairs independently after these six.

## PDF upload is a separate decision

The current UI answers from a pre-indexed SEC corpus; it **does not accept user PDF uploads**. A local single-user PDF prototype is possible, but PDF tables/OCR, page citations, file-size limits, untrusted content, retention and isolation for a hosted demo require their own acceptance checks. Do not advertise PDF upload on the public website until implemented and reviewed.
