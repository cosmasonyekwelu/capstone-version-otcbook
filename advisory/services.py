from groq import Groq
from django.conf import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_client = Groq(api_key=settings.GROQ_API_KEY)


class AdvisoryAIService:
    SYSTEM_PROMPT = """
You are a financial education assistant.
You provide general risk awareness, sizing concepts,
and performance interpretation for bookkeeping users.
Always include a disclaimer.
"""

    MAX_INPUT_LENGTH = 2_000
    MAX_OUTPUT_LENGTH = 4_000

    @staticmethod
    def ask(question: str) -> str:

        if not isinstance(question, str):
            raise TypeError("Question must be a string")

        question = question.strip()
        if not question:
            raise ValueError("Question cannot be empty")

        if len(question) > AdvisoryAIService.MAX_INPUT_LENGTH:
            raise ValueError("Question exceeds allowed length")

        try:
            completion = _client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": AdvisoryAIService.SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
                temperature=0.4,
                max_tokens=700,
            )

            content: Optional[str] = (
                completion.choices[0].message.content
                if completion.choices
                else None
            )

            if not content:
                raise RuntimeError("AI returned empty response")

            content = content.strip()

            if len(content) > AdvisoryAIService.MAX_OUTPUT_LENGTH:
                content = content[:AdvisoryAIService.MAX_OUTPUT_LENGTH].rstrip() + "…"

            return content

        except Exception:

            logger.exception("AdvisoryAIService failure")


            return (
                "The advisory service is temporarily unavailable. "
                "Please try again later."
            )
