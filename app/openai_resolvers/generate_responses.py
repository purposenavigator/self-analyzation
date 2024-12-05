from fastapi import HTTPException, logger
from app.models import UserConversation
from app.mongodb import update_conversation
from app.openai_client import client


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

        answers_response = await client.chat.completions.create(
            messages=user_conversation.answers,
            model="gpt-4o-mini",
        )
        ai_answers_response = answers_response.choices[0].message.content.strip()
        user_conversation.answers.append({"role": "assistant", "content": ai_answers_response})

        await update_conversation(user_conversation)

        return ai_question_response, ai_summary_response, ai_analyze_response, ai_answers_response
    except Exception as e:
        logger.error(f"Error generating responses for conversation {user_conversation.conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while generating responses.")
