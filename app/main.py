# main.py
from fastapi import FastAPI
from dotenv import load_dotenv
from app.models import AnalayzeRequest, GPTRequest
from app.resolvers import process_answer, process_answer_and_generate_followup

load_dotenv()

app = FastAPI()

@app.post("/conversation")
async def api_process_answer_and_generate_followup(request: GPTRequest):
    return await process_answer_and_generate_followup(request)

@app.post("/answer")
async def api_process_answer(request: AnalayzeRequest):
    return await process_answer(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

