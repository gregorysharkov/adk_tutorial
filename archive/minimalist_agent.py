import os
from openai import OpenAI


class MinimalisticAgent:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_response(
        self, prompt: str, system_message: str = "You are a helpful AI assistant."
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,  # Limit the response length
                temperature=0.7,  # Control randomness (0.0 is deterministic, 1.0 is very creative)
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"An error occurred: {e}"
