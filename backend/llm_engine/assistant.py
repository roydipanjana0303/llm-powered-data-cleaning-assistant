
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Project paths
ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / "backend" / "mcp_server" / "server.py"

# Environment setup
sys.path.insert(0, str(ROOT / "backend"))
load_dotenv(ROOT / ".env")

from rag_engine.retriever import retrieve_knowledge

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


async def get_dataset_context():
    """Retrieve actual dataset information using MCP tools."""

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER)]
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("MCP connected successfully!")

            # Call MCP tools
            inspection = await session.call_tool(
                "inspect_dataset", {}
            )

            missing = await session.call_tool(
                "detect_missing_values", {}
            )

            duplicates = await session.call_tool(
                "detect_duplicates", {}
            )

            monthly_summary = await session.call_tool(
                "summarize_column",
                {"column_name": "MonthlyCharges"}
            )

            total_summary = await session.call_tool(
                "summarize_column",
                {"column_name": "TotalCharges"}
            )

            monthly_outliers = await session.call_tool(
                "detect_outliers",
                {"column_name": "MonthlyCharges"}
            )

            total_outliers = await session.call_tool(
                "detect_outliers",
                {"column_name": "TotalCharges"}
            )

            results = [
                inspection,
                missing,
                duplicates,
                monthly_summary,
                total_summary,
                monthly_outliers,
                total_outliers
            ]

            context = []

            for result in results:
                for item in result.content:
                    if hasattr(item, "text"):
                        context.append(item.text)

            return "\n\n".join(context)


def generate_answer(question, dataset_context):
    """Combine MCP results with RAG knowledge and GPT."""

    # Retrieve relevant knowledge using RAG
    knowledge = retrieve_knowledge(question, top_k=3)

    rag_context = "\n\n".join(
        item["content"] for item in knowledge
    )

    sources = sorted(
        set(item["source"] for item in knowledge)
    )

    prompt = f"""
You are a professional, beginner-friendly data-cleaning analyst.

ACTUAL DATASET INFORMATION FROM MCP:
{dataset_context}

RETRIEVED CLEANING KNOWLEDGE FROM RAG:
{rag_context}

USER QUESTION:
{question}

RESPONSE STYLE:
- Answer the exact question directly.
- Do not start with conversational filler.
- Use a professional, concise, beginner-friendly tone.
- Use short headings and bullet points when useful.
- Explain difficult technical terms in simple language.
- For technical concepts, provide a definition, formula (if relevant),
  and one short example when requested.
- Avoid storytelling, long introductions, repetition,
  and unnecessary details.
- Keep simple factual answers to 2–4 sentences.
- Use numbered steps only when the user asks for steps.

ACCURACY:
- Use actual dataset information from MCP for dataset-specific findings.
- Use retrieved RAG knowledge where relevant.
- Never invent dataset statistics, column names, or calculated values.
- Clearly label hypothetical examples.
- If information is unavailable, say so.
- Never claim that data has been modified unless a cleaning operation
  actually ran.
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    return {
        "answer": response.output_text,
        "sources": sources
    }


async def main():
    question = "Find missing values and recommend how to handle them."

    print("Connecting to MCP server...")

    dataset_context = await get_dataset_context()

    print("MCP dataset information retrieved!")

    result = generate_answer(question, dataset_context)

    print("\nAI ASSISTANT RESPONSE:\n")
    print(result["answer"])

    print("\nRAG SOURCES:")

    for source in result["sources"]:
        print("-", source)


if __name__ == "__main__":
    asyncio.run(main())
