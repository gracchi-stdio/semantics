from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from chromadb.api.types import Document
from app.core.entities import DocumentChunk, DocumentMetadata


class IVectorStoreRepository(ABC):
    @abstractmethod
    def upsert_chunk(self, chunk: DocumentChunk) -> None:
        pass

    @abstractmethod
    def upsert_chunks(self, chunks: List[DocumentChunk]) -> None:
        pass

    @abstractmethod
    def search(
        self,
        embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        pass


class IMetadataRepository(ABC):
    @abstractmethod
    def get_metadata(self, source_id: str) -> Optional[DocumentMetadata]:
        pass


class IDocumentRepository(ABC):
    @abstractmethod
    def process(self, content: str, metadata: DocumentMetadata) -> List[DocumentChunk]:
        pass


class IEmbeddedGenerator(ABC):
    @abstractmethod
    def generate(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def get_dimensions(self) -> int:
        pass
