import time

from anthropic import Anthropic

from app.core.config import settings

DEFAULT_MODEL = "claude-sonnet-4-6"
RETRY_DELAYS_SECONDS = [1, 2, 4]

_client = Anthropic(api_key=settings.LLM_API_KEY)


class LLMError(Exception):
    pass


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 2000) -> str:
    last_error: Exception | None = None
    for attempt, delay in enumerate(RETRY_DELAYS_SECONDS):
        try:
            response = _client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        except Exception as e:
            last_error = e
            if attempt < len(RETRY_DELAYS_SECONDS) - 1:
                time.sleep(delay)
    raise LLMError(f"LLM call failed after {len(RETRY_DELAYS_SECONDS)} attempts: {last_error}")
