from fastapi import Depends, FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.packages.models.conversation_models import (
    AnalayzeRequest, 
    GPTRequest, 
    UserConversationRequest, 
)
from app.packages.repositories.user.auth import get_current_user
from app.resolvers import (
    get_all_questions_resolver, 
    get_question_resolver, 
    process_answer_resolver, 
    process_retrieve_keywords_resolver, 
    get_analyze_resolver,
    get_conversation_resolver, 
    get_all_user_conversations_resolver, 
    process_answer_and_generate_followup_resolver
)
from app.resolvers.analyze_resolvers import get_consolidated_and_labeled_values_for_user  # Update import
from app.resolvers.user_resolvers import register, login, logout
from app.packages.schemas.user_schema import UserCreate, UserLogin

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:3000",  
    "http://34.45.225.35:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],         # Allow all HTTP methods
    allow_headers=["*"],         # Allow all headers
)

# User routes
@app.post("/register")
async def api_register(user: UserCreate, response: Response):
    # Register a new user
    return await register(user, response)

@app.post("/login")
async def api_login(user: UserLogin, response: Response):
    # Login an existing user
    return await login(user, response)

@app.post("/logout")
async def api_logout(response: Response):
    # Logout the current user
    return await logout(response)

@app.get("/current_user")
async def api_get_current_user(request: Request):
    # Get the current logged-in user
    return await get_current_user(request)

# Conversation routes
@app.post("/conversation")
async def api_process_answer_and_generate_followup_resolver(request: GPTRequest, current_user: dict = Depends(get_current_user)):
    # Process an answer and generate a follow-up question
    return await process_answer_and_generate_followup_resolver(request, str(current_user['id']))

@app.post("/get_conversation")
async def api_get_conversation(request: UserConversationRequest, current_user: dict = Depends(get_current_user)):
    # Get a specific conversation for the current user
    return await get_conversation_resolver(request, str(current_user['id']))

@app.post("/user_conversations")
async def get_user_data(current_user: dict = Depends(get_current_user)):
    # Get all conversations for the current user
    return await get_all_user_conversations_resolver(str(current_user['id']))

@app.post("/user_all_values")
async def get_all_values_for_user(current_user: dict = Depends(get_current_user)):
    # Get all consolidated and labeled values for the current user
    return await get_consolidated_and_labeled_values_for_user(str(current_user['id']))

# Question routes
@app.get("/questions")
async def get_questions(current_user: dict = Depends(get_current_user)):
    # Get all questions
    return await get_all_questions_resolver()

@app.get("/question/{topic}")
async def get_question(topic, current_user: dict = Depends(get_current_user)):
    # Get a specific question by topic
    return await get_question_resolver(topic)

# Analyze routes
@app.post("/answer")
async def api_process_answer(request: AnalayzeRequest, current_user: dict = Depends(get_current_user)):
    # Process an answer for a given request
    return await process_answer_resolver(request)

@app.post("/retrieve_keywords")
async def retrieve_keywords(request: AnalayzeRequest, current_user: dict = Depends(get_current_user)):
    # Retrieve keywords for a given request
    return await process_retrieve_keywords_resolver(request)

@app.get("/analyze/{conversation_id}")
async def get_analyze(conversation_id: str, current_user: dict = Depends(get_current_user)):
    # Get analysis for a specific conversation
    return await get_analyze_resolver(conversation_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

