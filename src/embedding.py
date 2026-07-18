"""
Embedding wrapper around nomic-embed-text (768-dim), loaded locally via
sentence-transformers
"""

import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"
_FALLBACK_MODEL = "all-MiniLM-L6-v2"  # significantly smaller, loads when nomic fails
_model = None  # lazy-loaded singleton — avoid reloading the model on every call


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        try:
            _model = SentenceTransformer(_MODEL_NAME, trust_remote_code=True, device="cpu")
            logger.info("Loaded embedding model: %s", _MODEL_NAME)
        except Exception as e:
            logger.warning(
                "Failed to load %s: %s. Falling back to %s.",
                _MODEL_NAME, e, _FALLBACK_MODEL,
            )
            _model = SentenceTransformer(_FALLBACK_MODEL, device="cpu")
            logger.info("Loaded fallback embedding model: %s", _FALLBACK_MODEL)
    return _model


def embed_documents(texts: list[str]) -> list[list[float]]:
    """
    Embed a batch of document chunks for indexing (e.g. MD&A chunks
    going into ChromaDB). Applies the required "search_document:" prefix.
    """
    from logging_config import log_timer

    model = _get_model()
    prefixed = [f"search_document: {t}" for t in texts]
    with log_timer(logger, f"embed.{len(texts)}docs"):
        embeddings = model.encode(prefixed, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(text: str) -> list[float]:
    """
    Embed a single user query at retrieval time. Applies the required
    "search_query:" prefix — NOT the same prefix as embed_documents,
    since nomic-embed-text treats these as distinct roles.
    """
    from logging_config import log_timer

    model = _get_model()
    prefixed = f"search_query: {text}"
    with log_timer(logger, "embed.query"):
        embedding = model.encode([prefixed], normalize_embeddings=True)
    return embedding[0].tolist()


