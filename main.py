# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from mongodb import get_conversation, update_conversation
from questions import create_system_role, get_system_role
import questions

load_dotenv()

client = AsyncOpenAI(
    api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

app = FastAPI()

class GPTRequest(BaseModel):
    user_id: int
    prompt: str
    topic: str
    max_tokens: int = 150

@app.post("/generate")
async def generate_text(request: GPTRequest):
    try:
        topic = request.topic
        content = get_system_role(topic)

        # Fetch the existing conversation from MongoDB
        found, conversation = await get_conversation(request.user_id)
        if not found:
            system_role = {"role": "system", "content": content}
            conversation["messages"].append(system_role)

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
        await update_conversation(request.user_id, conversation)
        
        return {"response": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

