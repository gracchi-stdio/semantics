from app.config.settings import settings
from app.core.interfaces import IEmbeddedGenerator
from app.infrastructure.embedding.qwen_embedder import QwenEmbeddingGenerator


class EmbeddingFactory:
    @staticmethod
    def create_embedder() -> IEmbeddedGenerator:
        embedding_adaptor = settings.embedding_adaptor
        if embedding_adaptor == "qwen":
            return QwenEmbeddingGenerator()
        raise ValueError(f"Invalid embedding model: {embedding_adaptor}")
