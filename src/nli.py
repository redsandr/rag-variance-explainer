"""Optional NLI claim verification."""

import gc
import logging

from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


class NLIClient:
    """NLI engine for claim verification.

    Wraps a CrossEncoder model from sentence-transformers.
    Model is lazy-loaded on first use to avoid import-time memory spike.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/nli-deberta-v3-large",
        device: str = "cpu",
        threshold: float = 0.40,
    ) -> None:
        self._model_name = model_name
        self._device = device
        self.threshold = threshold
        self._model: CrossEncoder | None = None
        self._label_mapping: tuple[str, ...] = ()

    def _load(self) -> None:
        if self._model is not None:
            return
        try:
            logger.info(
                "Loading NLI model: %s on %s (first load ~1.5GB download)",
                self._model_name,
                self._device,
            )
            self._model = CrossEncoder(
                self._model_name,
                device=self._device,
                max_length=512,
            )
            transformer_model = self._model.model
            model_config = getattr(transformer_model, "config", None)
            id2label = getattr(model_config, "id2label", None)
            if id2label:
                self._label_mapping = tuple(id2label[i] for i in sorted(id2label))
            else:
                self._label_mapping = ("contradiction", "entailment", "neutral")
            logger.debug("NLI label mapping: %s", self._label_mapping)
        except Exception:
            logger.exception("Failed to load NLI model %s", self._model_name)
            raise

    def _predict(self, premise: str, hypothesis: str) -> dict:
        """Run NLI on one passage and claim using the model's label mapping."""
        model = self._model
        if model is None:
            raise RuntimeError("NLI model is not loaded")
        logits = model.predict([(premise, hypothesis)], apply_softmax=True, show_progress_bar=False)
        scores = logits[0]
        label_idx = int(scores.argmax())
        mapping = self._label_mapping or ("contradiction", "entailment", "neutral")
        label = mapping[label_idx]
        score = float(scores[label_idx])
        entail_idx = mapping.index("entailment")
        entailment_score = float(scores[entail_idx])

        return {
            "label": label,
            "score": score,
            "entailment_score": entailment_score,
        }

    def verify(
        self,
        claim: str,
        chunk_texts: list[str],
        threshold: float | None = None,
    ) -> dict:
        """Verify a single claim against a list of chunk texts.

        Chunk texts are treated as *premise*, claim as *hypothesis*.

        Returns dict with:
            - claim: the input claim
            - verdict: "entailment" | "contradiction" | "neutral"
            - confidence: score for the winning label
            - max_entailment: maximum entailment score across chunks
            - supported: True if max_entailment >= threshold
        """
        self._load()
        threshold = threshold if threshold is not None else self.threshold

        max_entailment = 0.0
        best_label = "neutral"
        best_score = 0.0
        strongest_entailing_score = 0.0
        strongest_contradiction_score = 0.0

        for chunk_text in chunk_texts:
            try:
                result = self._predict(chunk_text, claim)
                label = result["label"]
                score = result["score"]
                entail = result["entailment_score"]

                if entail > max_entailment:
                    max_entailment = entail
                if label == "entailment":
                    strongest_entailing_score = max(strongest_entailing_score, score)
                if label == "contradiction":
                    strongest_contradiction_score = max(strongest_contradiction_score, score)
                if score > best_score:
                    best_score = score
                    best_label = label
            except (RuntimeError, ValueError, IndexError, AttributeError) as e:
                logger.warning("NLI inference error for claim: %s — %s", claim[:80], e)
                continue

        if strongest_entailing_score >= threshold and strongest_entailing_score > strongest_contradiction_score:
            best_label = "entailment"
            best_score = strongest_entailing_score
        elif strongest_contradiction_score > 0 and strongest_contradiction_score >= strongest_entailing_score:
            best_label = "contradiction"
            best_score = strongest_contradiction_score

        return {
            "claim": claim,
            "verdict": best_label,
            "confidence": best_score,
            "max_entailment": max_entailment,
            "supported": best_label == "entailment" and max_entailment >= threshold,
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
        self._model = None
        gc.collect()
        logger.debug("NLI model unloaded")
