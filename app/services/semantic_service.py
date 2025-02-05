from typing import Optional

from app.core.entities import DocumentMetadata
from app.core.interfaces import IVectorStoreRepository, IEmbeddedGenerator
from app.repos.vector_store.factory import VectorStoreFactory
from app.services.markdown.processor import MarkdownProcessor


class SemanticService:
    def __init__(self, vector_store: IVectorStoreRepository,  embedder: IEmbeddedGenerator, markdown_parser: MarkdownProcessor):
        self.vector_store = vector_store or VectorStoreFactory.create_store()
        self.embedder = embedder
        self.markdown_parser = markdown_parser or MarkdownProcessor()

    def ingest_document(self, content: str, metadata: DocumentMetadata) -> int:
        """Return number of chunks processed"""
        md_metadata = metadata.model_dump()

        chunks = self.markdown_parser.process(content, md_metadata)
        for chunk in chunks:
            chunk.embedding = self.embedder.generate(chunk.content)
            self.vector_store.upsert_chunk(chunk)
        return len(chunks)

    def query(self, text: str, source_filter: str = None) -> list:
        """Query documents with optional source filter"""
        pass