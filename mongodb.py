# mongodb.py
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = mongo_client.get_database(os.getenv("MONGODB_DB_NAME"))
collection = db.get_collection("conversations")

async def get_conversation(user_id: int):
    try:
        conversation = await collection.find_one({"user_id": user_id})
        if not conversation:
            return False, {"user_id": user_id, "messages": []}
        return True, conversation
    except Exception as e:
        print(f"Error fetching conversation for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching conversation.")

async def update_conversation(user_id: int, conversation):
    await collection.update_one(
        {"user_id": user_id},
        {"$set": conversation},
        upsert=True
    )
