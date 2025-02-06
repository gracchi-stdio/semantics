from typing import List
from chromadb.config import Settings
from datetime import datetime

from app.config.settings import settings
from app.core.logger import logger
from app.core.entities import DocumentChunk, DocumentMetadata
from app.core.interfaces import IVectorStoreRepository
import chromadb


class ChromaAdaptor(IVectorStoreRepository):
    def __init__(
        self, collection_name: str, persist_dir: str = settings.chroma_persist_dir
    ):
        self.client = chromadb.PersistentClient(
            path=persist_dir, settings=Settings(allow_reset=True)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

    def upsert_chunk(self, chunk: DocumentChunk) -> None:
        """Single chunk upsert (uses batch internally)"""
        self.upsert_chunks([chunk])

    def upsert_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Batch upsert chunks with error handling"""
        if not chunks:
            return

        batch_size = len(chunks)
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in chunks:
            meta = {
                key: (
                    value.isoformat()
                    if isinstance(value, datetime)
                    else ""
                    if value is None
                    else value
                )
                for key, value in chunk.metadata.model_dump().items()
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

    def search(
        self, embedding: List[float], top_k: int = 5, filters=None
    ) -> List[DocumentChunk]:
        # Validate embedding length

        if filters:
            results = self.collection.query(
                query_embeddings=[embedding], n_results=top_k, where=filters
            )
        else:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=top_k,
            )

        print(f"Query results: {results}")
        required_keys = ["documents", "embeddings", "metadatas", "ids"]
        for key in required_keys:
            if key not in results:
                raise ValueError(f"Missing required key '{key}' in results.")

        # Handle cases where results are empty
        if not results or "documents" not in results or not results["documents"][0]:
            return []

        return [
            DocumentChunk(
                content=doc,
                embedding=emb,
                metadata=DocumentMetadata(**meta),
                content_hash=idx,
                source_id=meta.get("zotero_id"),
            )
            for doc, emb, meta, idx in zip(
                results["documents"][0],
                results["embeddings"][0],
                results["metadatas"][0],
                results["ids"][0],
            )
        ]
