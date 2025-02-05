from typing import List
import json
from chromadb.config import Settings
from datetime import datetime

from app.config.settings import settings
from app.core.entities import DocumentChunk, DocumentMetadata
from app.core.interfaces import IVectorStoreRepository
import chromadb

class ChromaAdaptor(IVectorStoreRepository):
    def __init__(self, collection_name: str, persist_dir: str = settings.chroma_persist_dir):
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(allow_reset=True)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def upsert_chunk(self, chunk: DocumentChunk) -> None:

        meta = {key: (value.isoformat() if  isinstance(value, datetime)
                      else "" if value is None else value)
                for key, value in chunk.metadata.model_dump().items()}

        print("meta :", meta)
        self.collection.upsert(
            ids=[chunk.content_hash],
            embeddings=[chunk.embedding],
            documents=[chunk.content],
            metadatas=[meta]
        )

    def search(self, embedding: List[float], top_k: int = 5, filters=None) -> List[DocumentChunk]:
        # Validate embedding length
        if len(embedding) < 384:
            raise ValueError("Embedding must be at least 384 dimensions long.")

        if filters is None:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=top_k,
                where=filters
            )
        else:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=top_k,
            )

        print(f"Query results: {results}")
        required_keys = ['documents', 'embeddings', 'metadatas', 'ids']
        for key in required_keys:
            if key not in results:
                raise ValueError(f"Missing required key '{key}' in results.")

       # Handle cases where results are empty
        if not results or 'documents' not in results or not results['documents'][0]:
            return []

        return [
            DocumentChunk(
                content=doc,
                embedding=emb.tolist(),
                metadata=DocumentMetadata(**meta),
                content_hash=idx,
                source_id=meta.get('zotero_id')
            ) for doc, emb, meta, idx in zip(
                results['documents'][0],
                results['embeddings'][0],
                results['metadatas'][0],
                results['ids'][0]
            )
        ]