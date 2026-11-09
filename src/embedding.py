"""
Embedding wrapper around nomic-embed-text (768-dim), loaded locally via
sentence-transformers
"""

import logging
import threading

from sentence_transformers import SentenceTransformer

from config import config
from logging_config import log_timer

logger = logging.getLogger(__name__)

_MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"   # 768-dim
_TARGET_DIM = 768


class EmbeddingModel:
    """Thread-safe singleton wrapper for nomic-embed model."""
    _instance: "EmbeddingModel | None" = None
    _lock = threading.Lock()
    _load_lock = threading.Lock()
    _model: SentenceTransformer | None

    def __new__(cls) -> "EmbeddingModel":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._model = None
        return cls._instance

    def get_model(self) -> SentenceTransformer:
        model = self._model
        if model is not None:
            return model
        with self._load_lock:
            model = self._model
            if model is None:
                model = SentenceTransformer(_MODEL_NAME, trust_remote_code=True, device=config.embedding_device)
                logger.info("Loaded embedding model: %s on %s", _MODEL_NAME, config.embedding_device)
                dim = model.get_sentence_embedding_dimension()
                if dim != _TARGET_DIM:
                    raise RuntimeError(f"Embedding model {_MODEL_NAME} has dimension {dim}; expected {_TARGET_DIM}.")
                self._model = model
        return model


_embedding_model = EmbeddingModel()


def embed_documents(texts: list[str]) -> list[list[float]]:
    """
    Embed a batch of document chunks for indexing (e.g. MD&A chunks
    going into ChromaDB). Applies the required "search_document:" prefix.
    """
    model = _embedding_model.get_model()
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
    model = _embedding_model.get_model()
    prefixed = f"search_query: {text}"
    with log_timer(logger, "embed.query"):
        embedding = model.encode([prefixed], normalize_embeddings=True)
    return embedding[0].tolist()


