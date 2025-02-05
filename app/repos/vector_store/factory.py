from typing import Literal

from app.config.settings import settings
from app.core.interfaces import IVectorStoreRepository
from app.repos.vector_store.chroma_adaptor import ChromaAdaptor

VectorStoreTypes = Literal["chroma", "pinecone", "qdrant"]

class VectorStoreFactory:
    @staticmethod
    def create_store(store_type: VectorStoreTypes = None) -> IVectorStoreRepository:
        store_type = store_type or settings.vector_store_type

        if store_type == "chroma":
            return ChromaAdaptor(settings.chroma_collection)
        elif store_type == "pinecone":
            raise NotImplementedError # TODO add pinecone adaptor
        elif store_type == "qdrant":
            raise NotImplementedError # TODO add qdrant adaptor
        else:
            raise ValueError(f"Invalid store type: {store_type}")

