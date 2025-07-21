from typing import AsyncGenerator
from pymongo import MongoClient
from pymongo.database import Database
from src.shared.settings import get_settings

class PyMongoClient:
    """
    Manages the PyMongo client connection.
    """
    client: MongoClient = None

pymongo_client_instance = PyMongoClient()


async def get_database() -> AsyncGenerator[Database, None]:
    """
    Dependency that yields a PyMongo database instance for each request.
    """
    if pymongo_client_instance.client is None:
        raise Exception("MongoDB client is not initialized.")
    yield pymongo_client_instance.client[get_settings().db_name]