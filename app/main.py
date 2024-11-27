# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.models import AnalayzeRequest, GPTRequest, UserConversationRequest, UserIdRequest
from app.resolvers import get_all_questions_resolver, get_all_user_conversations_resolver, get_conversation_resolver, get_question_resolver, process_answer_resolver, process_answer_and_generate_followup_resolver, process_retrieve_keywords_resolver
from app.type import Conversation

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:3000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/conversation")
async def api_process_answer_and_generate_followup_resolver(request: GPTRequest):
    return await process_answer_and_generate_followup_resolver(request)

@app.post("/get_conversation")
async def api_get_conversation(request: UserConversationRequest):
    return await get_conversation_resolver(request)

@app.post("/answer")
async def api_process_answer(request: AnalayzeRequest):
    return await process_answer_resolver(request)

@app.post("/retrieve_keywords")
async def retrieve_keywords(request: AnalayzeRequest):
    return await process_retrieve_keywords_resolver(request)

@app.post("/user_conversations")
async def get_user_data(user_request: UserIdRequest):
    return await get_all_user_conversations_resolver(user_request)

@app.get("/questions")
async def get_questions():
    return await get_all_questions_resolver()

@app.get("/question/{topic}")
async def get_question(topic):
    return await get_question_resolver(topic)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

