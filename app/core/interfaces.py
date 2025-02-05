from abc import ABC, abstractmethod
from typing import List

from anyio.abc import Listener

from app.core.entities import DocumentChunk


class IVectorStoreRepository(ABC):
    @abstractmethod
    def upsert_chunk(self, chunk: DocumentChunk) -> None:
        pass

    @abstractmethod
    def search(self, embedding: List[float], top_k: int, filters: dict) -> List[DocumentChunk]:
        pass

class IMetadataRepository(ABC):
    @abstractmethod
    def get_metadata(self, source_id: str) -> dict:
        pass

class IDocumentRepository(ABC):
    @abstractmethod
    def process(self, content: str, metadata: str) -> List[DocumentChunk]:
        pass

class IEmbeddedGenerator(ABC):
    @abstractmethod
    def generate(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def get_dimensions(self) -> int:
        pass