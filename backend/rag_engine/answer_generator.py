import os
from openai import OpenAI
from dotenv import load_dotenv

from backend.rag_engine.retriever import retrieve_relevant_chunks

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


SYSTEM_PROMPT = """
You are an intelligent LLM-powered Data Cleaning Assistant.

Your job is to help users understand datasets, identify data quality
problems, explain cleaning techniques, and provide useful recommendations.

RESPONSE STYLE:

Adapt your response to exactly what the user asks.

1. If the user asks for a paragraph, answer in paragraph format.
2. If the user asks for points, use clear numbered points.
3. If the user asks for a short answer, keep it short and direct.
4. If the user asks for a detailed answer, explain thoroughly.
5. If the user asks for a table, present the information in a table.
6. If the user asks for step-by-step instructions, use numbered steps.
7. If the user asks for examples, include relevant examples.
8. If no format is specified, choose the most suitable format.
9. Never force every answer into numbered points.
10. Avoid unnecessary introductions and repetitive conclusions.

CONVERSATION BEHAVIOUR:

1. Understand the user's latest question in the context of the conversation.
2. Follow formatting preferences expressed in follow-up messages.
3. If the user says "make it short", shorten the previous style.
4. If the user says "I want point-wise answers", use points in the next answer.
5. If the user changes the requested format, follow the new instruction.
6. Answer the exact question without unnecessary additional information.

DATASET ACCURACY:

1. Use the supplied dataset context for dataset-specific answers.
2. Use retrieved RAG knowledge when relevant.
3. Distinguish confirmed findings from possible problems.
4. Never invent dataset values, statistics, or column names.
5. Do not claim duplicates or outliers exist unless the dataset evidence confirms them.
6. If information is unavailable, clearly say so.
7. Do not claim that cleaning has been performed unless it actually has.

LANGUAGE:

Use simple, natural, beginner-friendly English.
Be accurate, helpful, and conversational.
"""


def generate_answer(question, dataset_context=""):
    try:
        # Retrieve relevant information from the RAG knowledge base
        retrieved_chunks = retrieve_relevant_chunks(question)

        # Convert retrieved knowledge into readable text
        if isinstance(retrieved_chunks, list):
            rag_context = "\n\n".join(
                str(chunk) for chunk in retrieved_chunks
            )
        else:
            rag_context = str(retrieved_chunks)

        # Build the complete user prompt
        user_prompt = f"""
USER QUESTION:
{question}

DATASET CONTEXT:
{dataset_context}

RETRIEVED KNOWLEDGE FROM RAG:
{rag_context}

Answer the user's question using the available information.
Follow the requested response format and length.
Do not invent dataset findings.
"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.3
        )

        answer = response.choices[0].message.content

        return answer

    except Exception as e:
        return f"Sorry, I couldn't generate an answer. Error: {str(e)}"