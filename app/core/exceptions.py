class CustomException(Exception):
    """Base class for custom exceptions in the application."""

    pass


class EmbeddingError(CustomException):
    """Base exception for embedding-related errors."""

    pass


class EmbeddingGenerationError(EmbeddingError):
    """Failed to generate embedding."""

    pass


class EmbeddingDimensionError(EmbeddingError):
    """Invalid embedding dimensions."""

    pass


class DocumentProcessingError(CustomException):
    """General document processing error."""

    pass


class VectorStoreError(CustomException):
    """General vector store error."""

    pass


class VectorStoreQueryError(VectorStoreError):
    """Error during vector store query."""

    pass
