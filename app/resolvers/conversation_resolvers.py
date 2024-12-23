from fastapi import HTTPException
from app.models import UserConversation, UserConversationRequest, SimpleConversationQuery
from app.mongodb import get_conversation
import logging

logger = logging.getLogger(__name__)

async def get_conversation_resolver(request: UserConversationRequest) -> UserConversation:
    try:
        conversation_id = request.conversation_id
        user_id = request.user_id
        query = SimpleConversationQuery(conversation_id=conversation_id, user_id=user_id)
        user_conversation = await get_conversation(query)
        return user_conversation
    except Exception as e:
        logger.error(f"Error in get_conversation for request {request}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
