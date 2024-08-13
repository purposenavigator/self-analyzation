
import os
from fastapi import HTTPException
from openai import AsyncOpenAI
from app.models import GPTRequest, UserConversation, UserConversationQuery
from app.mongodb import get_conversation, update_conversation
from app.questions import get_system_role
import logging

client = AsyncOpenAI(
    api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)


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

        user_conversation = await get_conversation(query)
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

async def process_answer_and_generate_followup(request: GPTRequest):
    try:
        user_conversation = await process_conversation(request)
        ai_question_response, ai_summary_response, ai_analyze_response = await generate_responses(user_conversation)

        return {
            "summary_response": ai_summary_response,
            "question_response": ai_question_response,
            "analyze_response": ai_analyze_response,
            "conversation_id": user_conversation.conversation_id
        }
    except Exception as e:
        logger.error(f"Error in process_answer_and_generate_followup for request {request}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

