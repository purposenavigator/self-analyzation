from fastapi import HTTPException
from app.data import questions
from app.type import SystemRoles
from app.openai_resolvers.keyword_extraction import adviser_prompts
from app.exceptions import InvalidTopicException

def create_question_system_role(primary_question: str):
    return f"You are an assistant that asks questions to guide the user to reflect on their values. The question is the first question:'{primary_question}'"

def create_summary_system_role(primary_question: str):
    return f"You are an assistant that summarizes the user's responses to the question: '{primary_question}'"

def create_answers_system_role(primary_question: str):
    text = (
        f"You are an assistant that generates several possible answers which the user might answer to the question: '{primary_question}'.\n"
        "Express the answers as json objects. Please add title and answer\n"
    )
    return text

def check_topic(topic: str):
    if topic not in questions:
        raise InvalidTopicException(topic)

def get_system_role(topic: str) -> SystemRoles:
    try:
        check_topic(topic)
        question = questions[topic]
        summary_role_content = create_summary_system_role(question)
        question_role_content = create_question_system_role(question)
        answer_role_content = create_answers_system_role(question)

        summary_role = {"role": "system", "content": summary_role_content}
        question_role = {"role": "system", "content": question_role_content}
        analyze_role = {"role": "system", "content": adviser_prompts}
        answer_role = {"role": "system", "content": answer_role_content}

        system_roles = {
            "summary": summary_role,
            "question": question_role,
            "analyze": analyze_role,
            "answers": answer_role
        }
        return system_roles
    except InvalidTopicException as e:
        raise HTTPException(status_code=500, detail=e.message)
