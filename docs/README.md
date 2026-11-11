# Documentation

Start with the [project README](../readme.md) to install and run the application. These pages explain the current boundaries and preserve earlier experiments.

## Current reference

- [Product roadmap](product-roadmap.md): analyst use case, evidence boundaries, news/PDF plans, and release gates.
- [Domain language](../CONTEXT.md): distinction between filing evidence, news, findings, and decision considerations.
- [Architecture](architecture.md): ingestion, retrieval, answer verification, data boundaries, and failure behavior.
- [GitHub readiness](14.%20GitHub%20Readiness.md): observed checks and open release gates.
- [MCP setup](mcp.md): local server commands and tools.
- [Dataset](dataset.md): supported companies and evaluation data.
- [Operator demo review](demo-review-runbook.md): six candidate questions, complete local startup, evidence capture and human review checklist.
- [Six candidate run results](demo-review-results-2026-11-11.md): dated observations and remaining original-filing checks; no case is approved for publication yet.
- [Output-token budget and SEC archives](output-budget-and-sec-archives.md): observed limits, explicit truncation notice, and links to historical filings.

## Historical notes

The [history folder](history/README.md) contains earlier technical progress, roadmap, hardening, structured-output, and tuning notes. The separately edited [NLI note](13.%20Phase%202%20Claim%20Decomposition%20%2B%20NLI.md), [product handoff](15.%20Product%20Development%20Handoff.md), and evaluation artifacts also record their original contexts. None is a current release checklist. Some paths, model defaults, test counts, and score claims have changed. Check the code and [readiness record](14.%20GitHub%20Readiness.md) before repeating a result.

The [dashboard](_Dashboard.md) is a short navigation page for readers of the old Obsidian vault.

## Working investigations (not release claims)

- [CMG/JNJ amount versus ratio](cmg-jnj-amount-vs-ratio-case.md): observed quote matches and an incomplete financial answer.
- [Multi-company evidence research](multi-company-evidence-research.md): retrieval and citation-index failures and candidate remedies.
- [Operator smoke test](operator-rag-smoke-test-2026-11-11.md): dated run observations, not a general success rate.

Keep these dated notes as audit evidence. Archive or remove historical files only after checking references and agreeing on the precise list; do not equate older benchmark claims with current product quality.
