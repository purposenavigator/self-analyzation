# mongodb.py
import os
import logging
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from dotenv import load_dotenv

from type import Query

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo_client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = mongo_client.get_database(os.getenv("MONGODB_DB_NAME"))
collection = db.get_collection("conversations")

async def initialize_counter(sequence_name: str):
    try:
        await db.counters.update_one(
            {"_id": sequence_name},
            {"$setOnInsert": {"seq": 0}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error initializing counter for {sequence_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while initializing counter.")

async def get_conversation(query: Query):
    user_id = query.user_id
    conversation_id = query.conversation_id
    try:
        conversation = await collection.find_one({"user_id": user_id, "conversation_id": conversation_id})
        if not conversation:
            return False, {"user_id": user_id, "messages": []}
        return True, conversation
    except Exception as e:
        logger.error(f"Error fetching conversation for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching conversation.")

async def update_conversation(user_id: int, conversation):
    try:
        await collection.update_one(
            {"user_id": user_id},
            {"$set": conversation},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error updating conversation for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while updating conversation.")

async def get_next_id(sequence_name: str) -> int:
    await initialize_counter(sequence_name)
    
    try:
        counter = await db.counters.find_one_and_update(
            {"_id": sequence_name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return counter["seq"]
    except DuplicateKeyError as e:
        logger.error(f"Duplicate key error for sequence_name {sequence_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching next ID.")
    except Exception as e:
        logger.error(f"Error fetching next ID for sequence_name {sequence_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching next ID.")

