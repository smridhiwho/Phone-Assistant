import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer
import pickle

from app.config import get_settings

settings = get_settings()


class EmbeddingService:
    """Service for generating and managing embeddings."""

    def __init__(self):
        self.model_name = settings.embedding_model
        self.model: Optional[SentenceTransformer] = None
        self._initialized = False

    def initialize(self):
        """Initialize the embedding model."""
        if self._initialized:
            return

        try:
            self.model = SentenceTransformer(self.model_name)
            self._initialized = True
        except Exception as e:
            print(f"Failed to load embedding model: {e}")
            self.model = None

    def encode(self, text: str) -> Optional[np.ndarray]:
        """Encode text to embedding vector."""
        self.initialize()
        if not self.model:
            return None

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            print(f"Encoding error: {e}")
            return None

    def encode_batch(self, texts: List[str]) -> Optional[np.ndarray]:
        """Encode multiple texts to embedding vectors."""
        self.initialize()
        if not self.model:
            return None

        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            print(f"Batch encoding error: {e}")
            return None

    def compute_similarity(
        self,
        query_embedding: np.ndarray,
        embeddings: np.ndarray
    ) -> np.ndarray:
        """Compute cosine similarity between query and embeddings."""
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        similarities = np.dot(embeddings_norm, query_norm)
        return similarities

    def serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """Serialize embedding for database storage."""
        return pickle.dumps(embedding)

    def deserialize_embedding(self, data: bytes) -> np.ndarray:
        """Deserialize embedding from database storage."""
        return pickle.loads(data)

    @property
    def is_available(self) -> bool:
        """Check if the embedding service is available."""
        self.initialize()
        return self.model is not None


_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
