# Security Policy

## Reporting a Vulnerability

This project handles financial data and API keys. If you discover a security
vulnerability, please report it privately — do not open a public issue.

Send details to the repository maintainer via GitHub Issues with the
`security` label, or reach out directly through the GitHub profile.

We will acknowledge receipt within 48 hours and work on a fix before
public disclosure.

## Scope

- Prompt injection vulnerabilities in the RAG pipeline
- API key or credential exposure
- SEC EDGAR data integrity issues
- Cross-tenant data leakage (if applicable)

## Out of Scope

- LLM hallucination or incorrect financial answers (these are documented
  known limitations, not security issues)
- Dependency vulnerabilities already patched in latest versions
