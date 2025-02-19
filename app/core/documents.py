from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
from pydantic import (
    BaseModel,
    Field,
    ValidationInfo,
    field_validator,
    ConfigDict,
    PrivateAttr,
)
from typing import List, Optional


@dataclass(frozen=True)
class DocumentMetadata:
    """Core metadata structure with validation."""

    zotero_id: str
    title: str
    authors: str
    section_header: Optional[str] = None  # nested section header separated by '>'
    page_range: Optional[str] = None
    chapter: Optional[str] = None
    ingestion_data: datetime = field(default_factory=datetime.now)
    source_version: str = "v1.0.0"
    tags: str = ""
    language: str = "en"


class DocumentChunk(BaseModel):
    content: str = Field(..., min_length=1)
    embedding: List[float] = Field(..., min_length=500)
    metadata: DocumentMetadata
    source_id: str = Field(..., pattern=r"[A-Za-z0-9_-]+")
    created_at: datetime = Field(default_factory=datetime.now)

    _content_hash: str = PrivateAttr()

    # optimizations for higher performace
    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        arbitrary_types_allowed=True,
    )

    def __init__(self, **data):
        """
        Custom initialization to automatically compute and set the internal content_hash.
        """
        super().__init__(**data)
        # Compute content_hash automatically and set to the private attribute
        self._content_hash = sha256(self.content.encode()).hexdigest()

    @property
    def content_hash(self) -> str:
        """
        Publicly expose content_hash as a read-only property.
        """
        return self._content_hash

    @field_validator("source_id")
    def validate_chunk_source_ids(cls, v, values: ValidationInfo):
        """Validate that source_id matches parent document's ID"""

        parent_source_id = values.data.get("source_id")
        if parent_source_id and v != parent_source_id:
            raise ValueError(
                f"Chunk source_id {v} mismatch with parent {parent_source_id}"
            )
        return v


@dataclass
class ProcessedDocument:
    source_id: str = Field(..., pattern=r"[A-Za-z0-9_-]+")
    chunks: List[DocumentChunk] = Field(..., min_length=1)
    processed_at: datetime = Field(default_factory=datetime.now)

    @field_validator("chunks")
    def validate_chunk_source_ids(cls, v, values: ValidationInfo):
        source_id = values.data.get("source_id")
        if any(chunk.source_id != source_id for chunk in v):
            raise ValueError("Chunk source ID mismatch")
        return v
