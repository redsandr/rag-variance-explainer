"""
NLI-based claim verification using DeBERTa-v3-large.
Lazy-loaded, batch-aware, configurable threshold.
"""

import gc
import logging
from typing import Any

logger = logging.getLogger(__name__)


class NLIClient:
    """NLI engine for claim verification.

    Wraps a DeBERTa-v3-large model from HuggingFace transformers.
    Model is lazy-loaded on first use to avoid import-time memory spike.
    """

    def __init__(
        self,
        model_name: str = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
        device: str = "cpu",
        threshold: float = 0.72,
    ) -> None:
        self._model_name = model_name
        self._device = device
        self.threshold = threshold
        self._pipeline: Any = None

    def _load(self) -> None:
        if self._pipeline is not None:
            return
        try:
            from transformers import pipeline as hf_pipeline

            logger.info(
                "Loading NLI model: %s on %s (first load ~1.5GB download)",
                self._model_name,
                self._device,
            )
            self._pipeline = hf_pipeline(
                "text-classification",
                model=self._model_name,
                device=self._device,
                truncation=True,
                max_length=512,
                top_k=None,
            )
        except Exception:
            logger.exception("Failed to load NLI model %s", self._model_name)
            raise

    def verify(
        self,
        claim: str,
        chunk_texts: list[str],
        threshold: float | None = None,
    ) -> dict:
        """Verify a single claim against a list of chunk texts.

        Returns dict with:
            - claim: the input claim
            - verdict: "ENTAILMENT" | "CONTRADICTION" | "NEUTRAL"
            - confidence: score for the winning label
            - max_entailment: maximum entailment score across chunks
            - supported: True if max_entailment >= threshold
        """
        self._load()
        threshold = threshold if threshold is not None else self.threshold

        max_entailment = 0.0
        best_label = "NEUTRAL"
        best_score = 0.0

        for chunk_text in chunk_texts:
            try:
                results = self._pipeline(f"{claim} </s></s> {chunk_text}")
                if isinstance(results, list) and len(results) > 0:
                    scores = results[0] if isinstance(results[0], dict) else results
                    if isinstance(scores, list):
                        scores = scores[0]
                    if isinstance(scores, dict):
                        label, score = scores.get("label", "NEUTRAL"), scores.get("score", 0.0)
                    else:
                        label, score = "NEUTRAL", 0.0
                elif isinstance(results, dict):
                    label, score = results.get("label", "NEUTRAL"), results.get("score", 0.0)
                else:
                    label, score = "NEUTRAL", 0.0

                if label == "ENTAILMENT" and score > max_entailment:
                    max_entailment = score
                if score > best_score:
                    best_score = score
                    best_label = label
            except Exception:
                logger.warning("NLI inference error for claim: %s", claim[:80])
                continue

        return {
            "claim": claim,
            "verdict": best_label,
            "confidence": best_score,
            "max_entailment": max_entailment,
            "supported": max_entailment >= threshold,
        }

    def verify_batch(
        self,
        claims: list[str],
        chunk_texts: list[str],
        threshold: float | None = None,
    ) -> list[dict]:
        """Verify multiple claims against a common set of chunk texts."""
        return [self.verify(c, chunk_texts, threshold) for c in claims]

    def unload(self) -> None:
        """Release model from memory."""
        self._pipeline = None
        gc.collect()
        logger.debug("NLI model unloaded")
