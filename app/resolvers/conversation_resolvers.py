import logging
from fastapi import HTTPException
from app.models import UserConversation, UserConversationRequest, SimpleConversationQuery, UserIdRequest, GPTRequest
from app.mongodb import get_conversation, fetch_user_data_from_db, update_conversation
from app.services.conversation_services import process_conversation
from app.openai_resolvers.get_title import get_title
from app.openai_resolvers.generate_responses import generate_responses

logger = logging.getLogger(__name__)

async def get_conversation_resolver(request: UserConversationRequest) -> UserConversation:
    try:
        conversation_id = request.conversation_id
        user_id = request.user_id
        query = SimpleConversationQuery(conversation_id=conversation_id, user_id=user_id)
        user_conversation = await get_conversation(query)
        if not user_conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return user_conversation
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger.error(f"Error in get_conversation for request {request}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_all_user_conversations_resolver(user_request: UserIdRequest):
    """
    Calls the database function and handles the case where no data is found.
    Takes a Pydantic model to retrieve user_id.
    """
    try:
        user_data = await fetch_user_data_from_db(user_request.user_id)
        
        if not user_data:
            raise ValueError(f"No data found for user_id {user_request.user_id}")
        
        return user_data
    except ValueError as ve:
        logger.warning(ve)
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Resolver error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching data.")

async def process_answer_and_generate_followup_resolver(request: GPTRequest):
    try:
        user_conversation = await process_conversation(request)
        user_prompt = request.prompt
        ai_question_response, ai_summary_response, ai_analyze_response, ai_answers_response = await generate_responses(user_conversation)
        await update_conversation(user_conversation)
        if request.is_title_generate or user_conversation.title is None:
            title = await get_title([ai_summary_response]) 
            user_conversation.title = title
            await update_conversation(user_conversation)
        else:
            title = user_conversation.title

        return {
            "user_prompt": user_prompt,
            "summary_response": ai_summary_response,
            "question_response": ai_question_response,
            "analyze_response": ai_analyze_response,
            "answers_response": ai_answers_response,
            "conversation_id": user_conversation.conversation_id,
            "title": title
        }
    except Exception as e:
        logger.error(f"Error in process_answer_and_generate_followup_resolver for request {request}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
