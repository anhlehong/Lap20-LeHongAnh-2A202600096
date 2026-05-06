"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import AgentExecutionError


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.timeout = settings.timeout_seconds

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion with retry logic and token tracking."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                timeout=self.timeout,
            )

            content = response.choices[0].message.content or ""
            usage = response.usage

            # Estimate cost (approximate rates for gpt-4o-mini)
            cost_usd = None
            if usage:
                input_cost = (usage.prompt_tokens / 1_000_000) * 0.15  # $0.15 per 1M input tokens
                output_cost = (
                    usage.completion_tokens / 1_000_000
                ) * 0.60  # $0.60 per 1M output tokens
                cost_usd = input_cost + output_cost

            return LLMResponse(
                content=content,
                input_tokens=usage.prompt_tokens if usage else None,
                output_tokens=usage.completion_tokens if usage else None,
                cost_usd=cost_usd,
            )

        except Exception as e:
            raise AgentExecutionError(f"LLM completion failed: {e}") from e
