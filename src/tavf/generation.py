"""One initial TAVF generation through the shared LLM client."""

from collections.abc import Mapping

from utils.llm_client import LLMClient


class GenerationError(RuntimeError):
    """Generation failed or returned no usable output."""


def generate_initial_output(prompt: str, client=None) -> dict:
    """Generate once and return output with available request metadata.

    Supply an LLMClient (or a mock) to control configuration. No retries,
    logging, validation, or refinement are performed here. Missing metadata
    remains None. Provider error details are not included in public errors.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must be a non-empty string.")

    try:
        if client is None:
            client = LLMClient()
        response = client.generate(prompt)
    except Exception:
        raise GenerationError("Initial LLM generation failed.") from None

    if not isinstance(response, Mapping):
        raise GenerationError("Initial LLM generation returned an invalid response.")
    output = response.get("output")
    if not isinstance(output, str) or not output.strip():
        raise GenerationError("Initial LLM generation returned an empty output.")

    return {
        "output": output,
        **{
            field: response.get(field)
            for field in (
                "model", "input_tokens", "output_tokens", "cached_input_tokens",
                "execution_time_seconds", "parameters", "response_id", "timestamp",
            )
        },
    }
