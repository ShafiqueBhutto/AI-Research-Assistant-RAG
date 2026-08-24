from app.services.llm_service import LLMService


llm = LLMService()

answer = llm.generate_answer(
    question="What is Python?",
    context="Python is a high-level programming language."
)

print("\nGemini Answer:")
print(answer)