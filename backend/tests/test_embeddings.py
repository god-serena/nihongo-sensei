from unittest.mock import MagicMock, patch
import numpy as np
from app.embeddings import EmbeddingGenerator


def test_embedding_generator_init():
    with patch("app.embeddings.SentenceTransformer") as mock_st:
        EmbeddingGenerator(model_name="test-model")
        mock_st.assert_called_once_with("test-model")


def test_generate_embeddings():
    with patch("app.embeddings.SentenceTransformer") as mock_st:
        mock_model = MagicMock()
        mock_model.encode.return_value = [
            np.array([0.1, 0.2, 0.3]),
            np.array([0.4, 0.5, 0.6])
        ]
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        texts = ["hello", "world"]
        embeddings = generator.generate_embeddings(texts)

        assert embeddings == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_model.encode.assert_called_once_with(texts)


def test_generate_embeddings_empty():
    with patch("app.embeddings.SentenceTransformer"):
        generator = EmbeddingGenerator()
        assert generator.generate_embeddings([]) == []

def test_generate_embedding_single():
    with patch("app.embeddings.SentenceTransformer") as mock_st:
        mock_model = MagicMock()
        mock_model.encode.return_value = [np.array([0.1, 0.2, 0.3])]
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        embedding = generator.generate_embedding("hello")
        assert embedding == [0.1, 0.2, 0.3]
