# main.py
from fastapi import FastAPI, HTTPException
from typing import List
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from mongodb import get_conversation, get_next_id, update_conversation
from questions import create_system_role, get_system_role
from type import GPTRequest, Query, UserConversation

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
        conversation = await get_conversation(query)
        if not conversation_id:
            system_role = {"role": "system", "content": content}
            conversation["messages"].append(system_role)
            conversation_id = await get_next_id("conversation_id")  

        # Add the user's request to the conversation
        conversation["messages"].append({"role": "user", "content": request.prompt})

        # Call the OpenAI API
        response = await client.chat.completions.create(
            messages=conversation["messages"],
            model="gpt-4o-mini",
        )
        
        # Extract the AI's response and add it to the conversation
        ai_response = response.choices[0].message.content.strip()
        conversation["messages"].append({"role": "assistant", "content": ai_response})

        # Save the updated conversation back to MongoDB
        user_conversation = UserConversation(request.user_id, conversation_id, conversation)
        await update_conversation(user_conversation)
        
        return {"response": ai_response, "conversation_id":conversation_id }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

