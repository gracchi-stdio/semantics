from typing import Optional

from app.core.documents import ProcessedDocument
from app.core.exceptions import DocumentProcessingError
from app.core.interfaces import (
    IDocumentRepository,
    IEmbeddedGenerator,
    ILibraryManagerRepository,
    IVectorStoreRepository,
)
from app.core.logger import logger
from tqdm import tqdm


class SemanticService:
    def __init__(
        self,
        vector_store: IVectorStoreRepository,
        embedder: IEmbeddedGenerator,
        processor: IDocumentRepository,
        library_manager: ILibraryManagerRepository,
    ):
        self.vector_store = vector_store
        self.embedder = embedder
        self.processor = processor
        self.library_manager = library_manager

    def process_zotero_item(self, zotero_id: str) -> ProcessedDocument | None:
        try:
            content = self.library_manager.get_source_content(zotero_id)
            if content is None:
                return None
        except Exception as e:
            logger.error(
                f"Something happened during retriving the content from zotero: {e}"
            )
            raise

        return self.process_document(zotero_id, content)

    def process_document(self, source_id, content: str) -> Optional[ProcessedDocument]:
        if not content.strip():
            logger.error("Empty content provided")
            return None

        try:
            # 1. Fetch metadata
            metadata = self.library_manager.get_metadata(source_id)
            if not metadata:
                logger.error(f"Metadata not found for {source_id}")
                return None

            # 2. process content
            raw_chunks = self.processor.process(content, metadata)
            if not raw_chunks:
                logger.error(f"No chunks generated for {source_id}")
                return None

            # 3. Generate embedding
            processed_chunks = []
            for chunk in tqdm(raw_chunks, desc="Processing embedding"):
                try:
                    embedding = self.embedder.generate(chunk.content)
                    if (
                        not embedding
                        or len(embedding) != self.embedder.get_dimensions()
                    ):  # Add null check
                        logger.error(
                            f"Empty embedding for chunk: {chunk.content[:50]}..."
                        )
                        continue

                    chunk.embedding = embedding
                    processed_chunks.append(chunk)
                except Exception as e:
                    logger.error(f"Embedding failed for chunk: {e}")
                    continue

            # 4. Validate and store
            validate_doc = ProcessedDocument(
                source_id=source_id, chunks=processed_chunks
            )

            try:
                self.vector_store.upsert_chunks(validate_doc.chunks)
            except Exception as e:
                logger.error(f"Storage failed for {source_id}: {e}")
                return None

            return validate_doc

        except Exception as e:
            logger.error(f"Processing failed for {source_id}: {e}")
            raise DocumentProcessingError(f"Document processing failed: {e}")
