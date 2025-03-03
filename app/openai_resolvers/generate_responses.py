from fastapi import HTTPException, logger
from app.packages.mongodb import update_conversation
from app.openai_resolvers.openai_client import client
from app.type import Conversation


async def get_ai_response(messages, model="gpt-4o-mini"):
    response = await client.chat.completions.create(
        messages=messages,
        model=model,
    )
    return response.choices[0].message.content.strip()

def prompt_for_possible_answers(next_question: str, previous_answers: str):
    text = (
        f"Imagine you are the user and you are answering the question: '{next_question}'.\n"
        f"Based on the user's previous response, '{previous_answers}', generate several possible answers to the question.\n"
        "Generate several possible answers to the question based on the user's previous responses.\n"
    )
    return text

async def generate_responses(user_conversation: Conversation):
    try:
        ai_question_response = await get_ai_response(user_conversation.questions)
        user_conversation.questions.append({"role": "assistant", "content": ai_question_response})

        ai_summary_response = await get_ai_response(user_conversation.summaries)
        user_conversation.summaries.append({"role": "assistant", "content": ai_summary_response})

        ai_analyze_response = await get_ai_response(user_conversation.analyze)
        user_conversation.analyze.append({"role": "assistant", "content": ai_analyze_response})

        possible_answers_prompt = prompt_for_possible_answers(user_conversation.questions[-1]["content"], user_conversation.summaries[-1]["content"])
        user_conversation.answers.append({"role": "user", "content": possible_answers_prompt})

        ai_answers_response = await get_ai_response(user_conversation.answers)
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