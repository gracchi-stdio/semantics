import hashlib
import uuid

import chromadb
from dotenv import load_dotenv
import os
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import MarkdownHeaderTextSplitter

load_dotenv()

qwen_api_key=os.getenv("QWEN_API_KEY")

client = OpenAI(api_key=qwen_api_key, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1")

def read_markdown(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def generate_content_id(text, metadata):
    unique_string = text + str(metadata)
    return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()[:32]

markdown_content = read_markdown("../entries/abrahamianHistoryModernIran2018/source.md")

headers_to_split_on = {
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
}

markdown_text_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    return_each_line=False,
)

md_header_splits = markdown_text_splitter.split_text(markdown_content)

chunks_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)
final_chunks = chunks_splitter.split_documents(md_header_splits)

# Step 5: Generate and store embeddings
chroma_client = chromadb.PersistentClient(path="../chroma_db")
collections = chroma_client.get_or_create_collection(name="book_embeddings")

# Step 6: Generate and store embeddings
def get_embedding(text: str):
    response = client.embeddings.create(input=text, model="text-embedding-v3")

    return response.data[0].embedding


ln = len(final_chunks)
print(f"This is the length : {ln}")
# store chunks with metadata
for i, chunk in enumerate(final_chunks):
    text_content = chunk.page_content
    metadata = chunk.metadata

    if not isinstance(metadata, dict) or not metadata:  # Check if metadata is a non-empty dict
        metadata = {"default_key": "default_value"}  # Assign a default dictionary

    print(f"iteration: {i} / {ln}")
    # generate embedding
    embedding = get_embedding(text_content)

    collections.add(
        ids=str(uuid.uuid4()),
        embeddings=embedding,
        documents=text_content,
        metadatas=metadata,
    )

# step 7: Query function
def query_book(query_text: str, top_k=3):
    query_embedding = get_embedding(query_text)
    results = collections.query(query_embeddings=query_embedding, n_results=top_k)
    return results

query_res = query_book("What are the main themes of the book?")
for doc in query_res["documents"][0]:
    print(doc)
    print("\n---\n")