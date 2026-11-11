
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from utils.llm_client import LLMClient


class TestLLMClient(unittest.TestCase):

    def test_successful_generation(self):
        calls = []

        class FakeResponses:
            def create(self, **kwargs):
                calls.append(kwargs)

                return SimpleNamespace(
                    id="fake-response-001",
                    output_text="Simulated model response",
                    usage=SimpleNamespace(
                        input_tokens=100,
                        output_tokens=50,
                        input_tokens_details=SimpleNamespace(
                            cached_tokens=20
                        ),
                    ),
                )

        fake_client = SimpleNamespace(
            responses=FakeResponses()
        )

        client = LLMClient(
            model="fake-test-model",
            client=fake_client,
        )

        result = client.generate("Test prompt")

        self.assertEqual(
            result["output"],
            "Simulated model response",
        )
        self.assertEqual(result["input_tokens"], 100)
        self.assertEqual(result["output_tokens"], 50)
        self.assertEqual(result["cached_input_tokens"], 20)
        self.assertEqual(result["model"], "fake-test-model")

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["input"], "Test prompt")
        self.assertEqual(
            calls[0]["reasoning"],
            {"effort": "none"},
        )
        self.assertEqual(
            calls[0]["max_output_tokens"],
            8192,
        )

    def test_empty_prompt_is_rejected(self):
        fake_client = SimpleNamespace(
            responses=SimpleNamespace()
        )

        client = LLMClient(client=fake_client)

        with self.assertRaises(ValueError):
            client.generate("")

    def test_empty_response_is_rejected(self):
        fake_client = SimpleNamespace(
            responses=SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(
                    id="fake-response-002",
                    output_text="",
                    usage=None,
                )
            )
        )

        client = LLMClient(client=fake_client)

        with self.assertRaisesRegex(
            ValueError,
            "empty output",
        ):
            client.generate("Test prompt")


if __name__ == "__main__":
    unittest.main()
