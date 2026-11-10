# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Independent financial analysts and small teams researching US companies.

## Product purpose

Help analysts investigate why a financial metric changed in a company's SEC 10-K or 10-Q. The website is a portfolio case study and an invite-only demo, not a public financial advice service.

## Positioning

The local research prototype retrieves MD&A passages, reranks them, generates a structured answer, and checks whether its source quotes occur in retrieved text. A quote match does not independently validate a cause or calculation.

## Operating context

Analysts inspect the original SEC filing before relying on an explanation. The first reviewed examples should come from restaurant and retail filings. The interface and case study use English.

## Capabilities and constraints

The repository includes a Streamlit UI, REST API, and MCP server. Current indexing covers seven US companies across four sectors, but the website must not imply that all indexed answers have been independently verified. No public hosted demo, invitation access, usage limits, or price has been confirmed. Free-form questions should be limited to companies and periods with reviewed index coverage when an invited demo is implemented.

## Evidence on hand

`docs/14. GitHub Readiness.md` records local tests but no verified clean-index end-to-end answer or human-reviewed faithfulness set. `docs/15. Product Development Handoff.md` notes that existing landing-page samples, page references, confidence scores, and time-savings figures are unverified. No filing-backed demo case is approved for publication yet.

## Product principles

- Show the source and the limits of verification before presenting an answer as evidence.
- State uncertainty when the filing does not explicitly support a causal explanation.
- Prefer a small set of reviewed examples to broad unsupported coverage claims.
