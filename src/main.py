import uvicorn
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient
from pymongo.database import Database

from src.shared.settings import get_settings
from src.infrastructure.persistence.database import pymongo_client_instance

from src.api.router import api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for connecting and disconnecting MongoDB.
    This is where concrete dependencies related to infrastructure are initialized.
    """
    logger.info("Connecting to MongoDB with PyMongo Async API...")
    try:
        settings = get_settings()
        pymongo_client_instance.client = AsyncMongoClient(settings.mongo_db_url)
        
        await pymongo_client_instance.client.admin.command('ping')
        logger.info("MongoDB connected successfully with PyMongo Async API!")
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise e

    yield

    logger.info("Closing MongoDB connection...")
    if pymongo_client_instance.client:
        pymongo_client_instance.client.close()
    logger.info("MongoDB connection closed.")

# Create the FastAPI application instance
app = FastAPI(
    title="Chat API",
    description="API for managing chat interactions with an LLM.",
    version="1.0.0",
    lifespan=lifespan
)

# API routers
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8080, reload=True)