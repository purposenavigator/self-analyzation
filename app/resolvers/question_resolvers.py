from fastapi import HTTPException
from app import questions

async def get_all_questions_resolver():
    return [{"id": str(i), "title": k, "explanation": v} for i, (k, v) in enumerate(questions.questions.items(), 1)]

async def get_question_resolver(topic: str):
    if topic in questions.questions:
        return {"title": topic, "explanation": questions.questions[topic]}
    else:
        raise HTTPException(status_code=404, detail=f"Topic '{topic}' not found.")
