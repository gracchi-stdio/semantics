from app.infrastructure.document_conversion.pdf_to_markdown_converter import (
    PdfToMarkdownConverter,
)
from app.infrastructure.markdown.document_repository import MarkdownDocumentRepository
from app.infrastructure.vector_store.factory import VectorStoreFactory
from app.infrastructure.zotero.zotero_repository import ZoteroRepository
from app.services.semantic_service import SemanticService
from app.infrastructure.embedding.factory import EmbeddingFactory


def test_pdf_to_markdown():
    converter = PdfToMarkdownConverter()
    filename = "SICQFK4X"
    markdown_content = converter.convert(file_path=f"sample/{filename}.pdf")

    with open(f"sample/{filename}.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)

    markdown_pages = converter.chunk_by_page(markdown_content)
    paragraph_chunks = converter.chunk_by_paragraph(markdown_pages)

    for i, chunk in enumerate(paragraph_chunks[:5]):
        print(
            f"Chunk {i + 1}: Page {chunk.page}. content (first 100 chars): {chunk.content} ..."
        )
        if i > 0:
            overlap_text_previous = (
                paragraph_chunks[i - 1].content[-50:]
                if len(paragraph_chunks[i - 1].content) >= 50
                else paragraph_chunks[i - 1].content
            )
            overlap_text_current = (
                chunk.content[:50] if len(chunk.content) >= 50 else chunk.content
            )
            print(
                f"  Overlap with previous chunk (previous chunk's last 50 chars): '{overlap_text_previous}'"
            )
            print(
                f"  Overlap with previous chunk (current chunk's first 50 chars):  '{overlap_text_current}'"
            )
        print("-" * 50)


def main():
    # logger.setLevel(logging.WARNING)
    # Initialize dependencies
    vector_store = VectorStoreFactory.create_store()
    embedder = EmbeddingFactory.create_embedder()
    processor = MarkdownDocumentRepository(embedder=embedder)
    library_manager = ZoteroRepository()

    semantic_service = SemanticService(
        vector_store=vector_store,
        embedder=embedder,
        processor=processor,
        library_manager=library_manager,
    )

    # example search
    # test_embedding = embedder.generate("who was Reza Shah?")
    # results = vector_store.search(test_embedding, top_k=10)
    # logger.info(f"Search result: {results}")

    processed_doc = semantic_service.process_zotero_item("5LDRFEH2")

    if processed_doc:
        logger.info(f"Processed document with {len(processed_doc.chunks)} chunks")

        # example search
        test_embedding = embedder.generate("who was Reza Shah?")
        results = vector_store.search(test_embedding, top_k=10)
        logger.info(f"Search result: {results}")
    else:
        logger.error("Document processing failed")


if __name__ == "__main__":
    test_pdf_to_markdown()
