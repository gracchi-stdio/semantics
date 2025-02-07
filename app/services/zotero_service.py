from dataclasses import dataclass
from typing import Dict, List, Union, cast

from pydantic import ValidationError
from pyzotero.zotero import Zotero
from app.config.settings import settings
from app.core.logger import logger
from app.core.documents import DocumentMetadata, ZoteroItem


class ZoteroService:
    def __init__(self) -> None:
        self.library_id = settings.zotero_library_id
        self.library_type = settings.zotero_library_type
        self.api_key = settings.zotero_api_key

        if not all([self.api_key, self.library_type, self.library_type]):
            raise ValueError("Zotero library credentials are not correctly set.")

        self.zot = Zotero(self.library_id, self.library_type, self.api_key)
        self.metadata_cache: Dict[str, DocumentMetadata] = {}

    def get_metadata(self, source_id: str) -> DocumentMetadata | None:
        try:
            # Check cache first
            if cached := self.metadata_cache.get(source_id):
                return cached

            # Fetch from Zotero API
            try:
                item = ZoteroItem(**cast(Dict, self.zot.item(source_id)))
            except ValidationError as e:
                logger.error(f"Validation of the returned zotero response failed: {e}")
                raise ValidationError

            child = self.find_source_md_child(source_id)

            print(self.zot.children(source_id))
            # print(self.zot.item(source_id))

            logger.debug(f"Item retrived: {item}")
            # Convert and cache
            metadata = self.convert_zotero_item(item)
            self.metadata_cache[source_id] = metadata
            return metadata

        except Exception as e:
            logger.error(f"Zotero metadata fetch failed: {e}")
            return None

    def find_source_md_child(self, parent_id: str) -> Dict | None:
        """Find child item with filname 'source.md' in Zotero children."""
        children = self.zot.children(parent_id)
        return next(
            (
                child
                for child in children
                if child.get("data").get("filename") == "source.md"
            ),
            None,
        )

    def get_attachment_content(self, item: ZoteroItem, attachment_filename: str):
        pass

    def convert_zotero_item(self, item: ZoteroItem) -> DocumentMetadata:
        """Convert Zotero API response to our metadata format"""

        data = item.data
        return DocumentMetadata(
            zotero_id=item.key,
            title=data.title,
            authors="; ".join(author.get("name", "") for author in data.creators),
            tags=", ".join(tag.get("tag", "") for tag in data.tags),
            source_version=str(item.version),  # Ensure version is a string
            language=data.language,
        )
