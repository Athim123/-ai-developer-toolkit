import time
from typing import Any, Optional

from groq import Groq

from app.core.config import settings
from app.core.logging import logger

_client: Optional[Groq] = None


def get_client() -> Groq:
    global _client
    if _client is None:
        if not settings.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your .env file (see .env.example)."
            )
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def chat_completion(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1024,
    tools: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Calls the Groq chat completions API and returns a normalized result:
    {
        "content": str | None,
        "tool_calls": list | None,
        "latency_ms": float,
        "usage": dict,
        "model": str,
    }
    """
    client = get_client()
    chosen_model = model or settings.groq_model
    start = time.perf_counter()

    kwargs: dict[str, Any] = {
        "model": chosen_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    try:
        completion = client.chat.completions.create(**kwargs)
    except Exception:
        logger.exception("Groq completion request failed")
        raise

    latency_ms = (time.perf_counter() - start) * 1000
    choice = completion.choices[0]
    message = choice.message

    return {
        "content": message.content,
        "tool_calls": [tc.model_dump() for tc in message.tool_calls] if message.tool_calls else None,
        "latency_ms": latency_ms,
        "usage": completion.usage.model_dump() if completion.usage else {},
        "model": chosen_model,
    }
