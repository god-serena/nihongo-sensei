from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    """
    Local embedding generator using sentence-transformers.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts)
        # Convert numpy arrays to standard python lists
        return [em.tolist() for em in embeddings]

    def generate_embedding(self, text: str) -> list[float]:
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else []
