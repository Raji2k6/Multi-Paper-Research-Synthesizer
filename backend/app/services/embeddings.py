from sentence_transformers import SentenceTransformer
from functools import lru_cache


@lru_cache
def get_embedding_model():
    """
    Load the embedding model only once.
    """
    return SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str) -> list[float]:
    """
    Generate a 384-dimensional embedding for the given text.
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)

    return embedding.tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple text chunks.
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True)

    return embeddings.tolist()