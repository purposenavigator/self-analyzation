import os
import json
import logging
import boto3
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load .env only in local development
if os.getenv("ENVIRONMENT") != "fargate":
    load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_secret(secret_name: str):
    """
    Fetch secret from AWS Secrets Manager.
    This is only called when running on AWS Fargate.
    """
    client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION", "us-east-1"))
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_data = response.get("SecretString")
        return json.loads(secret_data) if secret_data else {}
    except Exception as e:
        logger.error(f"Failed to retrieve secret from Secrets Manager: {e}")
        return {}

# Determine environment and get DB credentials
if os.getenv("ENVIRONMENT") == "fargate":
    secret_name = os.getenv("AWS_SECRET_NAME", "MySecretEnv")
    secret_values = get_secret(secret_name)
    
    MONGODB_URI = secret_values.get("MONGODB_URI")
    MONGODB_DB_NAME = secret_values.get("MONGODB_DB_NAME")
else:
    MONGODB_URI = os.getenv("MONGODB_URI")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")

# Initialize MongoDB client
mongo_client = AsyncIOMotorClient(MONGODB_URI)
db = mongo_client.get_database(MONGODB_DB_NAME)

conversation_collection = db.get_collection("conversations")
users_collection = db.get_collection("users")

