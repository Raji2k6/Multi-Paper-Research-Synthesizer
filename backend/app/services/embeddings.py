from sentence_transformers import SentenceTransformer
from functools import lru_cache
from sklearn.feature_extraction.text import HashingVectorizer

from app.core.config import settings
from app.core.database import engine


@lru_cache
def get_embedding_model():
    """
    Load the embedding model only once.
    """
    return SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache
def get_hashing_vectorizer():
    return HashingVectorizer(
        n_features=384,
        alternate_sign=False,
        norm="l2",
        ngram_range=(1, 2),
        token_pattern=r"(?u)\b\w+\b",
    )


def _use_hashing_embeddings() -> bool:
    backend = settings.EMBEDDING_BACKEND.lower()
    if backend == "auto":
        return engine.dialect.name == "sqlite"
    if backend in {"hashing", "sentence-transformers"}:
        return backend == "hashing"
    raise ValueError(
        "EMBEDDING_BACKEND must be 'auto', 'hashing', or 'sentence-transformers'."
    )


def generate_embedding(text: str) -> list[float]:
    """
    Generate a local 384-dimensional embedding for the given text.
    """
    if _use_hashing_embeddings():
        return get_hashing_vectorizer().transform([text]).toarray()[0].tolist()

    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)

    return embedding.tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple text chunks.
    """
    if _use_hashing_embeddings():
        return get_hashing_vectorizer().transform(texts).toarray().tolist()

    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True)

    return embeddings.tolist()