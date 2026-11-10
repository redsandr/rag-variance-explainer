from unittest.mock import MagicMock, patch

from src.embedding import EmbeddingModel


def test_nomic_loads_pinned_custom_code_and_checks_dimension() -> None:
    model = MagicMock(spec=["get_sentence_embedding_dimension"])
    model.get_sentence_embedding_dimension.return_value = 768
    embedding = object.__new__(EmbeddingModel)
    embedding._model = None

    with patch("src.embedding.SentenceTransformer", return_value=model) as loader:
        assert embedding.get_model() is model

    assert loader.call_args.kwargs["trust_remote_code"] is True
    assert loader.call_args.kwargs["revision"] == "e9b6763023c676ca8431644204f50c2b100d9aab"
    model.get_sentence_embedding_dimension.assert_called_once_with()
