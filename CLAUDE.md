# RAG Variance Explainer

Read [AGENTS.md](AGENTS.md) at the start of project work and again after context compaction. It defines the pstack workflow and financial answer contract.

Use [readme.md](readme.md) for installation, backend choices, and entry points. The local MCP server starts with `python src/server.py` after the index and backend are configured. Its four tools are `rag.answer`, `rag.search`, `rag.list_companies`, and `rag.list_questions`. The agent workflow is in [.opencode/skills/rag-finance/SKILL.md](.opencode/skills/rag-finance/SKILL.md); it depends on this repository's running MCP server.

Treat numbers in older `docs/` files as dated experimental results. Use [GitHub readiness](docs/14.%20GitHub%20Readiness.md) for current verification status.
