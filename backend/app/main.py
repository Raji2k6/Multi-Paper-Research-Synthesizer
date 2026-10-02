from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sqlalchemy import inspect, text

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.upload import router as upload_router
from app.api.chat import router as chat_router
from app.api.synthesis import router as synthesis_router
from app.core.config import settings
from app.core.database import Base, engine
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.query import Query
from app.services.llm import LLMGenerationError, uses_openrouter


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")
    Base.metadata.create_all(bind=engine)
    _migrate_auth_columns()
    yield


def _migrate_auth_columns():
    migrations = {
        "users": {
            "password_hash": "VARCHAR",
        },
        "queries": {
            "query_type": "VARCHAR(20) NOT NULL DEFAULT 'chat'",
            "sources": "JSON",
            "documents_analyzed": "INTEGER",
        },
    }
    with engine.begin() as connection:
        inspector = inspect(connection)
        for table, columns in migrations.items():
            existing_columns = {
                column["name"] for column in inspector.get_columns(table)
            }
            for column_name, definition in columns.items():
                if column_name not in existing_columns:
                    connection.execute(
                        text(
                            f"ALTER TABLE {table} ADD COLUMN "
                            f"{column_name} {definition}"
                        )
                    )


app = FastAPI(
    title="PaperFusion AI API",
    version="1.0.0",
    description="Standalone, evidence-grounded research assistant",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(LLMGenerationError)
async def handle_llm_generation_error(
    _request: Request,
    error: LLMGenerationError,
):
    logger.error("Request failed during model generation: %s", error)
    return JSONResponse(
        status_code=502,
        content={
            "detail": (
                "The language-model provider returned no usable answer. "
                "Please retry or switch to local evidence mode."
            )
        },
    )


app.include_router(upload_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(synthesis_router)


@app.get("/")
def root():
    return {
        "message": "PaperFusion AI API is running",
        "storage": engine.dialect.name,
        "answer_mode": "openrouter" if uses_openrouter() else "local-evidence",
    }


@app.get("/health")
def health():
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")
    return {"status": "healthy"}