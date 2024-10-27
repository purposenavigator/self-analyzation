# mongodb.py
import os
import logging
from datetime import datetime, timezone
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
                analyze=conversation["analyze"],
                created_at=conversation["created_at"],
                status=conversation["status"],
                is_favorite=conversation["is_favorite"],
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

async def create_conversation(user_conversation: UserConversation):
    try:

        # Prepare the document to insert
        conversation_data = {
            "user_id": user_conversation.user_id,
            "conversation_id": str(ObjectId()),  # Generating a new ObjectId for the conversation
            "topic": user_conversation.topic,
            "summaries": user_conversation.summaries,
            "questions": user_conversation.questions,
            "analyze": user_conversation.analyze,
            "title": user_conversation.title,
            "created_at": user_conversation.created_at or datetime.now(timezone.utc),
            "updated_at": user_conversation.updated_at or datetime.now(timezone.utc),
            "status": user_conversation.status,
            "is_favorite": user_conversation.is_favorite,
            "deleted_at": user_conversation.deleted_at
        }

        # Remove None values from the conversation data
        conversation_data = {k: v for k, v in conversation_data.items() if v is not None}

        # Insert the new document
        result = await collection.insert_one(conversation_data)

        if result.inserted_id:
            return str(result.inserted_id)
        else:
            raise HTTPException(status_code=500, detail="Failed to create conversation.")
    
    except Exception as e:
        logger.error(f"Error creating conversation for user_id {user_conversation.user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while creating conversation.")

async def update_conversation(user_conversation: UserConversation):
    user_id = user_conversation.user_id
    conversation_id = user_conversation.conversation_id
    questions = user_conversation.questions
    summaries = user_conversation.summaries
    analyze = user_conversation.analyze
    title = user_conversation.title
    status = user_conversation.status
    is_favorite = user_conversation.is_favorite
    deleted_at = user_conversation.deleted_at
    updated_at = datetime.utcnow()  # Update the timestamp when modifying

    update_data = {
        "user_id": user_id,
        "questions": questions,
        "summaries": summaries,
        "analyze": analyze,
        "title": title,
        "status": status,
        "is_favorite": is_favorite,
        "updated_at": updated_at,
        "deleted_at": deleted_at
    }

    # Remove None values from the update data
    update_data = {k: v for k, v in update_data.items() if v is not None}

    try:
        result: UpdateResult = await collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": update_data},
            upsert=True
        )
        if result.upserted_id:
            return str(result.upserted_id)
        else:
            existing_document = await collection.find_one(
                {"_id": ObjectId(conversation_id)},
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

async def fetch_user_data_from_db(user_id: int):
    """
    Interacts with the MongoDB database to retrieve all records that contain user_id
    and have 'questions' and 'summaries' attributes.
    """
    try:
        user_data = await collection.find({
            "user_id": user_id,
            "questions": { "$exists": True, "$ne": [] },
            "summaries": { "$exists": True, "$ne": [] }
        }).to_list(length=None)
    
        for document in user_data:
            if "_id" in document:
                document["_id"] = str(document["_id"])  # Convert ObjectId to string
        
        return user_data
    except Exception as e:
        logger.error(f"Database error fetching data for user_id {user_id}: {e}")
        raise
