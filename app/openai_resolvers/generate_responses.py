from fastapi import HTTPException, logger
from app.questions import prompt_for_possible_answers  # Import the function
from app.models import UserConversation
from app.mongodb import update_conversation
from app.openai_resolvers.openai_client import client


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

        possible_answers_prompt = prompt_for_possible_answers(user_conversation.questions[-1]["content"], user_conversation.summaries[-1]["content"])
        user_conversation.answers.append({"role": "user", "content": possible_answers_prompt})
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

async def get_answer(responses: list):
    try:
        answers_response = await client.chat.completions.create(
            messages=responses.answers,
            model="gpt-4o-mini",
        )
        ai_answers_response = answers_response.choices[0].message.content.strip()
        responses.answers.append({"role": "assistant", "content": ai_answers_response})

        await update_conversation(responses)

        return ai_answers_response
    except Exception as e:
        logger.error(f"Error generating title for responses: {responses}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while generating title.")