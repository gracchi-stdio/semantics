from typing import List
from app.core.documents import DocumentChunk
from app.core.interfaces import IDocumentRepository, IEmbeddedGenerator
from app.services.markdown.processor import MarkdownProcessor
from app.core.logger import logger


class MarkdownDocumentRepo(IDocumentRepository):
    """Markdown processing implementation with chunking"""

    def __init__(self, embedder: IEmbeddedGenerator):
        self.processor = MarkdownProcessor(embedder=embedder)
        self.validation_enabled = True

    def process(self, content: str, metadata: dict) -> List[DocumentChunk]:
        try:
            if not content.strip():
                logger.warning("Empty content received for processing")
                return []

            return self.processor.process(content=content, source_metadata=metadata)

        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise
