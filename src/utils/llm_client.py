
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL = "gpt-5.4-mini-2026-03-17"
MAX_OUTPUT_TOKENS = 8192


class LLMClient:
    """Reusable interface for OpenAI model requests."""

    def __init__(
        self,
        model=DEFAULT_MODEL,
        reasoning_effort="none",
        max_output_tokens=MAX_OUTPUT_TOKENS,
        client=None,
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_output_tokens = max_output_tokens

        # Allows a fake client to be supplied during local tests.
        if client is not None:
            self.client = client
        else:
            load_dotenv(ROOT / ".env")

            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError(
                    "OPENAI_API_KEY is missing."
                )

            from openai import OpenAI

            self.client = OpenAI(
                max_retries=0,
                timeout=120,
            )

    def generate(self, prompt):
        """Send a prompt and return output with request metadata."""

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        start = time.perf_counter()

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            reasoning={
                "effort": self.reasoning_effort
            },
            max_output_tokens=self.max_output_tokens,
        )

        elapsed = time.perf_counter() - start

        output = response.output_text

        if not output or not output.strip():
            raise ValueError(
                "Model returned an empty output."
            )

        usage = response.usage

        cached_tokens = 0

        if usage:
            details = getattr(
                usage,
                "input_tokens_details",
                None,
            )

            if details:
                cached_tokens = (
                    getattr(details, "cached_tokens", 0) or 0
                )

        return {
            "model": self.model,
            "output": output,
            "response_id": response.id,
            "parameters": {
                "reasoning_effort": self.reasoning_effort,
                "max_output_tokens": self.max_output_tokens,
            },
            "execution_time_seconds": round(elapsed, 3),
            "input_tokens": (
                usage.input_tokens if usage else None
            ),
            "output_tokens": (
                usage.output_tokens if usage else None
            ),
            "cached_input_tokens": cached_tokens,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }
