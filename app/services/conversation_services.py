from fastapi import HTTPException
from app.models import GPTRequest, UserConversation, UserConversationQuery
from app.mongodb import init_or_get_conversation, create_conversation
from app.questions import get_system_role
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
            topic=topic,
        )

        user_conversation = await init_or_get_conversation(query)
        if not first_conversation_id:
            question_role = system_roles["question"]
            summary_role = system_roles["summary"]
            analyzer_role = system_roles["analyze"]
            answers_role = system_roles["answers"]

            user_conversation.questions.append(question_role)
            user_conversation.summaries.append(summary_role)
            user_conversation.analyze.append(analyzer_role)
            user_conversation.answers.append(answers_role)

        user_conversation.questions.append({"role": "user", "content": request.prompt})
        user_conversation.summaries.append({"role": "user", "content": request.prompt})
        user_conversation.analyze.append({"role": "user", "content": request.prompt})

        if not user_conversation.conversation_id:
            user_conversation.conversation_id = await create_conversation(user_conversation)

        return user_conversation
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Error processing conversation for request {request}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing conversation.")
