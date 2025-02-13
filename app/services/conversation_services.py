from fastapi import HTTPException
from app.packages.models.conversation_models import GPTRequest, UserConversationQuery
from app.packages.mongodb import init_or_get_conversation, create_conversation
from app.services.get_system_role import get_system_role
from app.type import Conversation
import logging

logger = logging.getLogger(__name__)

async def process_conversation(request: GPTRequest, user_id: str) -> Conversation:
    try:
        topic = request.topic
        system_roles = get_system_role(topic)
        first_conversation_id = request.conversation_id

        query = UserConversationQuery(
            conversation_id=first_conversation_id,
            user_id=user_id,
            topic=topic,
        )

        conversation = await init_or_get_conversation(query)
        if not first_conversation_id:
            question_role = system_roles["question"]
            summary_role = system_roles["summary"]
            analyzer_role = system_roles["analyze"]
            answers_role = system_roles["answers"]

            conversation.questions.append(question_role)
            conversation.summaries.append(summary_role)
            conversation.analyze.append(analyzer_role)
            conversation.answers.append(answers_role)

        conversation.questions.append({"role": "user", "content": request.prompt})
        conversation.summaries.append({"role": "user", "content": request.prompt})
        conversation.analyze.append({"role": "user", "content": request.prompt})

        if not conversation.conversation_id:
            conversation.conversation_id = await create_conversation(conversation)

        return conversation
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Error processing conversation for request {request}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing conversation.")
