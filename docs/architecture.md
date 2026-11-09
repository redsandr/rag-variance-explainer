# Architecture and boundaries

## Index build

`src/build_index.py` loops over the seven tickers in `src/constants.py`. `src/ingest.py` obtains SEC 10-K and 10-Q filings, extracts MD&A text, and `src/chunking.py` splits it by paragraph, line, then token when needed. `src/post_process.py` tags each chunk. `src/embedding.py` generates document vectors, and `src/retrieval.py` stores the text, metadata, and vectors in a local ChromaDB collection.

The checkpoint records processed ticker and accession pairs after a filing is stored. On a retry, completed pairs are skipped. A replacement filing is embedded and upserted before obsolete chunk IDs are deleted, so an embedding or upsert error leaves the previous filing in place. If any filing fails, the command logs it and exits with an error. A checkpoint is progress, not proof of corpus completeness. `--rebuild` clears the checkpoint and reprocesses the selected filings; it does not erase filings outside that selection from ChromaDB.

## Question path

`app.py`, `src/api.py`, and `src/server.py` call `src/rag.py`. Retrieval uses dense vectors, optional query expansion, BM25 merging, and a cross encoder before the LLM sees selected passages. `src/llm.py` chooses the configured local or cloud backend. `src/verifier.py` parses the structured answer and checks each claim's source index and quoted text against a retrieved chunk. A parsing or quote failure produces a refusal instead of presenting the raw model text as sourced findings.

Quote matching tolerates case and whitespace differences. It establishes the presence of text in a retrieved excerpt, not the truth of a computed value or causal explanation. NLI is optional and off by default because its accuracy has not been established on a human labeled financial set. The historical LLM judge scores in older documents have not been reproduced on the current code.

## Runtime and data boundaries

- SEC and model downloads need network access. The index, checkpoint, downloaded models, and `.env` remain local and are excluded from Git.
- A local llama.cpp backend uses a separately installed GGUF model. OpenAI and Anthropic backends send retrieved passages to their APIs.
- The REST API and MCP server are local single user interfaces. They have no authentication, quotas, or multi tenant isolation. Keep their default bind address on loopback.
- The application never executes LLM generated arithmetic code. Treat its numerical and financial conclusions as research leads that require source review.

See [GitHub readiness](14.%20GitHub%20Readiness.md) for the tests already run and the gates still open.
