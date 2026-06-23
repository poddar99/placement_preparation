import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import (
    analytics,
    auth,
    company,
    dashboard,
    dsa,
    interview_rag,
    mentor,
    mock_interview,
    resume,
    resume_rewriter,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("PlacementPilot AI backend started")
    yield
    await engine.dispose()
    logger.info("PlacementPilot AI backend shutdown")


app = FastAPI(
    title=settings.app_name,
    description="AI-powered placement preparation platform backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = settings.api_prefix

app.include_router(auth.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(dsa.router, prefix=api_prefix)
app.include_router(resume.router, prefix=api_prefix)
app.include_router(resume_rewriter.router, prefix=api_prefix)
app.include_router(company.router, prefix=api_prefix)
app.include_router(mentor.router, prefix=api_prefix)
app.include_router(interview_rag.router, prefix=api_prefix)
app.include_router(mock_interview.router, prefix=api_prefix)
app.include_router(analytics.router, prefix=api_prefix)


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "ollama_model": settings.ollama_model}