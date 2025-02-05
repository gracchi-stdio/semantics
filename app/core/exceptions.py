class EmbeddingError(Exception):
    """Base exception for embedding-related errors"""

class EmbeddingGenerationError(EmbeddingError):
    """Failed to generate embedding"""

class EmbeddingDimensionError(EmbeddingError):
    """Invalid embedding dimensions"""

class DocumentProcessingError(Exception):
    """General document processing error"""