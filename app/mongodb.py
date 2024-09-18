# mongodb.py
import os
import logging
from typing import List
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from pymongo.results import UpdateResult
from dotenv import load_dotenv
from bson import ObjectId

from app.models import Analyze, AnalyzeQuery, SimpleConversationQuery, UserConversation, UserConversationQuery
from app.type import Conversation


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

async def get_conversation(query: SimpleConversationQuery) -> UserConversation:
    user_id = query.user_id
    conversation_id = query.conversation_id

    try:
        conversation: Conversation | None = await collection.find_one({ "_id": ObjectId(conversation_id)})
        if not conversation:
            return None
        user_conversation = UserConversation(
                user_id=user_id, 
                conversation_id=conversation_id, 
                topic='topic here',
                questions=conversation["questions"],
                summaries=conversation["summaries"],
                analyze=conversation["analyze"]
            )
        return user_conversation
    except Exception as e:
        logger.error(f"Error fetching conversation for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching conversation.")

async def init_or_get_conversation(query: UserConversationQuery) -> UserConversation:
    user_id = query.user_id
    conversation_id = query.conversation_id
    topic = query.topic

    try:
        conversation: Conversation | None = await collection.find_one({ "_id": ObjectId(conversation_id)})
        if not conversation:
            update_conversation = UserConversation(
                user_id=user_id, 
                conversation_id=conversation_id, 
                topic=topic,
                questions=[],
                summaries=[],
                analyze=[]
            )
            return update_conversation
        update_conversation = UserConversation(
                user_id=user_id, 
                conversation_id=conversation_id, 
                topic=topic,
                questions=conversation["questions"],
                summaries=conversation["summaries"],
                analyze=conversation["analyze"]
            )
        return update_conversation
    except Exception as e:
        logger.error(f"Error fetching conversation for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching conversation.")

async def get_analyze(query: AnalyzeQuery) -> Analyze:
    conversation_id = query.conversation_id

    try:
        conversation: Conversation | None = await collection.find_one({ "_id": ObjectId(conversation_id)})
        if not conversation:
            return None
        analyze = Analyze(
                conversation_id=conversation_id, 
                analyze=conversation["analyze"],
                keywords=conversation.get("keywords", [])
            )
        return analyze
    except Exception as e:
        logger.error(f"Error fetching conversation for user_id {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching conversation.")



async def update_conversation(user_conversation: UserConversation):
    user_id = user_conversation.user_id
    conversation_id = user_conversation.conversation_id
    questions = user_conversation.questions
    summaries = user_conversation.summaries
    analyze = user_conversation.analyze

    try:
        result: UpdateResult = await collection.update_one(
            { "_id": ObjectId(conversation_id)},
            {"$set": {
                "user_id": user_id,
                "questions": questions,
                "summaries": summaries,
                "analyze": analyze
            }},
            upsert=True
        )
        if result.upserted_id:
            return str(result.upserted_id)
        else:
            existing_document = await collection.find_one(
                { "_id": ObjectId(conversation_id)},
            )
            return str(existing_document["_id"])
    except Exception as e:
        logger.error(f"Error updating conversation for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while updating conversation.")

async def store_keywords(conversation_id: str, keywords: List[str]):
    try:
        result: UpdateResult = await collection.update_one(
            { "_id": ObjectId(conversation_id)},
            {"$set": {
                "keywords": keywords
            }},
            upsert=True
        )
        if result.upserted_id:
            return str(result.upserted_id)
        else:
            existing_document = await collection.find_one(
                { "_id": ObjectId(conversation_id)},
            )
            return str(existing_document["_id"])
    except Exception as e:
        logger.error(f"Error storing keywords for conversation_id {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while storing keywords.")

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

