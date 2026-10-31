import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]

load_dotenv(ROOT / ".env")

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is missing from the project .env file.")

client = OpenAI(api_key=api_key)

DB_PATH = ROOT / "storage" / "chroma_db"
COLLECTION_NAME = "data_cleaning_knowledge"
EMBEDDING_MODEL = "text-embedding-3-small"

chroma_client = chromadb.PersistentClient(path=str(DB_PATH))

collection = chroma_client.get_collection(
    name=COLLECTION_NAME
)


def retrieve_knowledge(question, top_k=3):
    """Retrieve relevant cleaning knowledge from ChromaDB."""

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[question]
    )

    query_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, total_chunks)
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    return [
        {
            "content": document,
            "source": metadata.get("source", "Unknown source")
        }
        for document, metadata in zip(documents, metadatas)
    ]


def retrieve_relevant_chunks(question, top_k=3):
    """Compatibility function for the answer generator."""

    knowledge = retrieve_knowledge(question, top_k)

    return [
        {
            "text": item["content"],
            "source": item["source"]
        }
        for item in knowledge
    ]