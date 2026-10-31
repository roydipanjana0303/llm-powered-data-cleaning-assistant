
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

# Find the project root
ROOT = Path(__file__).resolve().parents[3]

# Load environment variables
load_dotenv(ROOT / ".env")

# Initialize OpenAI
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is missing from .env")

client = OpenAI(api_key=api_key)

# File containing our RAG knowledge
GUIDE_PATH = (
    ROOT
    / "backend"
    / "rag_engine"
    / "knowledge_base"
    / "data_cleaning_guide.md"
)

# Persistent ChromaDB storage
DB_PATH = ROOT / "storage" / "chroma_db"

# Create ChromaDB client
chroma_client = chromadb.PersistentClient(path=str(DB_PATH))

collection = chroma_client.get_or_create_collection(
    name="data_cleaning_knowledge"
)


def split_into_chunks(text, chunk_size=700):
    """Split the guide into smaller meaningful chunks."""
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        if len(current_chunk) + len(paragraph) <= chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())

            current_chunk = paragraph + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def build_knowledge_base():
    if not GUIDE_PATH.exists():
        raise FileNotFoundError(f"Guide not found: {GUIDE_PATH}")

    # Read the knowledge document
    text = GUIDE_PATH.read_text(encoding="utf-8")

    # Divide it into chunks
    chunks = split_into_chunks(text)

    print("Total knowledge chunks:", len(chunks))

    # Generate embeddings
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )

    embeddings = [item.embedding for item in response.data]

    # Store chunks and embeddings in ChromaDB
    collection.upsert(
        ids=[f"cleaning-guide-{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings,
        metadatas=[
            {
                "source": "data_cleaning_guide.md",
                "chunk_number": i
            }
            for i in range(len(chunks))
        ]
    )

    print("Knowledge base created successfully!")
    print("Stored chunks:", collection.count())


if __name__ == "__main__":
    build_knowledge_base()
