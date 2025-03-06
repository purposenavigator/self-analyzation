from app.openai_resolvers.openai_client import client

system_prompt = {
    "role": "system",
    "content": "You are a title generation assistant. Your task is to read through a set of sentences provided by the user and create a concise, compelling, and relevant title that captures the main theme or purpose of the sentences. Ensure that the title is engaging and aligns with the content, using language that is clear and impactful. Avoid using overly complex or ambiguous words, and aim for a length of no more than 8-10 words unless otherwise specified. The title should not contain any double quotes."
}

def create_client_role(sentences: list[str]) -> dict:
    combined_sentence = " ".join(sentences)
    return {"role": "user", "content": combined_sentence}

async def ask_title(sentences: list[str]) -> dict:
    client_role = create_client_role(sentences)
    print(client_role)
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[system_prompt, client_role]
    )

def retrieve_title(response: dict) -> str:
    return response.choices[0].message.content.strip()

async def get_title(sentences: list[str]) -> str:
    response = await ask_title(sentences)
    return retrieve_title(response)