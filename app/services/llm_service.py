import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LLMService:

    def __init__(self):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Please add it to your .env file."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.6-flash"

    # ============================================================
    # GENERATE ANSWER
    # ============================================================

    def generate_answer(
        self,
        question: str,
        context: str,
        conversation_history: str = ""
    ) -> str:

        if conversation_history:

            history_section = f"""
Previous Conversation:
{conversation_history}
"""

        else:

            history_section = """
Previous Conversation:
No previous conversation.
"""

        prompt = f"""
You are an AI Research Assistant.

Your job is to answer questions using the provided
document context.

IMPORTANT RULES:

1. Use the provided document context as the primary
   source of truth.

2. Do not invent information.

3. Do not use outside knowledge when answering
   document-specific questions.

4. You may use the previous conversation only to
   understand what the user is referring to.

5. If the user asks a follow-up question such as:
   "What about his education?"
   use the previous conversation to understand
   the reference, but answer using the provided
   document context.

6. If the requested information is not available
   in the document context, clearly say:

   "I could not find the answer in the provided documents."

7. Give natural, clear and concise answers.

8. Do not unnecessarily mention that you are an AI.

9. Do not repeat the entire previous conversation.

10. Answer directly.

{history_section}

Retrieved Document Context:
{context}

Current User Question:
{question}

Answer:
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        if not response.text:

            return (
                "I could not generate an answer "
                "from the provided document."
            )

        return response.text.strip()