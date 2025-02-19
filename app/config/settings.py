from functools import lru_cache
from typing import Literal

from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict


VectorStoreTypes = Literal["chroma", "pinecone", "qdrant"]


class ZoteroLibraryType(str, Enum):
    user = "user"
    group = "group"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Vector Store config
    vector_store_type: VectorStoreTypes = "chroma"
    chroma_collection: str = "readings"
    chroma_persist_dir: str = "/home/tg/Development/semantics/chroma_db"

    qwen_api_key: str
    qwen_api_endpoint: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    qwen_embedding_model: str = "text-embedding-v3"
    qwen_embedding_dimension: int = 1024

    deepseek_api_key: str

    gemini_api_key: str

    # Zotero integration
    zotero_api_key: str
    zotero_library_id: str
    zotero_library_type: ZoteroLibraryType = ZoteroLibraryType.user

    # Embedding Services
    embedding_adaptor: str = "qwen"
    embedding_batch_size: int = 32
    embedding_max_retries: int = 3
    embedding_timeout: int = 60

    # Processing Parameters
    chunk_size: int = 1000
    chunk_overlap: int = 100

    database_url: str = "sqlite:///./data/app."


@lru_cache(maxsize=None)
def get_settings() -> Settings:
    """Singleton configuration loader using LRU cache."""
    return Settings()


settings = get_settings()
