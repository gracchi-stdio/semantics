from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.core.documents import DocumentChunk, DocumentMetadata


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
    def get_metadata(self, source_id: str) -> DocumentMetadata | None:
        pass


class ILibraryManagerRepository(ABC):
    @abstractmethod
    def get_metadata(self, source_id: str) -> DocumentMetadata | None:
        pass

    @abstractmethod
    def get_source_content(self, parent_id: str) -> str | None:
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
