from datetime import datetime
from hashlib import sha256
from pydantic import BaseModel, Field, field_validator, ConfigDict, PrivateAttr
from typing import List, Optional

class DocumentMetadata(BaseModel):
    """Core metadata structure with validation."""
    model_config = ConfigDict(extra="forbid", frozen=True)

    # required fields
    zotero_id: str = Field(..., min_length=4, pattern=r"[A-Za-z0-9_-]+", description="Zotero citation Id")
    title: str = Field(..., min_length=4, max_length=100)
    authors: str = Field(..., min_length=1, max_length=300)

    # optional chunk-specific fields
    section_header: Optional[str] = Field(
        None,
        max_length=300,
        examples=["1.2 Algorithms"],
        description="Nested section headers separated by >"
    )
    page_range: Optional[str] = Field(
        None,
        pattern=r"^\d+(\.\d+)*$",
        examples=["44-48"],
        description="Page range in formate start-end or single page number"
    )

    chapter: Optional[str] = Field(
        None,
        max_length=300,
        examples=["Introduction"],
        description="Chapter name"
    )

    # System tracking
    ingestion_date: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Date of ingestion"
    )
    source_version: Optional[str] = Field(
        "v1.0.0",
        pattern=r"^v\d+\.\d+\.\d+$",
    )

    # Custom fields
    tags: str = Field(..., min_length=1)

    language: Optional[str] = Field(
        "en",
        min_length=2,
        max_length=5,
        pattern=r"^[a-z]{2}(-[A-Z]{2})?$",
        examples=["en", "de", "fr-FR"],
        description="Language code in ISO 639-1 format"
    )

    @field_validator('authors')
    def validate_authors(cls, v):
        authors = v.split(';')
        for author in authors:
            if ',' not in author:
                raise ValueError("Author must be in 'LastName, FirstName' format")
            if len(author.split(',')) > 3:
                raise ValueError("Maximum 3 authors supported")
        return v

    @field_validator('tags')
    def normalize_tags(cls, v):
        tags = v.split(',')
        return ",".join([tag.lower().strip() for tag in tags])

    @field_validator("section_header")
    def validate_section_hierarchy(cls, v):
        if v and len(v.split(">")) > 6:
            raise ValueError("Maximum 6 section levels supported")
        return v


class DocumentChunk(BaseModel):
    content: str = Field(..., min_length=1)
    embedding: List[float] = Field(..., min_length=1536)
    metadata: DocumentMetadata
    source_id: str = Field(..., pattern=r"[A-Za-z0-9_-]+")
    created_at: datetime = Field(default_factory=datetime.now)

    _content_hash: str = PrivateAttr()

   # optimizations for higher performace
    model_config = ConfigDict(
        frozen=True, # immutable objects
        extra="forbid",
        validate_default=True,
        arbitrary_types_allowed=False
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


class ProcessedDocument(BaseModel):
    source_id: str = Field(..., pattern=r"[A-Za-z0-9_-]+")
    chunks: List[DocumentChunk] = Field(..., min_length=1)
    processed_at: datetime = Field(default_factory=datetime.now)

    @field_validator("chunks")
    def validate_chunk_source_ids(cls, v, values):
        source_id = values.get('source_id')
        if any(chunk.source_id != source_id for chunk in v):
            raise ValueError("Chunk source ID mismatch")
        return v

def convert_zotero_item(item: dict) -> DocumentMetadata:
    """Convert Zotero API response to our metadata format"""
    return DocumentMetadata(
        zotero_id=item['key'],
        title=item['data']['title'],
        authors=[f"{creator['lastName']}, {creator['firstName']}" for creator in item['data'].get('creators', [])],
        tags=item['data'].get('tags', []),
        source_version=item['version'],
        language=item['data'].get('language', 'en')
    )