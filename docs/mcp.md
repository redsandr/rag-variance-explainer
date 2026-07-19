# MCP Server — RAG Variance Explainer

MCP (Model Context Protocol) server exposing the RAG pipeline as tools
consumable by AI agents (Claude Code, Cursor, Cline, Windsurf, etc.).

## Quick Start

```bash
# Stdio mode (default) — for local MCP clients
python src/server.py

# SSE mode — for remote clients on port 8765
python src/server.py --sse --port 8765
```

From Makefile:
```bash
make mcp       # stdio
make mcp-sse   # SSE on :8765
```

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `rag.answer` | Answer a financial question with sourced citations | `question` (str, req), `ticker` (str, opt) |
| `rag.search` | Search chunks by relevance (no LLM) | `query` (str, req), `ticker` (str, opt), `top_k` (int, default 5) |
| `rag.list_companies` | List available tickers with names and sectors | — |
| `rag.list_questions` | Get suggested questions per ticker or all | `ticker` (str, opt: "ALL" for all) |

## Client Configuration

### Claude Code (`claude.json`)

```json
{
  "mcpServers": {
    "rag-variance-explainer": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "C:\\Users\\Lenovo\\Documents\\Portofolio 2 App\\rag variance explainer"
    }
  }
}
```

### Cursor

1. Open Cursor Settings → Features → MCP Servers
2. Add new server:
   - Name: `rag-variance-explainer`
   - Type: `command`
   - Command: `python src/server.py`
   - Working directory: path to project root

### Cline (VS Code Extension)

In `cline_mcp_settings.json`:
```json
{
  "mcpServers": {
    "rag-variance-explainer": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "C:\\Users\\Lenovo\\Documents\\Portofolio 2 App\\rag variance explainer"
    }
  }
}
```

### Windsurf

Add to `windsurf.json`:
```json
{
  "mcpServers": {
    "rag-variance-explainer": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "C:\\Users\\Lenovo\\Documents\\Portofolio 2 App\\rag variance explainer"
    }
  }
}
```

### Remote (SSE) — any HTTP client

```bash
# SSE endpoint
curl -N http://localhost:8765/sse

# Streamable HTTP (JSON-RPC)
curl -X POST http://localhost:8765/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

## Architecture

```
┌──────────────┐     stdio/SSE      ┌──────────────────┐
│  AI Agent     │ ◄──────────────►  │  MCP Server       │
│ (Claude,      │                    │  (src/server.py)  │
│  Cursor, ...) │                    │                   │
└──────────────┘                    │ rag.answer        │
                                    │ rag.search        │
                                    │ rag.list_companies│
                                    │ rag.list_questions│
                                    └────────┬─────────┘
                                             │
                                    ┌────────▼─────────┐
                                    │  RAG Pipeline      │
                                    │  (src/rag.py,      │
                                    │   src/retrieval.py)│
                                    └────────────────────┘
```

## Notes

- The server loads the LLM on first tool call (lazy init via `LLMClient()`)
- No embedding model is loaded — ChromaDB queries use existing vectors
- Cross-encoder re-ranking is enabled (CPU or CUDA based on config)
- Timeout: 120s per generation (configurable via `LLM_TIMEOUT` env var)
