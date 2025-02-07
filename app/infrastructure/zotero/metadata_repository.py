from operator import itemgetter
from typing import Dict, Optional
from app.config.settings import settings
from app.core.logger import logger
from app.core.documents import DocumentMetadata, convert_zotero_item
from app.core.interfaces import IMetadataRepository
from pyzotero import zotero


class ZoteroMetadataRepository(IMetadataRepository):
    """
    Zotero API implementation for metadata retrieval
    """

    def __init__(self) -> None:
        self.zot = zotero.Zotero(
            settings.zotero_library_id,
            settings.zotero_library_type,
            settings.zotero_api_key,
        )
        self.cache: Dict[str, DocumentMetadata] = {}

    def get_metadata(self, source_id: str) -> Optional[DocumentMetadata]:
        try:
            # Check cache first
            if cached := self.cache.get(source_id):
                return cached

            # Fetch from Zotero API
            item = self.zot.item(source_id)
            if not item or "data" not in item:
                return None

            # Conver and cache
            metadata = convert_zotero_item(item)
            self.cache[source_id] = metadata
            return metadata

        except Exception as e:
            logger.error(f"Zotero metadata fetch failed: {e}")
            return None
