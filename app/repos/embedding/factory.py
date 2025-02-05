from app.config.settings import settings
from app.core.interfaces import IEmbeddedGenerator
from app.repos.embedding.qwen_embedder import QwenEmbeddingGenerator


class EmbeddingFactory:
    @staticmethod
    def create_embedder() -> IEmbeddedGenerator:
        if settings.embedding_adaptor is  "qwen":
            return QwenEmbeddingGenerator()
        raise ValueError(f"Invalid embedding model: {settings.embedding_model}")
