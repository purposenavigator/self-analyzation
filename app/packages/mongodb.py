# mongodb.py
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from pymongo.results import UpdateResult
from bson import ObjectId

from app.packages.models.conversation_models import Analyze, AnalyzeQuery, SimpleConversationQuery, UserConversationQuery
from app.type import Conversation
from app.packages.database import conversation_collection, logger


async def get_conversation_by_id(conversation_id) -> Conversation:
    """
    Fetches a conversation document from the MongoDB conversation_collection by its ID.

    Parameters:
    - conversation_collection: The MongoDB conversation_collection object.
    - conversation_id: The ID of the conversation as a string.

    Returns:
    - The conversation document or None if not found.
    """
    try:
        conversation = await conversation_collection.find_one({"_id": ObjectId(conversation_id)})
        return conversation
    except Exception as e:
        raise Exception(f"An error occurred while fetching the conversation: {e}")

async def get_conversation(query: SimpleConversationQuery) -> Conversation:
    user_id = query.user_id
    conversation_id = query.conversation_id

    try:
        conversation: Conversation | None = await get_conversation_by_id(conversation_id)
        if not conversation:
            return None
        user_conversation = Conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            topic=conversation['topic'],
            questions=conversation["questions"],
            summaries=conversation["summaries"],
            analyze=conversation["analyze"],
            answers=conversation.get("answers", []),
        )
        return user_conversation
    except Exception as e:
        logger.error(f"Error fetching conversation for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching conversation.")


async def init_or_get_conversation(query: UserConversationQuery) -> Conversation:
    user_id = query.user_id
    conversation_id = query.conversation_id
    topic = query.topic

    initialized_conversation = Conversation(
                user_id=user_id, 
                conversation_id=None, 
                topic=topic,
                questions=[],
                summaries=[],
                analyze=[],
                answers=[]
            )
    
    if not conversation_id:
        return initialized_conversation

    try:
        conversation: Conversation | None = await get_conversation_by_id(conversation_id)
        if not conversation:
            return initialized_conversation
        update_conversation = Conversation(
                user_id=user_id, 
                conversation_id=conversation_id, 
                topic=topic,
                questions=conversation["questions"],
                summaries=conversation["summaries"],
                analyze=conversation["analyze"],
                answers=conversation["answers"],
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
        conversation: Conversation | None = await get_conversation_by_id(conversation_id)
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

async def create_conversation(user_conversation: Conversation):
    try:

        # Prepare the document to insert
        conversation_data = {
            "user_id": user_conversation.user_id,
            "conversation_id": str(ObjectId()),  # Generating a new ObjectId for the conversation
            "topic": user_conversation.topic,
            "summaries": user_conversation.summaries,
            "questions": user_conversation.questions,
            "analyze": user_conversation.analyze,
            "answers": user_conversation.answers,
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
        result = await conversation_collection.insert_one(conversation_data)

        if result.inserted_id:
            return str(result.inserted_id)
        else:
            raise HTTPException(status_code=500, detail="Failed to create conversation.")
    
    except Exception as e:
        logger.error(f"Error creating conversation for user_id {user_conversation.user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while creating conversation.")

async def update_or_append_field_by_id(conversation_id: str, field_name: str, key: str, value: any):
    """
    Updates or appends a field in a conversation document.
    For nested objects, it updates/adds the key-value pair within that field.
    
    Args:
        conversation_id (str): The ID of the conversation
        field_name (str): Name of the field to update
        key (str): Key to update/add within the field
        value (any): Value to set for the key
        
    Returns:
        UpdateResult: The result of the update operation
    """
    try:
        update_result = await conversation_collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$set": {
                    f"{field_name}.{key}": value
                }
            },
            upsert=True
        )

        if update_result.modified_count > 0 or update_result.upserted_id:
            logger.info(f"Successfully updated {field_name}.{key} for conversation {conversation_id}")
        else:
            logger.warning(f"No changes made to {field_name}.{key} for conversation {conversation_id}")

        return update_result

    except Exception as e:
        logger.error(f"Error updating {field_name} for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating {field_name}")

async def update_conversation(user_conversation: Conversation):
    user_id = user_conversation.user_id
    conversation_id = user_conversation.conversation_id
    questions = user_conversation.questions
    summaries = user_conversation.summaries
    analyze = user_conversation.analyze
    answers = user_conversation.answers
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
        "answers": answers,
        "title": title,
        "status": status,
        "is_favorite": is_favorite,
        "updated_at": updated_at,
        "deleted_at": deleted_at,
    }

    # Remove None values from the update data
    update_data = {k: v for k, v in update_data.items() if v is not None}

    try:
        result: UpdateResult = await conversation_collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": update_data},
            upsert=True
        )
        if result.upserted_id:
            return str(result.upserted_id)
        else:
            existing_document = await conversation_collection.find_one(
                {"_id": ObjectId(conversation_id)},
            )
            return str(existing_document["_id"])
    except Exception as e:
        logger.error(f"Error updating conversation for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while updating conversation.")

async def store_keywords(conversation_id: str, keywords: List[str]):
    try:
        result: UpdateResult = await conversation_collection.update_one(
            { "_id": ObjectId(conversation_id)},
            {"$set": {
                "keywords": keywords
            }},
            upsert=True
        )
        if result.upserted_id:
            return str(result.upserted_id)
        else:
            existing_document = await conversation_collection.find_one(
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

async def fetch_user_data_from_db(user_id: int) -> List[Conversation]:
    """
    Interacts with the MongoDB database to retrieve all records that contain user_id
    and have 'questions' and 'summaries' attributes.
    """
    try:
        user_data = await conversation_collection.find({
            "user_id": user_id,
            "questions": { "$exists": True, "$ne": [] },
            "summaries": { "$exists": True, "$ne": [] }
        }).to_list(length=None)
    
        if not user_data or len(user_data) == 0:
            return []
    
        for document in user_data:
            if "_id" in document:
                document["_id"] = str(document["_id"])  # Convert ObjectId to string
        
        return user_data
    except Exception as e:
        logger.error(f"Database error fetching data for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching data.")

async def get_analysis_summary_by_sha(conversation_id: str, sha256_hash: str):
    """
    Retrieves the analysis summary for a given SHA hash from a conversation.
    
    Args:
        conversation_id (str): The ID of the conversation
        sha256_hash (str): The SHA-256 hash of the content
        
    Returns:
        str | None: The analysis summary if found, None otherwise
    """
    try:
        conversation = await conversation_collection.find_one(
            {
                "_id": ObjectId(conversation_id),
                f"analysis_summaries.{sha256_hash}": {"$exists": True}
            },
            {f"analysis_summaries.{sha256_hash}": 1}
        )
        
        if conversation and "analysis_summaries" in conversation:
            return conversation["analysis_summaries"].get(sha256_hash)
        return None
        
    except Exception as e:
        logger.error(f"Error fetching analysis summary for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching analysis summary")
