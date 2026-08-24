import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LLMService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Please add it to your .env file."
            )

        self.client = genai.Client(api_key=api_key)

        self.model = "gemini-3.6-flash"

    def generate_answer(
        self,
        question: str,
        context: str
    ) -> str:

        prompt = f"""
You are an AI Research Assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Do not use outside knowledge.
- Do not make up information.
- If the answer cannot be found in the context, say:
  "I could not find the answer in the provided documents."
- Give a clear and concise answer.

Context:
{context}

Question:
{question}

Answer:
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text