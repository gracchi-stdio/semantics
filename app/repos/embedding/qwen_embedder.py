from openai import OpenAI, APIConnectionError
from retry import retry
from app.config.settings import settings
from app.core.interfaces import IEmbeddedGenerator
from app.core.logger import logger

class QwenEmbeddingGenerator(IEmbeddedGenerator):
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.qwen_api_endpoint,
            api_key=settings.qwen_api_key
        )
        self.model = settings.qwen_embedding_model
        self._dimension = 1536

    @retry(tries=3, delay=2, backoff=2, exceptions=(APIConnectionError,))
    def generate(self, text: str) -> list[float]:
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    def get_dimensions(self) -> int:
        return self._dimension