import os

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

qwen_api_key=os.getenv("QWEN_API_KEY")

client = OpenAI(api_key=qwen_api_key, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1")


chroma_client = chromadb.PersistentClient(path="../chroma_db")
collections = chroma_client.get_or_create_collection(name="book_embeddings")

def get_embedding(text: str):
    response = client.embeddings.create(input=text, model="text-embedding-v3")

    return response.data[0].embedding

def query_book(query_text: str, top_k=5):
    query_embedding = get_embedding(query_text)
    results = collections.query(query_embeddings=query_embedding, n_results=top_k)
    return results


query_res = query_book("what is the author's views of nationalism?")

for doc in query_res["documents"][0]:
    print(doc)
    print("\n---\n")