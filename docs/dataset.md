# Dataset

## Overview

| Property | Value |
|----------|-------|
| Total chunks | 740 |
| Total tokens | ~251k |
| Total filings | 40 |
| Filing types | 10-K (211), 10-Q (529) |
| Date range | 2024–2026 (2+ years per company) |
| Source | SEC EDGAR HTML |
| Section | MD&A (Item 7 / Management's Discussion and Analysis) |

## Composition by Ticker

| Ticker | Company | Sector | Chunks | Filings |
|--------|---------|--------|-------:|--------:|
| WMT | Walmart | Retail | 187 | 8 |
| CBRL | Cracker Barrel | Restaurant | 177 | 8 |
| DRI | Darden Restaurants | Restaurant | 159 | 8 |
| TGT | Target | Retail | 121 | 8 |
| CMG | Chipotle | Restaurant | 96 | 8 |

## Composition by Sector

| Sector | Chunks | Percentage |
|--------|-------:|-----------:|
| Restaurant | 432 | 58.4% |
| Retail | 308 | 41.6% |

## Composition by Year

| Year | Chunks |
|------|-------:|
| 2024 | 178 |
| 2025 | 393 |
| 2026 | 169 |

## Chunking Strategy

- **Method:** Structure-aware recursive split
- **Chunk size:** 500 tokens (tiktoken cl100k_base)
- **Fallback order:** paragraph → line → token
- **Metadata per chunk:** ticker, accession_number, form (10-K/10-Q), filing_date, chunk_index, metric tags

## Preprocessing

1. MD&A section extracted from HTML via `ingest.py` (regex-based section detection)
2. XBRL tags stripped
3. Tables preserved as structured text
4. Forward-looking statements and risk factors tagged for penalty scoring
5. Metric labels extracted via `tag_chunk()` for metric-level retrieval filtering

## Evaluation Split

40 ground-truth questions, balanced across sectors:
- 20 restaurant (CMG, DRI, CBRL)
- 20 retail (WMT, TGT)

Each question has 1-3 golden chunk IDs from the index. Questions cover:
- Labor cost variance
- Revenue drivers
- Margin changes
- Expense analysis
- Segment performance
- Cross-company comparison
