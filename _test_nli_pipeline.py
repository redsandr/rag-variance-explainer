"""Quick end-to-end NLI pipeline test."""
from rag import answer_question

r = answer_question("What was CMG revenue in Q3 2024?", ticker_filter="CMG", top_k=5)
print("Answer:", (r.get("answer") or "")[:200])
print("Structured:", r.get("structured"))
s = r.get("nli_summary")
print("NLI summary:", s)
vs = r.get("nli_verdicts") or []
for v in vs:
    print(f"  [{v['verdict']}] sup={v['supported']} entail={v['max_entailment']:.3f}  {v['claim'][:80]}")
