# main.py
from fastapi import FastAPI
from dotenv import load_dotenv
from app.models import AnalayzeRequest, GPTRequest, UserConversationRequest
from app.resolvers import get_conversation_resolver, process_answer_resolver, process_answer_and_generate_followup_resolver, process_retrieve_keywords_resolver

load_dotenv()

app = FastAPI()

@app.post("/conversation")
async def api_process_answer_and_generate_followup_resolver(request: GPTRequest):
    return await process_answer_and_generate_followup_resolver(request)

@app.get("/get_conversation")
async def api_get_conversation(request: UserConversationRequest):
    return await get_conversation_resolver(request)

@app.post("/answer")
async def api_process_answer(request: AnalayzeRequest):
    return await process_answer_resolver(request)

@app.post("/retrieve_keywords")
async def retrieve_keywords(request: AnalayzeRequest):
    return await process_retrieve_keywords_resolver(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

