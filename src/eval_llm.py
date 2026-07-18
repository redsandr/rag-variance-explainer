"""
LLM output quality evaluation.
Runs the RAG pipeline on eval questions, saves Q&A for faithfulness review.
"""

import argparse
import json
import logging
import time
from pathlib import Path

from llm import LLMClient
from rag import answer_question
from retrieval import get_client, get_collection, query

logger = logging.getLogger(__name__)

EVAL_FILE = Path(__file__).parent.parent / "data" / "eval_questions.json"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "llm_outputs.json"


def load_eval_set(path: Path) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=None, help="Run first N questions")
    parser.add_argument("--ids", nargs="*", default=None, help="Specific eval IDs to run")
    parser.add_argument("--no-generate", action="store_true", help="Skip LLM, only retrieve context")
    args = parser.parse_args()

    eval_set = load_eval_set(EVAL_FILE)

    if args.ids:
        eval_set = [q for q in eval_set if q["id"] in args.ids]
    elif args.sample:
        eval_set = eval_set[: args.sample]

    logger.info("Running %s questions...", len(eval_set))
    if args.no_generate:
        logger.info("  (retrieval only, no LLM generation)")

    LLMClient.reset()
    llm = LLMClient()
    logger.info("Active backend: %s, model loaded once, reused across all questions", llm.backend)
    outputs = []
    for item in eval_set:
        qid = item["id"]
        question = item["question"]
        ticker = item.get("ticker_filter")

        logger.info("\n%s\n[%s] %s\n%s", "=" * 60, qid, question, "=" * 60)

        t0 = time.time()

        if args.no_generate:
            client = get_client()
            collection = get_collection(client)
            results = query(collection, question, top_k=5, ticker_filter=ticker)
            output = {
                "question": question,
                "ticker": ticker,
                "answer": "[SKIPPED - retrieval only]",
                "sources": [
                    {
                        "chunk_id": f"{r['metadata']['ticker']}_{r['metadata']['accession_number']}_{r['metadata']['chunk_index']}",
                        "relevance": r["relevance"],
                        "text_preview": r["text"],
                    }
                    for r in results
                ],
                "retrieval_time_s": round(time.time() - t0, 1),
            }
        else:
            result = answer_question(question, ticker_filter=ticker, top_k=5, llm=llm)
            output = {
                "question": question,
                "ticker": ticker,
                "answer": result["answer"],
                "sources": [
                    {
                        "chunk_id": f"{r['metadata']['ticker']}_{r['metadata']['accession_number']}_{r['metadata']['chunk_index']}",
                        "relevance": r["relevance"],
                        "text_preview": r["text"],
                    }
                    for r in result["sources"]
                ],
                "retrieval_time_s": round(time.time() - t0, 1),
            }

        outputs.append(output)
        logger.info("  Done (%ss)", output["retrieval_time_s"])

    with open(OUTPUT_FILE, "w") as f:
        json.dump(outputs, f, indent=2)

    logger.info("\nSaved to %s", OUTPUT_FILE)
    summary = ["\nSummary:"]
    for o in outputs:
        ans_preview = o["answer"][:100].replace("\n", " ") if not args.no_generate else "[retrieval-only]"
        summary.append(f"  {o['question'][:50]:<52} {ans_preview}...")
    logger.info("\n".join(summary))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
