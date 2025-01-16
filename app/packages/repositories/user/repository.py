from bson.objectid import ObjectId
from typing import List, Optional
from app.packages.database import users_collection
from app.packages.schemas.user_schema import UserCreate

# Utility function to convert ObjectId to string
def objectid_to_str(obj_id: ObjectId) -> str:
    return str(obj_id)

# Create a new user
async def create_user(user: UserCreate) -> dict:
    new_user = {
        "username": user.username,
        "hashed_password": user.password,  # Assumes password is already hashed
        "is_active": True,
        "is_admin": False,
    }
    result = await users_collection.insert_one(new_user)
    new_user["_id"] = objectid_to_str(result.inserted_id)
    return new_user

# Get a user by username or ID
async def get_user(identifier: str) -> Optional[dict]:
    if ObjectId.is_valid(identifier):
        user = await users_collection.find_one({"_id": ObjectId(identifier)})
    else:
        user = await users_collection.find_one({"username": identifier})
    
    if user:
        user["_id"] = objectid_to_str(user["_id"])
    return user

# Update a user's information
async def update_user(user_id: str, update_data: dict) -> Optional[dict]:
    if not ObjectId.is_valid(user_id):
        return None
    result = await users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=True  # Return the updated document
    )
    if result:
        result["_id"] = objectid_to_str(result["_id"])
    return result

# Delete a user by ID
async def delete_user(user_id: str) -> bool:
    if not ObjectId.is_valid(user_id):
        return False
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0

# Get all users (with optional filters)
async def get_all_users(filter: dict = {}) -> List[dict]:
    users_cursor = users_collection.find(filter)
    users = []
    async for user in users_cursor:
        user["_id"] = objectid_to_str(user["_id"])
        users.append(user)
    return users
