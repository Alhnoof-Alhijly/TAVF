import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tavf.generation import GenerationError, generate_initial_output
from tavf.prompting import build_prompt
from utils.llm_client import LLMClient


class TestTAVFGeneration(unittest.TestCase):
    def test_existing_client_with_mock_provider_and_constructed_prompt(self):
        provider = Mock()
        provider.responses.create.return_value = SimpleNamespace(
            id="mock-response", output_text="Initial output", usage=SimpleNamespace(
                input_tokens=100, output_tokens=25,
                input_tokens_details=SimpleNamespace(cached_tokens=10),
            ),
        )
        client = LLMClient(model="mock-model", max_output_tokens=256, client=provider)
        prompt = build_prompt("bug_report_refinement", {"original_text": "Save crashes."})
        result = generate_initial_output(prompt, client)
        provider.responses.create.assert_called_once_with(
            model="mock-model", input=prompt, reasoning={"effort": "none"},
            max_output_tokens=256,
        )
        self.assertEqual(result["output"], "Initial output")
        self.assertEqual(result["model"], "mock-model")
        self.assertEqual(result["input_tokens"], 100)
        self.assertEqual(result["output_tokens"], 25)
        self.assertEqual(result["cached_input_tokens"], 10)
        self.assertGreaterEqual(result["execution_time_seconds"], 0)
        self.assertEqual(result["parameters"], {
            "reasoning_effort": "none", "max_output_tokens": 256,
        })

    def test_missing_metadata_stays_missing_and_extra_fields_are_excluded(self):
        client = Mock()
        client.generate.return_value = {"output": "Generated", "api_key": "secret"}
        result = generate_initial_output("Prompt", client)
        client.generate.assert_called_once_with("Prompt")
        self.assertEqual(result["output"], "Generated")
        self.assertIsNone(result["input_tokens"])
        self.assertIsNone(result["execution_time_seconds"])
        self.assertNotIn("api_key", result)

    def test_invalid_prompts_do_not_construct_or_call_client(self):
        client = Mock()
        with patch("tavf.generation.LLMClient") as factory:
            for prompt in (None, 1, "", "   "):
                with self.subTest(prompt=prompt):
                    with self.assertRaisesRegex(ValueError, "non-empty string"):
                        generate_initial_output(prompt, client)
                    with self.assertRaises(ValueError):
                        generate_initial_output(prompt)
            factory.assert_not_called()
        client.generate.assert_not_called()

    def test_api_failure_is_sanitized_and_not_retried(self):
        client = Mock()
        client.generate.side_effect = RuntimeError("provider details: secret-key")
        with self.assertRaisesRegex(GenerationError, "generation failed") as caught:
            generate_initial_output("Prompt", client)
        self.assertNotIn("secret-key", str(caught.exception))
        client.generate.assert_called_once_with("Prompt")

    def test_empty_or_invalid_responses_are_rejected(self):
        for response in (None, [], {}, {"output": None}, {"output": ""},
                         {"output": "   "}, {"output": 123}):
            with self.subTest(response=response):
                client = Mock()
                client.generate.return_value = response
                with self.assertRaises(GenerationError):
                    generate_initial_output("Prompt", client)
                client.generate.assert_called_once_with("Prompt")

    def test_default_client_construction_failure_is_sanitized(self):
        with patch("tavf.generation.LLMClient", side_effect=ValueError("secret")):
            with self.assertRaisesRegex(GenerationError, "generation failed") as caught:
                generate_initial_output("Prompt")
        self.assertNotIn("secret", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
