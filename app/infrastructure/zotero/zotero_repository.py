from typing import Dict
from pyzotero.zotero import Zotero
from app.config.settings import settings
from app.core.logger import logger
from app.core.documents import DocumentMetadata
from app.core.interfaces import ILibraryManagerRepository
from app.core.zotero import ZoteroItem


class ZoteroRepository(ILibraryManagerRepository):
    """Zotero API implementation with caching and data validation"""

    def __init__(self) -> None:
        if not all(
            [
                settings.zotero_api_key,
                settings.zotero_library_type,
                settings.zotero_library_id,
            ]
        ):
            raise ValueError("Missing Zotero configuration in settings")

        self.client = Zotero(
            settings.zotero_library_id,
            settings.zotero_library_type,
            settings.zotero_api_key,
        )
        self.metadata_cache: Dict[str, DocumentMetadata] = {}
        self.raw_item_cache: Dict[str, ZoteroItem] = {}

    def get_metadata(self, source_id: str) -> DocumentMetadata | None:
        try:
            if cached := self.metadata_cache.get(source_id):
                return cached

            item = self._get_validated_item(source_id)
            if not item:
                return None

            metadata = self._convert_to_document_metadata(item)
            self.metadata_cache[source_id] = metadata
            return metadata

        except Exception as e:
            logger.error(f"Zotero metadata fetch failed: {e}")
            return None

    def _get_validated_item(self, source_id: str) -> ZoteroItem | None:
        """Fetch and validate raw Zotero Item"""
        try:
            if cache := self.raw_item_cache.get(source_id):
                return cache

            raw_item = self.client.item(source_id)
            if not raw_item:
                return None

            validated_item = ZoteroItem(**raw_item)
            self.raw_item_cache[source_id] = validated_item
            return validated_item

        except Exception as e:
            logger.error(f"Zotero data validation failed: {e}")
            raise

    def get_source_content(self, parent_id: str) -> str | None:
        """Retrive content of a specific attachment"""
        try:
            children_raw = self.client.children(parent_id)
            if not children_raw:
                return None

            children = [ZoteroItem(**child) for child in children_raw]

            source = next(
                (child for child in children if child.data.filename == "source.md"),
                None,
            )

            if source is None:
                logger.warning(
                    "Content has not been set. Please add a `source.md` as an attachment to the parent entry."
                )
                return None

            return self.client.file(source.key)

        except Exception as e:
            logger.error(
                f"Encountered a problem while retriving content encountered: {e}"
            )
            return None

    def _convert_to_document_metadata(self, item: ZoteroItem) -> DocumentMetadata:
        """Map Zotero API response to DocumentMetadata"""
        return DocumentMetadata(
            zotero_id=item.key,
            title=item.data.title,
            authors="; ".join(
                f"{c.lastName}, {c.firstName}".strip() for c in item.data.creators
            ),
            tags=", ".join(tag.tag for tag in item.data.tags),
            source_version=str(item.version),
            language=item.data.language,
        )
