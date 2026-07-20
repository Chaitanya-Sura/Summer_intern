"""MongoDB support for AuraWrite AI."""

import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

_MONGO_CLIENT = None


def get_mongo_client():
    global _MONGO_CLIENT
    if _MONGO_CLIENT is not None:
        return _MONGO_CLIENT

    uri = os.getenv("MONGODB_URI", "").strip()
    if not uri:
        return None

    try:
        _MONGO_CLIENT = MongoClient(uri, serverSelectionTimeoutMS=5000)
        _MONGO_CLIENT.admin.command("ping")
        return _MONGO_CLIENT
    except PyMongoError as exc:
        logger.error(f"MongoDB connection failed: {exc}")
        _MONGO_CLIENT = None
        return None


def get_database():
    client = get_mongo_client()
    if client is None:
        return None
    db_name = os.getenv("MONGODB_DB", "aura_write_ai")
    return client[db_name]


def get_library_collection():
    db = get_database()
    if db is None:
        return None
    collection_name = os.getenv("MONGODB_COLLECTION", "library")
    return db[collection_name]


def get_library_items():
    collection = get_library_collection()
    if collection is None:
        return []
    try:
        items = list(collection.find({}, {'_id': False}).sort('timestamp', -1))
        return items
    except PyMongoError as exc:
        logger.error(f"MongoDB read failed: {exc}")
        return []


def save_library_item(item: dict):
    collection = get_library_collection()
    if collection is None:
        return False
    try:
        collection.replace_one({'id': item['id']}, item, upsert=True)
        return True
    except PyMongoError as exc:
        logger.error(f"MongoDB write failed: {exc}")
        return False


def delete_library_item(item_id: str):
    collection = get_library_collection()
    if collection is None:
        return False
    try:
        collection.delete_one({'id': item_id})
        return True
    except PyMongoError as exc:
        logger.error(f"MongoDB delete failed: {exc}")
        return False
