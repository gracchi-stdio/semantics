from typing import List
import pymupdf4llm
from app.core.logger import logger
from app.infrastructure.document_conversion.document_converter import (
    IDocumentConverter,
    MarkdownPage,
    ParagraphChunk,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


class PdfToMarkdownConverter(IDocumentConverter):
    """
    Convert PDF content to Markdown format using pymupdf.
    pymupdf tends to separate pages by '---'
    """

    def convert(self, file_path: str) -> str:
        try:
            return pymupdf4llm.to_markdown(file_path)

        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            raise Exception

    def chunk_by_page(self, markdown_content: str) -> List[MarkdownPage]:
        """
        Converts a PDF file to Markdown format, splitting into pages by '---' separator.

        Args:
            file_path: Path to the PDF file.

        Returns:
            List of MarkdownPage
        """

        paged_documents: List[MarkdownPage] = []
        page_markdown_string = markdown_content.split("---\n")

        for page_number, page_markdown in enumerate(page_markdown_string):
            if page_markdown.strip():  # Ignore empty page
                page_document = MarkdownPage(
                    content=page_markdown.strip(),  # Store page markdown strip white space
                    page=page_number + 1,
                )
                paged_documents.append(page_document)

        return paged_documents

    def chunk_by_paragraph(
        self, markdown_pages: List[MarkdownPage]
    ) -> List[ParagraphChunk]:
        """
        Chunks the document into paragraphs using Langchain's RecursiveCharacterTextSplitter.
        Args:
            markdown_pages: List of MarkdownPage objects.

        Returns:
            List of ParagraphChunk objects.
        """
        paragraph_chunks: List[ParagraphChunk] = []

        text_splitter = RecursiveCharacterTextSplitter(  # Initialize Langchain splitter for paragraphs
            separators=[
                "\n\n",
                "\n",
                " ",
                ".",
                ",",
                "\u200b",  # Zero-width space
                "\uff0c",  # Fullwidth comma
                "\u3001",  # Ideographic comma
                "\uff0e",  # Fullwidth full stop
                "\u3002",  # Ideographic full stop
                "",
            ],  # Try splitting by paragraph breaks, newlines, spaces, then characters
            chunk_size=1000,  # You can adjust chunk_size as needed
            chunk_overlap=50,
            length_function=len,
        )

        for page in markdown_pages:
            split_text = text_splitter.split_text(page.content)

            for chunk_text in split_text:
                if chunk_text.strip():
                    paragraph_chunk = ParagraphChunk(
                        content=chunk_text,
                        page=page.page,
                        chapter=page.chapter,
                        section=page.section,
                    )
                    paragraph_chunks.append(paragraph_chunk)

        return paragraph_chunks
