from openai import OpenAI
import os

# Get the API key from the environment variables
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
model = "gpt-4o"

def get_chat_completion(messages):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "As QA engineer, you are an AI assistant for image analysis"},
            {"role": "user", "content": messages},
        ]
    )
    return response