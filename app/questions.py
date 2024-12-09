from fastapi import HTTPException

from app.type import SystemRole, SystemRoles
from app.openai_resolvers.keyword_extraction import adviser_prompts



questions = {
    "Test": "What is your favorite color?",
    "Inspiration": "Who is someone that stimulates you when you meet them? What about them stimulates you? Does it relate to your values?",
    "Influence": "Who is the person who has the most influence on you right now? What actions or words of this person affect you?",
    "Father": "What do you like and dislike about your father's way of living? Do your current values reflect your father's values? Or are they the opposite?",
    "Mother": "What do you like and dislike about your mother's way of living? Do your current values reflect your mother's values? Or are they the opposite?",
    "Legacy": "After you die, how would you like to be described by the people around you? What does that reveal about your values?",
    "Book": "Among the books you have read so far, which one is your favorite? What does that reveal about your values?",
    "Emotion": "What kinds of things move you? What is the most moving experience you have had? What does that reveal about your values?",
    "Reflection": "(Imagine you are 80 years old and fill in the blanks) I spent too much time on □□□. I hardly spent any time on □□□. If I could turn back time, I would like to spend my time on □□□. What does that reveal about your values?"
}

def create_question_system_role(primary_question: str):
    return f"You are an assistant that asks questions to guide the user to reflect on their values. The question is the first question:'{primary_question}'"

def create_summary_system_role(primary_question: str):
    return f"You are an assistant that summarizes the user's responses to the question: '{primary_question}'"

#"Add the following styles to the HTML elements:\n"
#'- Add `style="display: block; margin-bottom: 0.5rem; font-size: 1.25rem; line-height: 1.75rem;"` to the `<p>` tag for the paragraph.\n'
#'- Add `style="display: block; font-size: 1.25rem; line-height: 1.75rem;"` to each `<li>` tag in the ordered list.\n\n'
#"This prompt guides the AI to produce the desired format in HTML while focusing on values analysis and integrating specific tags for structure."

def create_answers_system_role(primary_question: str):
    text = (
        f"You are an assistant that generates several possible answers which the user might answer to the question: '{primary_question}'.\n"
        "Express the answers as json objects. Please add title and answer\n"
    )
    return text

def prompt_for_possible_answers(next_question: str, previous_answers: str):
    text = (
        f"Imagine you are the user and you are answering the question: '{next_question}'.\n"
        f"Based on the user's previous response, '{previous_answers}', generate several possible answers to the question.\n"
        "Generate several possible answers to the question based on the user's previous responses.\n"
    )
    return text

def check_topic(topic: str):
    if topic not in questions:
        raise HTTPException(status_code=500, detail=f"Invalid topic: {topic}")

def get_system_role(topic: str) -> SystemRoles:
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
