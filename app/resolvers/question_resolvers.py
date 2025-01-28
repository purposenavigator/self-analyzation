from fastapi import HTTPException

from app.data import questions

async def get_all_questions_resolver():
    return [
        {"id": str(index), "title": title, "explanation": explanation}
        for index, (title, explanation) in enumerate(questions.items(), 1)
    ]

async def get_question_resolver(topic: str):
    if topic in questions:
        return {"title": topic, "explanation": questions[topic]}
    else:
        raise HTTPException(status_code=404, detail=f"Topic '{topic}' not found.")
