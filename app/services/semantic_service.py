from typing import Optional

from app.core.documents import ProcessedDocument
from app.core.exceptions import DocumentProcessingError
from app.core.interfaces import (
    IDocumentRepository,
    IEmbeddedGenerator,
    IMetadataRepository,
    IVectorStoreRepository,
)
from app.core.logger import logger


class SemanticService:
    def __init__(
        self,
        vector_store: IVectorStoreRepository,
        embedder: IEmbeddedGenerator,
        processor: IDocumentRepository,
        metadata_repo: IMetadataRepository,
    ):
        self.vector_store = vector_store
        self.embedder = embedder
        self.processor = processor
        self.metadata_repo = metadata_repo

    def process_document(self, source_id, content: str) -> Optional[ProcessedDocument]:
        if not content.strip():
            logger.error("Empty content provided")
            return None

        try:
            # 1. Fetch metadata
            metadata = self.metadata_repo.get_metadata(source_id)
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
            for chunk in raw_chunks:
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
