from typing import List, Tuple

from langchain_text_splitters import MarkdownTextSplitter, MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from app.config.settings import settings
from app.core.entities import DocumentMetadata, DocumentChunk
from app.core.logger import logger


class MarkdownProcessor:
    def __init__(self, headers_to_split=None, chunk_size = settings.chunk_size, chunk_overlap = settings.chunk_overlap):
        if headers_to_split is None:
            headers_to_split = [
                ("#", "Header1"),
                ("##", "Header2"),
                ("###", "Header3")
            ]

        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split,
            strip_headers=False
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )

    def _convert_metadata(self, md_metadata: dict) -> DocumentMetadata:
        """Convert splitter metadata to our DocumentMetadata object."""
        return DocumentMetadata(
            zotero_id=md_metadata.get("zotero_id", ""),
            title=md_metadata.get("Header1", ""),
            authors=md_metadata.get("authors", ""),
            tags=md_metadata.get("tags", ""),
            section_header= self._build_section_hierarchy(md_metadata),
            chapter=md_metadata.get("Header 2", ""),
            page_range=md_metadata.get("page_range", ""),
        )


    def _build_section_hierarchy(self, metadata: dict) -> str:
        """Build section hierarchy from header metadata."""
        return " > ".join(
            metadata[header]
            for header in ["Header 1", "Header 2", "Header 3"]
            if metadata.get(header)
        )

    def process(self, content: str, source_metadata: dict) -> List[DocumentChunk]:
        # First split by headers
        header_splits = self.header_splitter.split_text(content)

        final_chunks = []
        for split in header_splits:
            combine_metadata = {
                **source_metadata,
                **split.metadata
            }

            text_splits = self.text_splitter.split_documents([split])

            for text_split in text_splits:
                chunk_metadata = self._convert_metadata({
                    **combine_metadata,
                    **text_split.metadata
                })
                print("meta: ", combine_metadata, text_split.metadata, chunk_metadata)

                final_chunks.append(
                   DocumentChunk(
                       content=text_split.page_content,
                       metadata=chunk_metadata,
                       source_id=source_metadata.get("zotero_id"),
                       embedding=[]
                   )
                )
        return final_chunks