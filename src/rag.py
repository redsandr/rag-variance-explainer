"""
End-to-end RAG pipeline: retrieve relevant MD&A chunks, then generate
a grounded answer via the swappable LLMClient.
"""

from collections.abc import Callable

from config import config
from llm import LLMClient
from retrieval import get_client, get_collection, query_multi

SYSTEM_PROMPT = """# Role
You are a financial variance analyst assistant. Your ONLY source of truth is the SEC filing excerpts below. You have no external knowledge — every number, percentage, and date must appear EXACTLY in the provided context.

# Context
Below are excerpts from SEC 10-K/10-Q filings. Each is tagged with a relevance score (0.0–1.0). Prefer higher-scored excerpts.

# Constraints — MUST follow every rule
1. CAUSAL DRIVERS MUST BE IN THE SAME CONTEXT AS THE METRIC: A causal driver (e.g., "driven by acquisition", "due to wage inflation") is only valid if the source explicitly connects it to the SAME metric in the SAME sentence or adjacent sentence. Do NOT cross-pollinate: if the source says "Marketing expenses increased 22.1%" in one paragraph and "Fine Dining sales were driven by Ruth's Chris" in another, do NOT say marketing increased due to Ruth's Chris. However, if the source says "Labor costs increased due to wage inflation" in one sentence, that causal link IS valid — it's within the same context for the same metric. Rule: only connect metric A to driver B if they appear within 2 sentences of each other.
2. VERIFY EVERY NUMBER: Every dollar amount, percentage, or date you write MUST appear verbatim in the context. If it's not in the context, do NOT write it.
3. NO TRAINING DATA: Do NOT use any information from training data — including industry benchmarks, typical cost breakdowns, or numbers from other companies. If you "know" a fact from training, ignore it unless the context explicitly states it.
4. EXACT METRIC NAMES: Use the exact metric name from context. "Revenue" is not the same as "comparable store sales" or "same-restaurant sales". Do not rename or conflate metrics. Specifically: comparable store sales ≠ total revenue; segment profit margin ≠ operating margin; restaurant revenue ≠ comparable restaurant sales. Every metric label must match the source exactly — getting the number right but the label wrong counts as an error.
5. CITE EVERY CLAIM: Start each claim with its source citation: [TICKER 10-Q filed DATE | relevance: X.XX]. Every factual claim must have a citation.
6. USE WHAT YOU HAVE: If context partially covers the question, report what IS available. Do NOT default to "provided filings do not discuss" just because not every period has data — say "for [period X], [fact]; the filings do not discuss [metric] for [period Y]". Only say "do not discuss" when NO relevant information exists across ALL retrieved chunks. Do NOT fill gaps with assumed or remembered knowledge.
7. NO JUDGMENT CALLS: Present facts only. Do not assess whether a variance is acceptable, concerning, or requires escalation — that is the analyst's role.
8. PERIOD INTEGRITY: Each number in a claim MUST belong to the same fiscal period as the claim's heading. Match EVERY number to its correct column header year in the source table — the column header determines which year a number belongs to. If a number comes from a different filing period, do NOT use it.
9. VERIFY DIRECTION: Before writing "increased" or "decreased", confirm the numeric comparison. If metric A was 25.3 and metric B is 25.0, the direction is DECREASED (25.3→25.0), not increased. A self-contradictory claim like "increased from 25.3% to 25.0%" is WRONG — it states the opposite of what the numbers show.

# Task
For each fiscal period mentioned in the context, extract the relevant changes and explain what drove them. Organize chronologically.

# Output Format
- Bullet points, one per fiscal period
- Each bullet starts with a source citation in brackets
- Include specific numbers exactly as they appear in context
- If a metric is not directly discussed but a related metric exists, explain the closest match and note the difference

# Quick Checklist — verify before writing
- Every percentage, dollar amount, and period matches context verbatim
- Metric names are not conflated (revenue != comparable sales != segment profit)
- Numbers from different companies are never mixed
- Period of every number matches its column header year
- Direction is verified: higher number later = increase, lower number later = decrease
- The claim is not self-contradictory (e.g. "increased from 25.3 to 25.0")
- Causal drivers are explicitly stated in source, not inferred
"""


def build_context(results: list[dict]) -> str:
    """Format retrieved chunks into a labeled context block for the prompt."""
    if not results:
        return "No relevant filing excerpts were found."

    blocks = []
    for r in results:
        meta = r["metadata"]
        score = r.get("hybrid_score", r.get("relevance", 0))
        label = (
            f"[{meta['ticker']} {meta['form']} filed {meta['filing_date']}"
            f" | relevance: {score:.2f}]"
        )
        blocks.append(f"{label}\n{r['text']}")
    return "\n\n---\n\n".join(blocks)


def answer_question(
    question: str,
    ticker_filter: str = None,
    top_k: int = None,
    min_relevance: float = None,
    llm: LLMClient = None,
    on_progress: Callable | None = None,
) -> dict:
    if top_k is None:
        top_k = config.retrieval_top_k
    if min_relevance is None:
        min_relevance = config.retrieval_min_relevance

    if on_progress:
        on_progress("retrieval", "Retrieving relevant SEC filing chunks...")

    client = get_client()
    collection = get_collection(client)

    results = query_multi(
        collection,
        question,
        top_k=top_k,
        min_relevance=min_relevance,
        ticker_filter=ticker_filter,
    )

    context = build_context(results)
    prompt = (
        f"Context from SEC filings:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer (bullet points, cite each claim, chronological by period):"
    )

    if on_progress:
        on_progress("generate", "Generating answer with LLM (may take several minutes)...")

    if llm is None:
        llm = LLMClient()
    answer = llm.generate(prompt, system=SYSTEM_PROMPT, max_tokens=config.llm_max_tokens, temperature=config.llm_temperature)
    print(f">>> RAW LLM OUTPUT (first 200 chars): {answer[:200]}")
    if on_progress:
        on_progress("done", "Done!")

    return {
        "question": question,
        "answer": answer,
        "sources": results,
    }


