from app.openai_resolvers.keyword_extraction import create_prompt_for_single_sentence, create_prompts_for_multiple_sentences, fetch_keywords_from_api, fetch_keywords_from_api_only_one
from app.services.conversation_services import process_conversation
from fastapi import HTTPException
from app import questions
from app.openai_resolvers.get_title import get_title
from app.openai_resolvers.generate_responses import generate_responses
from app.models import AnalayzeRequest, AnalyzeQuery, GPTRequest, SimpleConversationQuery, UserConversation, UserConversationQuery, UserConversationRequest, UserIdRequest
from app.mongodb import create_conversation, fetch_user_data_from_db, get_analyze, get_conversation, get_conversation_by_id, init_or_get_conversation, store_keywords, update_conversation, update_or_append_field_by_id, get_analysis_summary_by_sha
from app.questions import get_system_role
from app.openai_client import client
import hashlib
import logging

logger = logging.getLogger(__name__)

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

async def process_answer_resolver(request: AnalayzeRequest):
    try:
        first_conversation_id = request.conversation_id
        query = AnalyzeQuery(conversation_id=first_conversation_id)
        user_conversation = await get_analyze(query)
        analyze = [analyze for analyze in user_conversation.analyze if analyze["role"] == "assistant"]
        return analyze
        
    except Exception as e:
        logger.error(f"Error in process_answer_resolver for request {request}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_retrieve_keywords_resolver(request: AnalayzeRequest):
    try:
        first_conversation_id = request.conversation_id
        query = AnalyzeQuery(conversation_id=first_conversation_id)
        user_conversation = await get_analyze(query)
        analyze = [analyze['content'] for analyze in user_conversation.analyze if analyze["role"] == "assistant"]

        if hasattr(user_conversation, 'keywords') and user_conversation.keywords:
            keywords = [keyword for keyword in user_conversation.keywords]
        else:
            keywords = [] 

        if len(analyze) > len(keywords):
            missing_analyze = analyze[len(keywords):]
            prompts = create_prompts_for_multiple_sentences(missing_analyze)
            
            responses = await fetch_keywords_from_api(prompts)
            new_keywords = [response.choices[0].message.content.strip() for response in responses]
            
            keywords.extend(new_keywords)
            
            await store_keywords(first_conversation_id, keywords)

            return keywords
        
    except Exception as e:
        logger.error(f"Error in process_retrieve_keywords_resolver for request {request}: {e}")
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

async def get_all_questions_resolver():
    return [{"id": str(i), "title": k, "explanation": v} for i, (k, v) in enumerate(questions.questions.items(), 1)]

async def get_question_resolver(topic: str):
    if topic in questions.questions:
        return {"title": topic, "explanation": questions.questions[topic]}
    else:
        raise HTTPException(status_code=404, detail=f"Topic '{topic}' not found.")

async def get_analyze_resolver(conversation_id: str):
    """
    Fetches and analyzes the conversation by extracting keywords from summaries.
    Returns existing analysis if SHA matches, otherwise generates new analysis.

    Args:
        conversation_id (str): The ID of the conversation to analyze.

    Returns:
        str: The analysis summary.

    Raises:
        HTTPException: If there is an error during data fetching or processing.
    """
    try:
        user_conversation = await get_conversation_by_id(conversation_id)
        
        # Combine all assistant summaries
        summaries_content = " ".join(
            summary['content'] 
            for summary in user_conversation['summaries'] 
            if summary["role"] == "assistant"
        )

        # Generate SHA-256 hash of the combined summaries
        sha256_hash = hashlib.sha256(summaries_content.encode('utf-8')).hexdigest()
        
        # Try to get existing analysis summary
        existing_summary = await get_analysis_summary_by_sha(conversation_id, sha256_hash)
        
        if existing_summary:
            return existing_summary
            
        # If no existing summary, generate new one
        prompts = create_prompt_for_single_sentence(summaries_content)
        api_response = await fetch_keywords_from_api_only_one(prompts)
        analysis_summary = api_response.choices[0].message.content.strip()
        
        # Store the new analysis summary
        await update_or_append_field_by_id(
            conversation_id=conversation_id,
            field_name="analysis_summaries",
            key=sha256_hash,
            value=analysis_summary
        )
        
        return analysis_summary
        
    except Exception as error:
        logger.error(f"Error in get_analyze_resolver: {error}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching data.")

