from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel


class MarkdownPage(BaseModel):
    content: str
    page: Optional[int] = None
    chapter: Optional[str] = None
    section: Optional[str] = None


class ParagraphChunk(BaseModel):
    content: str
    page: Optional[int] = None
    chapter: Optional[str] = None
    section: Optional[str] = None


class IDocumentConverter(ABC):
    """
    Abstract base class for document converters.
    """

    @abstractmethod
    def convert(self, file_path: str) -> str:
        pass

    @abstractmethod
    def chunk_by_page(self, markdown_content: str) -> List[MarkdownPage]:
        pass
