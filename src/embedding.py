"""
Embedding wrapper around nomic-embed-text (768-dim), loaded locally via
sentence-transformers
"""

import logging

from sentence_transformers import SentenceTransformer
logger = logging.getLogger(__name__)

_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"
_model = None  # lazy-loaded singleton — avoid reloading the model on every call


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME, trust_remote_code=True)
    return _model


def embed_documents(texts: list[str]) -> list[list[float]]:
    """
    Embed a batch of document chunks for indexing (e.g. MD&A chunks
    going into ChromaDB). Applies the required "search_document:" prefix.
    """
    model = _get_model()
    prefixed = [f"search_document: {t}" for t in texts]
    embeddings = model.encode(prefixed, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(text: str) -> list[float]:
    """
    Embed a single user query at retrieval time. Applies the required
    "search_query:" prefix — NOT the same prefix as embed_documents,
    since nomic-embed-text treats these as distinct roles.
    """
    model = _get_model()
    prefixed = f"search_query: {text}"
    embedding = model.encode([prefixed], normalize_embeddings=True)
    return embedding[0].tolist()


