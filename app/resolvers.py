
from fastapi import HTTPException
from app import questions
from app.keyword_extraction import fetch_keywords_from_api, generate_keyword_extraction_prompts
from app.models import AnalayzeRequest, AnalyzeQuery, GPTRequest, SimpleConversationQuery, UserConversation, UserConversationQuery, UserConversationRequest, UserIdRequest
from app.mongodb import fetch_user_data_from_db, get_analyze, get_conversation, init_or_get_conversation, store_keywords, update_conversation
from app.questions import get_system_role
from app.openai_client import client

import logging


logger = logging.getLogger(__name__)

async def process_conversation(request: GPTRequest) -> UserConversation:
    try:
        topic = request.topic
        system_roles = get_system_role(topic)
        first_conversation_id = request.conversation_id

        query = UserConversationQuery(
            conversation_id=first_conversation_id,
            user_id=request.user_id,
            topic=topic
        )

        user_conversation = await init_or_get_conversation(query)
        if not first_conversation_id:
            question_role = system_roles["question"]
            summary_role = system_roles["summary"]
            analyzer_role = system_roles["analyze"]

            user_conversation.questions.append(question_role)
            user_conversation.summaries.append(summary_role)
            user_conversation.analyze.append(analyzer_role)

        user_conversation.questions.append({"role": "user", "content": request.prompt})
        user_conversation.summaries.append({"role": "user", "content": request.prompt})
        user_conversation.analyze.append({"role": "user", "content": request.prompt})

        if not first_conversation_id:
            user_conversation.conversation_id = await update_conversation(user_conversation)

        return user_conversation
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Error processing conversation for request {request}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing conversation.")

async def generate_responses(user_conversation: UserConversation):
    try:
        question_response = await client.chat.completions.create(
            messages=user_conversation.questions,
            model="gpt-4o-mini",
        )
        ai_question_response = question_response.choices[0].message.content.strip()
        user_conversation.questions.append({"role": "assistant", "content": ai_question_response})

        summary_response = await client.chat.completions.create(
            messages=user_conversation.summaries,
            model="gpt-4o-mini",
        )
        ai_summary_response = summary_response.choices[0].message.content.strip()
        user_conversation.summaries.append({"role": "assistant", "content": ai_summary_response})

        analyze_response = await client.chat.completions.create(
            messages=user_conversation.analyze,
            model="gpt-4o-mini",
        )
        ai_analyze_response = analyze_response.choices[0].message.content.strip()
        user_conversation.analyze.append({"role": "assistant", "content": ai_analyze_response})

        await update_conversation(user_conversation)

        return ai_question_response, ai_summary_response, ai_analyze_response
    except Exception as e:
        logger.error(f"Error generating responses for conversation {user_conversation.conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while generating responses.")

async def process_answer_and_generate_followup_resolver(request: GPTRequest):
    try:
        user_conversation = await process_conversation(request)
        user_prompt = request.prompt
        ai_question_response, ai_summary_response, ai_analyze_response = await generate_responses(user_conversation)

        return {
            "user_prompt": user_prompt,
            "summary_response": ai_summary_response,
            "question_response": ai_question_response,
            "analyze_response": ai_analyze_response,
            "conversation_id": user_conversation.conversation_id
        }
    except Exception as e:
        logger.error(f"Error in process_answer_and_generate_followup_resolver for request {request}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_conversation_resolver(request: UserConversationRequest):
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
            prompts = generate_keyword_extraction_prompts(missing_analyze)
            
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
    return [{"id": i, "title": k, "explanation": v} for i, (k, v) in enumerate(questions.questions.items(), 1)]

