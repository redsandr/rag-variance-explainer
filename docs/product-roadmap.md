# Active product roadmap

Updated: 2026-11-10. This document describes the **target**, not shipped capabilities. The repository root is the code and documentation source of truth; the separate `Documents/portofolio 2/Project 2` vault points here. Older numbered notes are history, not release evidence.

## Product and user

An evidence-first research assistant for independent financial analysts investigating public companies. It should help answer what changed, why management says it changed, what alternative explanations exist, and what to check before a decision. It must distinguish a company's filings, the analyst's uploaded documents, and dated third-party news. It must not turn a news headline or a matching quote into a proven cause, calculated value, or buy/sell recommendation.

Initial scope: US public companies with reviewed SEC 10-K/10-Q coverage; English research workflow. Owner-operated businesses and arbitrary PDF chat are separate future use cases, not promises of the first release.

## What exists today

- Local SEC ingestion and Chroma index, Streamlit UI, REST API, and a local MCP server (`src/server.py`). These surfaces do not yet share a reviewed production-grade answer contract.
- Quote-to-retrieved-chunk checking can refuse unsourced generated text. It does not prove causation, arithmetic, or fidelity to the original filing.
- Local Docker llama.cpp backend can serve the existing 7B model. A Qwen3-8B/TurboQuant Docker build and comparative benchmark are **not yet verified**. Keep baseline and candidate configurations separate.
- No general user-PDF ingestion, live news retrieval, hosted multi-user isolation, or Agensi publication has been verified. See [readiness](14.%20GitHub%20Readiness.md) for recorded checks.

## Delivery order and gates

### 1. Reliable SEC research core

Reproduce the failed Chipotle question: record the retrieved passages, generated claims and rejected quotes without treating model output as verified. Establish a versioned, human-reviewed set of questions covering revenue versus income versus margin, period comparisons, numerical checks, unsupported causes, and abstention. Rebuild a small index with source URLs; manually compare one complete result with the original SEC filing. Record model, index version, prompt, configuration, latency and per-question outcomes. Fail closed on parse and quote errors; independently review causal and numerical claims.

**Gate:** at least one recorded end-to-end filing-backed case through UI, API and MCP, plus documented failures and regression tests. This is a development milestone, not a production-readiness claim.

### 2. Analyst decision workflow

Present reported facts, calculated metrics with inputs, interpretation, competing explanations, unknowns, and conditional next checks in distinct fields. For example, a rise in net income is not automatically a rise in revenue or margin. A decision consideration must cite the supporting and conflicting evidence and explain what would change it. No personalized investment recommendation or fabricated confidence percentage.

**Gate:** representative analyst review confirms the distinctions and can inspect the original sources; unsupported conclusions abstain.

### 3. News as corroboration, not authority over filings

Choose a licensed/terms-compliant news provider and record URL, publisher, publication time, retrieval time, entity, and event date. Search within a declared time window; deduplicate syndicated stories; keep filing claims separate from news claims. If news conflicts with a filing, show the conflict and dates rather than smoothing it over. Treat web/news text as untrusted input, never as instructions to the model or app.

**Gate:** tests for outdated, duplicate, irrelevant, inaccessible, contradictory, and prompt-injection news; explicit absence when no reliable result is found. Provider and cost remain open decisions.

### 4. Analyst-uploaded PDFs

Start with financial reports. Extract text and tables with page references, flag scanned/OCR or unreadable pages, and maintain document-level provenance. Separate private uploads from shared SEC data and from other users; define retention/deletion, upload size and type limits, malware and resource controls, and external-processing consent before hosting. A PDF title or author is not proof of authenticity.

**Gate:** real and malformed PDF fixtures; verified page citations; user isolation, deletion and abuse tests before public upload.

### 5. Interfaces, operational hardening and distribution

Refactor only after the answer/evidence contract is stable. Make Streamlit a clear research workbench with inspectable sources, progress and actionable failure states; update the public website only with reviewed cases and measured claims. Test the existing MCP with a fresh client and clean setup; package agent/Agensi instructions only after reproducibility, security and licensing checks. Hosted scale additionally needs authentication, quotas, persistence, monitoring, backup/restore, privacy terms and incident handling.

**Gate:** [readiness record](14.%20GitHub%20Readiness.md) is updated with actual commands, environments and outcomes. Do not register/publish or claim production readiness while required gates remain open.

## Immediate next actions

1. Finish and validate the Qwen3-8B download. Build the candidate TurboQuant image separately; verify supported flags and compare against a recorded 7B baseline on identical workloads. Do not infer answer quality from token speed.
2. Capture a reproducible failing Chipotle retrieval/generation case and fix the first unsupported step, keeping fail-closed behavior.
3. Define the smallest reviewed filing-backed analyst case and run it through all three current surfaces before adding news or PDF upload.
