from app.core.interfaces import IMetadataRepository
from app.core.logger import logger
from app.config.settings import settings
from app.core.documents import DocumentMetadata
from app.infrastructure.zotero.zotero_repository import ZoteroRepository
from app.services.semantic_service import SemanticService
from app.services.zotero_service import ZoteroService


class MockMetadataRepository(IMetadataRepository):
    def get_metadata(self, source_id: str) -> DocumentMetadata:
        return DocumentMetadata(
            zotero_id=source_id,
            title="Sample Document",
            authors="Doe, John",
            tags="sample,test",
            language="en",
            source_version="1.0",
        )


def zotero_test():
    zRepo = ZoteroRepository()

    content = zRepo.get_source_content("GIMF3MWC")

    print(content)


# def main():
#     # Initialize dependencies
#     vector_store = ChromaAdaptor(collection_name="documents")
#     embedder = QwenEmbeddingGenerator()
#     processor = MarkdownDocumentRepo(embedder=embedder)
#     metadata_repo = MockMetadataRepository()
#
#     semantic_service = SemanticService(
#         vector_store=vector_store,
#         embedder=embedder,
#         processor=processor,
#         metadata_repo=metadata_repo,
#     )
#
#     md_content = """
#     # Research Paper Summary
#
#     ## Introduction
#     Large language models (LLMs) have revolutionized natural language processing...
#
#     ## Methodology
#     We conducted experiments using transformer-based architectures...
#     """
#
#     processed_doc = semantic_service.process_document("paper_123", md_content)
#
#     if processed_doc:
#         logger.info(f"Processed document with {len(processed_doc.chunks)} chunks")
#
#         # example search
#         test_embedding = embedder.generate("transformer experiments")
#         results = vector_store.search(test_embedding, top_k=1)
#         logger.info(f"Search result: {results}")
#     else:
#         logger.error("Document processing failed")
#

if __name__ == "__main__":
    zotero_test()
