from dataclasses import asdict
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from tqdm import tqdm

from app.config.settings import settings
from app.core.documents import DocumentMetadata, DocumentChunk
from app.core.logger import logger


class MarkdownProcessor:
    def __init__(
        self,
        embedder,
        headers_to_split=None,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    ):
        if headers_to_split is None:
            headers_to_split = [("#", "Header1"), ("##", "Header2"), ("###", "Header3")]

        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split, strip_headers=False
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
        )
        self.embedder = embedder

    def _build_section_hierarchy(self, metadata: dict) -> str:
        """Build section hierarchy from header metadata."""
        return " > ".join(
            metadata[header]
            for header in ["Header1", "Header2", "Header3"]
            if metadata.get(header)
        )

    def _convert_metadata(self, md_metadata: dict) -> DocumentMetadata:
        return DocumentMetadata(
            zotero_id=md_metadata.get("zotero_id", ""),
            title=md_metadata.get("Header1", ""),
            authors=md_metadata.get("authors", ""),
            tags=md_metadata.get("tags", ""),
            section_header=self._build_section_hierarchy(md_metadata),
            chapter=md_metadata.get("Header2", ""),
            page_range=md_metadata.get("page_range", ""),
        )

    def process(
        self, content: str, source_metadata: DocumentMetadata
    ) -> List[DocumentChunk]:
        # Convert dataclass to dict First
        source_metadata_dict = asdict(source_metadata)
        logger.info(f"Processing content length: {len(content)} characters")
        logger.debug(f"Content sample: {content[:200]}...")

        print(content)
        # Test
        # test_split = self.header_splitter.split_text("# Test\nContent")
        # logger.info(f"Test header split result: {len(test_split)} chunks")

        # First split by headers
        try:
            header_splits = self.header_splitter.split_text(content)
            logger.debug(f"Initial header splits: {len(header_splits)}")
        except Exception as e:
            logger.warning(
                f"Header splitting failed: {e}. Using full content as fallback."
            )
            header_splits = [Document(page_content=content, metadata={})]

        # Fallback for empty header splits
        if not header_splits:
            logger.warning("No header splits. Creating single chunk from full content")
            header_splits = [Document(page_content=content, metadata={})]

        final_chunks = []
        for split in tqdm(header_splits, desc="Splitting content"):
            if not split.page_content.strip():
                logger.debug("Skipping empty split")
                continue

            try:
                text_splits = self.text_splitter.split_documents([split])
                logger.debug(f"Text splits from header section: {len(text_splits)}")
            except Exception as e:
                logger.warning(f"Text splitting failed: {e}. Using original split")
                text_splits = [split]

            combine_metadata = {**source_metadata_dict, **split.metadata}
            # Handke empty content after stripping
            if not split.page_content.strip():
                continue

            # text_splits = self.text_splitter.split_documents([split])

            # Ensure at least one chink per split
            if not text_splits:
                text_splits = [split]

            for text_split in text_splits:
                if not text_split.page_content.strip():
                    continue

                chunk_metadata = self._convert_metadata(
                    {**combine_metadata, **text_split.metadata}
                )
                logger.debug(
                    "Processign chunk metadata",
                    extra={"chunk_metadata": chunk_metadata},
                )

                embedding = self.embedder.generate(text_split.page_content)
                final_chunks.append(
                    DocumentChunk(
                        content=text_split.page_content,
                        metadata=chunk_metadata,
                        source_id=source_metadata.zotero_id,
                        embedding=embedding,
                    )
                )

        # Add before final return
        if not final_chunks:
            logger.critical("No chunks generated - creating minimal emergency chunk")
            emergency_content = content.strip() or "Empty document content"
            return [
                DocumentChunk(
                    content=emergency_content[:1000],
                    metadata=source_metadata,
                    source_id=source_metadata.zotero_id,
                    embedding=self.embedder.generate(emergency_content[:1000]),
                )
            ]
        return final_chunks
