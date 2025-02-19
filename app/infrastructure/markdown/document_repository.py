from typing import List
from app.core.documents import DocumentChunk, DocumentMetadata
from app.core.interfaces import IDocumentRepository, IEmbeddedGenerator
from app.core.logger import logger
from app.infrastructure.markdown.processor import MarkdownProcessor


class MarkdownDocumentRepository(IDocumentRepository):
    """Markdown processing implementation with chunking"""

    def __init__(self, embedder: IEmbeddedGenerator):
        self.processor = MarkdownProcessor(embedder=embedder)
        self.validation_enabled = True

    def process(self, content: str, metadata: DocumentMetadata) -> List[DocumentChunk]:
        try:
            if not content.strip():
                logger.warning("Empty content received for processing")
                return []

            return self.processor.process(content=content, source_metadata=metadata)

        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise
