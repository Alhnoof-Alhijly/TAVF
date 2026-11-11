
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INPUT_PRICE = Decimal("0.75")
OUTPUT_PRICE = Decimal("4.50")
CACHED_INPUT_PRICE = Decimal("0.075")

BUDGET = Decimal("2.00")
SAFETY_LIMIT = Decimal("1.50")

RESULT_FILES = [
    ROOT / "results/pilot/pilot_outputs.json",
    ROOT / "results/baseline/baseline_outputs.json",
]


def calculate_cost(input_tokens, output_tokens, cached_tokens=0):
    input_tokens = int(input_tokens)
    output_tokens = int(output_tokens)
    cached_tokens = int(cached_tokens)

    if not 0 <= cached_tokens <= input_tokens:
        raise ValueError("Invalid cached token count.")

    regular_tokens = input_tokens - cached_tokens

    return (
        Decimal(regular_tokens) * INPUT_PRICE
        + Decimal(cached_tokens) * CACHED_INPUT_PRICE
        + Decimal(output_tokens) * OUTPUT_PRICE
    ) / Decimal("1000000")


def calculate_spent():
    total = Decimal("0")
    seen_responses = set()

    for path in RESULT_FILES:
        if not path.exists():
            continue

        records = json.loads(path.read_text(encoding="utf-8"))

        for record in records:
            response_id = record.get("response_id")

            if response_id and response_id in seen_responses:
                continue

            if response_id:
                seen_responses.add(response_id)

            input_tokens = record.get("input_tokens")
            output_tokens = record.get("output_tokens")

            if input_tokens is None or output_tokens is None:
                raise ValueError(
                    f"Missing token usage in {path.name}"
                )

            total += calculate_cost(
                input_tokens,
                output_tokens,
                record.get("cached_input_tokens", 0),
            )

    return total


def check_budget(estimated_input_tokens, max_output_tokens):
    spent = calculate_spent()

    estimated_cost = calculate_cost(
        estimated_input_tokens,
        max_output_tokens,
    )

    projected_total = spent + estimated_cost

    print(f"Recorded spending: ${spent:.4f}")
    print(f"Estimated next request: ${estimated_cost:.4f}")
    print(f"Projected total: ${projected_total:.4f}")
    print(f"Safety limit: ${SAFETY_LIMIT:.2f}")

    if projected_total > SAFETY_LIMIT:
        print("STOP: Safety limit would be exceeded.")
        return False

    print("Budget check passed.")
    return True


if __name__ == "__main__":
    # Local demonstration only: no API requests.
    check_budget(
        estimated_input_tokens=2000,
        max_output_tokens=8192,
    )
