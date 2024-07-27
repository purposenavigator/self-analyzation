# main.py
from fastapi import FastAPI, HTTPException
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from models import GPTRequest, Query
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
        content = get_system_role(topic)

        # Fetch the existing conversation from MongoDB
        query = Query(user_id=request.user_id, conversation_id=request.conversation_id)
        conversation_id = request.conversation_id
        user_conversation = await get_conversation(query)
        if not conversation_id:
            system_role = {"role": "system", "content": content}
            user_conversation.messages.append(system_role)
            conversation_id = await get_next_id("conversation_id")  
            user_conversation.conversation_id = conversation_id

        # Add the user's request to the user_conversation
        user_conversation.messages.append({"role": "user", "content": request.prompt})

        # Call the OpenAI API
        response = await client.chat.completions.create(
            messages=user_conversation.messages,
            model="gpt-4o-mini",
        )
        
        # Extract the AI's response and add it to the conversation
        ai_response = response.choices[0].message.content.strip()
        user_conversation.messages.append({"role": "assistant", "content": ai_response})

        await update_conversation(user_conversation)
        
        return {"response": ai_response, "conversation_id":conversation_id }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

