import os
import logging

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo_client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = mongo_client.get_database(os.getenv("MONGODB_DB_NAME"))
conversation_collection = db.get_collection("conversations")
users_collection = db.get_collection("users")
