from typing import List
from openai import OpenAI, APIConnectionError, APIError
from retry import retry
from app.config.settings import settings
from app.core.exceptions import EmbeddingGenerationError
from app.core.interfaces import IEmbeddedGenerator
from app.core.logger import logger


class QwenEmbeddingGenerator(IEmbeddedGenerator):
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.qwen_api_endpoint, api_key=settings.qwen_api_key
        )
        self.model = settings.qwen_embedding_model
        self._dimension = getattr(settings, "qwen_embedding_dimension", 1024)

    @retry(tries=3, delay=2, backoff=2, exceptions=(APIConnectionError, APIError))
    def generate(self, text: str) -> List[float]:
        """Generate embeddings for the given text.

        Args:
            text: Input text to generate embeddings for

        Returns:
            List of floats representing the embedding

        Raises:
            APIError: If the API request fails
            ValueError: If the response is invalid
        """
        if not text.strip():
            raise ValueError("Input text cannot be empty")

        try:
            response = self.client.embeddings.create(input=text, model=self.model)

            if not response.data or not response.data[0].embedding:
                raise EmbeddingGenerationError("Invalid embedding response")

            embedding = response.data[0].embedding

            if len(embedding) != self._dimension:
                logger.warning(
                    f"Embedding dimension mismatch. Expected {self._dimension}, got {len(embedding)}"
                )
                raise EmbeddingGenerationError(
                    f"Embedding dimenstion mismatch. Expected {self._dimension}, got {len(embedding)}"
                )

            return embedding

        except Exception as e:
            logger.error(
                f"Embedding generation failed for text: {text[:100]}... Error: {str(e)}"
            )
            raise

    def get_dimensions(self) -> int:
        """Get the expected embedding dimension."""
        return self._dimension
