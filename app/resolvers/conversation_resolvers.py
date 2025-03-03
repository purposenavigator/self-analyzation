import logging
from fastapi import HTTPException
from app.packages.models.conversation_models import UserConversationRequest, SimpleConversationQuery, GPTRequest
from app.packages.mongodb import get_conversation, fetch_user_data_from_db, update_conversation
from app.services.conversation_services import process_conversation
from app.openai_resolvers.get_title import get_title
from app.openai_resolvers.generate_responses import generate_responses
from app.type import Conversation
from typing import List

logger = logging.getLogger(__name__)

async def get_conversation_resolver(request: UserConversationRequest, user_id: str) -> Conversation:
    try:
        conversation_id = request.conversation_id
        query = SimpleConversationQuery(conversation_id=conversation_id, user_id=user_id)
        conversation = await get_conversation(query)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger.error(f"Error in get_conversation for request {request}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_all_user_conversations_resolver(user_id: str) -> List[Conversation]:
    """
    Calls the database function and handles the case where no data is found.
    Takes user_id as a parameter.

    Args:
        user_id (str): The ID of the user whose conversations are to be retrieved.

    Returns:
        list: List of user conversations.

    Raises:
        HTTPException: If there is an error during data fetching or processing.
    """
    try:
        user_data = await fetch_user_data_from_db(user_id)
        
        if not user_data:
            raise ValueError(f"No data found for user_id {user_id}")
        
        return user_data
    except ValueError as ve:
        logger.warning(ve)
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Resolver error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching data.")

async def process_answer_and_generate_followup_resolver(request: GPTRequest, user_id: str):
    try:
        conversation = await process_conversation(request, user_id)
        user_prompt = request.prompt
        ai_question_response, ai_summary_response, ai_analyze_response, ai_answers_response = await generate_responses(conversation)
        await update_conversation(conversation)
        if request.is_title_generate or conversation.title is None:
            title = await get_title([ai_summary_response]) 
            conversation.title = title
            await update_conversation(conversation)
        else:
            title = conversation.title

        return {
            "user_prompt": user_prompt,
            "summary_response": ai_summary_response,
            "question_response": ai_question_response,
            "analyze_response": ai_analyze_response,
            "answers_response": ai_answers_response,
            "conversation_id": conversation.conversation_id,
            "title": title
        }
    except Exception as e:
        logger.error(f"Error in process_answer_and_generate_followup_resolver for request {request}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
