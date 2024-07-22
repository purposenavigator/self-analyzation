from fastapi import HTTPException


questions = {
    "Inspiration": "Who is someone that stimulates you when you meet them? What about them stimulates you? Does it relate to your values?",
    "Influence": "Who is the person who has the most influence on you right now? What actions or words of this person affect you?",
    "Father": "What do you like and dislike about your father's way of living? Do your current values reflect your father's values? Or are they the opposite?",
    "Mother": "What do you like and dislike about your mother's way of living? Do your current values reflect your mother's values? Or are they the opposite?",
    "Legacy": "After you die, how would you like to be described by the people around you? What does that reveal about your values?",
    "Book": "Among the books you have read so far, which one is your favorite? What does that reveal about your values?",
    "Emotion": "What kinds of things move you? What is the most moving experience you have had? What does that reveal about your values?",
    "Reflection": "(Imagine you are 80 years old and fill in the blanks) I spent too much time on □□□. I hardly spent any time on □□□. If I could turn back time, I would like to spend my time on □□□. What does that reveal about your values?"
}

def create_system_role(primary_question: str):
    return f"You are an assistant that summarizes the user's input and asks follow-up questions to gain more information. Additionally, you must ensure that the discussion includes the primary question: '{primary_question}'"


def check_topic(topic: str):
    if topic not in questions:
        raise HTTPException(status_code=400, detail=f"Invalid topic: {topic}")

def get_system_role(topic: str):
    check_topic(topic)
    return create_system_role(questions[topic])