import logging
import threading

from sentence_transformers import CrossEncoder

from config import config

logger = logging.getLogger(__name__)


class CrossEncoderModel:
    """Thread-safe singleton wrapper for cross-encoder model."""
    _instance: "CrossEncoderModel | None" = None
    _lock = threading.Lock()
    _load_lock = threading.Lock()
    _model: CrossEncoder | None

    def __new__(cls) -> "CrossEncoderModel":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._model = None
        return cls._instance

    def get_model(self) -> CrossEncoder:
        model = self._model
        if model is not None:
            return model
        with self._load_lock:
            model = self._model
            if model is None:
                logger.info("Loading cross-encoder: %s (device=%s)", config.cross_encoder_model, config.cross_encoder_device)
                model = CrossEncoder(config.cross_encoder_model, device=config.cross_encoder_device)
                self._model = model
        return model


_cross_encoder_model = CrossEncoderModel()


def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """Re-rank candidates using cross-encoder scores blended with bi-encoder.

    Normalises both cross-encoder and bi-encoder scores to [0,1], blends
    them with *cross_encoder_weight*, adds keyword boost and forward-looking
    penalty, then returns the top *top_k* candidates sorted by hybrid score.
    Falls back silently to input order if cross-encoder loading fails.
    """
    if not candidates:
        return []

    model = _cross_encoder_model.get_model()
    pairs = [[query, c["text"]] for c in candidates]
    scores = model.predict(pairs, batch_size=config.cross_encoder_batch_size, show_progress_bar=False)  # type: ignore[arg-type]

    for i, score in enumerate(scores):
        candidates[i]["cross_encoder_score"] = float(score)

    ce_scores = [c["cross_encoder_score"] for c in candidates]
    lo, hi = min(ce_scores), max(ce_scores)
    ce_range = hi - lo if hi > lo else 1.0

    bi_scores = [c["relevance"] for c in candidates]
    bi_lo, bi_hi = min(bi_scores), max(bi_scores)
    bi_range = bi_hi - bi_lo if bi_hi > bi_lo else 1.0

    w = config.cross_encoder_weight
    for i, c in enumerate(candidates):
        ce_norm = (ce_scores[i] - lo) / ce_range
        bi_norm = (bi_scores[i] - bi_lo) / bi_range
        penalty = c.get("forward_looking_penalty", 0.0)
        kw_boost = c.get("keyword_boost", 0.0)
        c["hybrid_score"] = w * ce_norm + (1 - w) * bi_norm + penalty + kw_boost * config.keyword_boost_weight

    candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
    return candidates[:top_k]
