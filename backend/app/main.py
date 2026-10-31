
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from uuid import uuid4
import pandas as pd
import json
import sys

# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

# main.py is located in the project root
ROOT = Path(__file__).resolve().parents[2]

BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

UPLOAD_DIR = ROOT / "storage" / "uploads"
PROCESSED_DIR = ROOT / "storage" / "processed"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Add backend folder to Python path
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ==================================================
# 2. IMPORT EXISTING PROJECT MODULES
# ==================================================

try:
    from data_engine.profiling.profile import (
        load_dataset,
        profile_dataset
    )

    from data_engine.cleaning.cleaner import (
        prepare_cleaning_preview,
        apply_cleaning
    )

    from llm_engine.assistant import (
        get_dataset_context,
        generate_answer
    )

except ImportError as error:
    raise ImportError(
        f"Could not import project modules: {error}. "
        "Check your backend folder structure."
    )


# ==================================================
# 3. REQUEST MODEL
# ==================================================

class AssistantRequest(BaseModel):
    question: str


# ==================================================
# 4. FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="LLM-Powered Data Cleaning Assistant",
    description=(
        "AI-powered data cleaning using LLMs, "
        "RAG and MCP."
    ),
    version="1.0.0"
)


# ==================================================
# 5. CORS CONFIGURATION
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# 6. HOME API
# ==================================================

@app.get("/")
def home():
    return {
        "project": "LLM-Powered Data Cleaning Assistant",
        "message": "Backend is running successfully!",
        "status": "Online"
    }


# ==================================================
# 7. HEALTH CHECK API
# ==================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FastAPI Backend"
    }


# ==================================================
# 8. CSV UPLOAD API
# ==================================================

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select a file."
        )

    if Path(file.filename).suffix.lower() != ".csv":
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )

    content = await file.read()
    await file.close()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 10 MB."
        )

    saved_name = f"{uuid4().hex}.csv"
    file_path = UPLOAD_DIR / saved_name

    try:
        file_path.write_bytes(content)

        df = pd.read_csv(file_path)

        if df.empty or len(df.columns) == 0:
            raise ValueError(
                "CSV contains no dataset records."
            )

        preview = json.loads(
            df.head(5).to_json(orient="records")
        )

        return {
            "message": "CSV uploaded successfully!",
            "original_filename": file.filename,
            "saved_filename": saved_name,
            "filename": saved_name,
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "column_names": df.columns.tolist(),
            "preview": preview
        }

    except Exception as error:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail=f"Could not process CSV file: {str(error)}"
        )


# ==================================================
# 9. DATASET PROFILING API
# ==================================================

@app.get("/profile/{saved_filename}")
def profile_uploaded_dataset(saved_filename: str):

    if (
        Path(saved_filename).name != saved_filename
        or not saved_filename.lower().endswith(".csv")
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    file_path = UPLOAD_DIR / saved_filename

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Uploaded dataset not found."
        )

    try:
        df = load_dataset(str(file_path))

        result = profile_dataset(df)

        return {
            "message": "Dataset profiling completed!",
            "filename": saved_filename,
            "profiling_results": jsonable_encoder(result)
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Profiling failed: {str(error)}"
        )


# ==================================================
# 10. CLEANING PREVIEW API
# ==================================================

@app.get("/clean/preview/{saved_filename}")
def cleaning_preview(saved_filename: str):

    if (
        Path(saved_filename).name != saved_filename
        or not saved_filename.lower().endswith(".csv")
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    file_path = UPLOAD_DIR / saved_filename

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Uploaded dataset not found."
        )

    try:
        original_df = pd.read_csv(file_path)

        preview_df, actions = prepare_cleaning_preview(
            original_df
        )

        return {
            "message": "Cleaning preview generated successfully!",
            "filename": saved_filename,
            "rows_before": int(len(original_df)),
            "rows_after": int(len(preview_df)),
            "proposed_actions": jsonable_encoder(actions),
            "preview": json.loads(
                preview_df.head(10).to_json(orient="records")
            ),
            "approval_required": True
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Cleaning preview failed: {str(error)}"
        )


# ==================================================
# 11. CLEANING APPROVAL API
# ==================================================

@app.post("/clean/approve/{saved_filename}")
def approve_cleaning(saved_filename: str):

    if (
        Path(saved_filename).name != saved_filename
        or not saved_filename.lower().endswith(".csv")
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    file_path = UPLOAD_DIR / saved_filename

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Uploaded dataset not found."
        )

    try:
        original_df = pd.read_csv(file_path)

        cleaned_df, actions = apply_cleaning(original_df)

        output_name = f"cleaned_{uuid4().hex}.csv"
        output_path = PROCESSED_DIR / output_name

        cleaned_df.to_csv(output_path, index=False)

        missing_before = int(
            original_df.replace(
                r"^\s*$",
                pd.NA,
                regex=True
            ).isna().sum().sum()
        )

        missing_after = int(
            cleaned_df.isna().sum().sum()
        )

        return {
            "message": "Cleaning approved and completed!",
            "original_filename": saved_filename,
            "cleaned_filename": output_name,
            "rows_before": int(len(original_df)),
            "rows_after": int(len(cleaned_df)),
            "proposed_actions": jsonable_encoder(actions),
            "missing_values_before": missing_before,
            "missing_values_after": missing_after,
            "original_preserved": True
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Cleaning failed: {str(error)}"
        )


# ==================================================
# 12. AI ASSISTANT API
# ==================================================

@app.post("/assistant/ask")
async def ask_ai_assistant(request: AssistantRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    try:
        dataset_context = await get_dataset_context()

        result = generate_answer(
            question,
            dataset_context
        )

        return {
            "message": "AI response generated successfully!",
            "question": question,
            "answer": result["answer"],
            "rag_sources": result["sources"]
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"AI assistant failed: {str(error)}"
        )


# ==================================================
# 13. RUN APPLICATION DIRECTLY
# ==================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
