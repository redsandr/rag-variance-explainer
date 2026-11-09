---
name: rag-finance
description: Use the locally installed RAG Variance Explainer MCP server to search SEC MD&A and answer questions about its seven supported companies. Requires this repository, a built index, and an LLM backend for answers.
---

# RAG finance

Follow [the README](../../../readme.md) to install the repository, build the SEC index, choose an LLM backend, and connect `python src/server.py` as a stdio MCP server. This skill does not install the application or include its data and models.

## Answer a question

1. Call `rag.list_companies` to confirm the requested ticker is covered. The default set is CMG, DRI, CBRL, WMT, TGT, JNJ, and XOM.
2. Call `rag.answer` with the user's question and ticker. Use `rag.search` when you need to inspect retrieved passages or the answer lacks enough support.
3. Report the cited filing and date. Preserve any refusal or uncertainty. A matching quote confirms source text, while causal and numerical claims still need inspection of the filing.

For comparisons, query each company separately and retain each company's sources. Use `rag.list_questions` only for examples of supported question wording; it does not prove that the current index contains the answer.

The server covers English MD&A sections from the filings selected during local indexing. Downloads require internet access; a local LLM can answer without sending retrieved passages to a cloud API. OpenAI and Anthropic backends send passages to their APIs. See [GitHub readiness](../../../docs/14.%20GitHub%20Readiness.md) for current limits.
