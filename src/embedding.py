"""
Embedding wrapper around nomic-embed-text (768-dim), loaded locally via
sentence-transformers
"""

import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"   # 768-dim
_FALLBACK_MODEL = "all-MiniLM-L6-v2"              # 384-dim — can NOT be used for upsert
_MODEL = None  # lazy-loaded singleton

_TARGET_DIM = 768


def _get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        try:
            _MODEL = SentenceTransformer(_MODEL_NAME, trust_remote_code=True, device="cpu")
            logger.info("Loaded embedding model: %s", _MODEL_NAME)
        except Exception as e:
            logger.warning(
                "Failed to load %s: %s. Falling back to %s.",
                _MODEL_NAME, e, _FALLBACK_MODEL,
            )
            fallback = SentenceTransformer(_FALLBACK_MODEL, device="cpu")
            dim = fallback.get_sentence_embedding_dimension()
            if dim != _TARGET_DIM:
                raise RuntimeError(
                    f"Embedding fallback model {_FALLBACK_MODEL} has dimension {dim}, "
                    f"but ChromaDB collection requires {_TARGET_DIM}. "
                    f"Load {_MODEL_NAME} manually or use a {_TARGET_DIM}-dim fallback."
                ) from e
            _MODEL = fallback
            logger.info("Loaded fallback embedding model: %s", _FALLBACK_MODEL)
    return _MODEL


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


