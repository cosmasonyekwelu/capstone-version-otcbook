from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)


class AdvisoryAIService:
    SYSTEM_PROMPT = """
You are a financial education assistant.
You provide general risk awareness, sizing concepts,
and performance interpretation for bookkeeping users.
Always include a disclaimer.
"""

    @staticmethod
    def ask(question: str):
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": AdvisoryAIService.SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.4,
        )

        return completion.choices[0].message.content
