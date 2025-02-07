from typing import Any, Dict, List, Optional
from chromadb.config import Settings
from datetime import datetime

from pydantic import validate_call


from app.config.settings import settings
from app.core.logger import logger
from app.core.entities import DocumentChunk, DocumentMetadata
from app.core.interfaces import IVectorStoreRepository
import chromadb


class ChromaAdaptor(IVectorStoreRepository):
    def __init__(self, collection_name: str, persist_dir: Optional[str] = None):
        """Initialize Chroma client and collection

        Args:
        collection_name: Name of the collection to use
        persist_dir: Directory to persist data (default from settings)
        """

        if not collection_name:
            raise ValueError("Collection name cannot be emnpty.")

        self.client = chromadb.PersistentClient(
            path="/home/tg/Development/semantics/chroma_db",  # TODO change to settings
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"Initialized Chroma collection '{collection_name}'")

    @validate_call
    def upsert_chunk(self, chunk: DocumentChunk) -> None:
        """Single chunk upsert (uses batch internally)

        Args:
            chunk: DocumentChunk to upsert
        """
        self.upsert_chunks([chunk])

    @validate_call
    def upsert_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Batch upsert chunks with error handling

        Args:
            chunks: List of DocumentChunks to upsert

        Raises:
            ValueError: If input validation fails
            Exception: If upsert operation fails
        """

        if not chunks:
            logger.debug("No chunks to upsert")
            return

        batch_size = len(chunks)
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        logger.debug(f"Preparing to upsert {batch_size} chunks")

        for chunk in chunks:
            if not chunk.content_hash or not chunk.content:
                raise ValueError("Chunk must have content and content_hash")

            meta = {
                key: (
                    value.isoformat()
                    if isinstance(value, datetime)
                    else ""
                    if value is None
                    else value
                )
                for key, value in chunk.metadata.__dict__.items()
            }

            ids.append(chunk.content_hash)
            embeddings.append(chunk.embedding)
            documents.append(chunk.content)
            metadatas.append(meta)

        try:
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
            logger.debug(f"Successfully upserted {batch_size} chunks.")

        except Exception as e:
            logger.error(f"Failed to upsert batch of {batch_size} chunks: {e}")
            raise

    @validate_call
    def search(
        self,
        embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """Search for similar chunks using embedding vector.

        Args:
            embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of matching DocumentChunks

        Raises:
            ValueError: If input validation fails
        """
        if not embedding:
            raise ValueError("Embedding cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be positive")

        try:
            query_results = self.collection.query(
                query_embeddings=[embedding],
                n_results=top_k,
                where=filters if filters else None,
            )

            if not query_results or not query_results.get("ids"):
                logger.warning("No results found for the query.")
                return []

            documents = query_results.get("documents", [[]])
            embeddings = query_results.get("embeddings", [[]])
            metadatas = query_results.get("metadatas", [[]])
            ids = query_results.get("ids")[0]

            if documents is None or embeddings is None or metadatas is None:
                logger.warning("Incomplete data in query results.")
                return []
            document_chunks = []
            for doc, emb, meta, idx in zip(
                documents[0], embeddings[0], metadatas[0], ids
            ):
                # Normalize metadata fields

                normalized_meta = {
                    "zotero_id": str(meta.get("zotero_id", "")),
                    "title": str(meta.get("title", "")),
                    "authors": str(meta.get("authors", "")),
                    "section_header": str(meta.get("section_header"))
                    if meta.get("section_header")
                    else None,
                    "page_range": str(meta.get("page_range"))
                    if meta.get("page_range")
                    else None,
                    "chapter": str(meta.get("chapter"))
                    if meta.get("chapter")
                    else None,
                    "ingestion_date": (
                        datetime.fromisoformat(str(meta.get("ingestion_date", "")))
                        if meta.get("ingestion_date")
                        else None
                    ),
                    "source_version": str(meta.get("source_version", "v1.0.0")),
                    "tags": str(meta.get("tags", "")),
                    "language": str(meta.get("language", "en")),
                }

                # Create DocumentChunk

                document_chunks.append(
                    DocumentChunk(
                        content=doc,
                        embedding=emb,
                        metadata=DocumentMetadata(**normalized_meta),
                        source_id=str(meta.get("zotero_id")),
                        content_hash=idx,
                    )
                )
            return document_chunks
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
