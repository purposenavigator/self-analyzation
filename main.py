# main.py
from fastapi import FastAPI, HTTPException
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from models import GPTRequest, ConversationQuery
from mongodb import get_conversation, get_next_id, update_conversation
from questions import  get_system_role

load_dotenv()

client = AsyncOpenAI(
    api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

app = FastAPI()

@app.post("/generate")
async def generate_text(request: GPTRequest):
    try:
        topic = request.topic
        system_roles = get_system_role(topic)

        query = ConversationQuery(user_id=request.user_id, conversation_id=request.conversation_id)
        conversation_id = request.conversation_id
        user_conversation = await get_conversation(query)
        if not conversation_id:

            question_role = system_roles["question"]
            summary_role = system_roles["summary"]
            conversation_id = await get_next_id("conversation_id")  

            user_conversation.questions.append(question_role)
            user_conversation.summaries.append(summary_role)
            user_conversation.conversation_id = conversation_id

        user_conversation.questions.append({"role": "user", "content": request.prompt})
        user_conversation.summaries.append({"role": "user", "content": request.prompt})

        await update_conversation(user_conversation)

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

        await update_conversation(user_conversation)
        
        return {
            "summary_response": ai_summary_response, "question_response": ai_question_response, "conversation_id":conversation_id }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

