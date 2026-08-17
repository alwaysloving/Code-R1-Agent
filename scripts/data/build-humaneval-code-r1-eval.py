#!/usr/bin/env python3
from __future__ import annotations

import gzip
import json
import re
from pathlib import Path
from typing import Any


SYSTEM_PROMPT = """You are a Python coding agent operating under a limited public-test budget.
You may run visible public tests or submit a final answer.

At each turn, output exactly one action:

<test>
```python
complete current candidate code
```
</test>

or:

<answer>
```python
complete final code
```
</answer>

Use <test> when public feedback is useful. After receiving <information> feedback, fix the code before testing or answering again.
Use <answer> only when submitting the final solution.
Output no extra text outside the XML action tags."""


DOCTEST_RE = re.compile(r"^\s*>>>\s*(.+?)\s*$\n\s*(.+?)\s*$", re.MULTILINE)


def read_jsonl_gz(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def build_public_test(prompt: str, entry_point: str) -> dict[str, Any] | None:
    assertions: list[str] = []
    for expr, expected in DOCTEST_RE.findall(prompt):
        if not expr.strip().startswith(entry_point + "("):
            continue
        assertions.append(f"    assert candidate{expr.strip()[len(entry_point):]} == {expected.strip()}")
    if not assertions:
        return None
    test_code = "def check(candidate):\n" + "\n".join(assertions) + "\n"
    return {"mode": "unit_test", "fn_name": entry_point, "test_code": test_code}


def user_prompt(item: dict[str, Any], num_public: int) -> str:
    task_id = item["task_id"]
    entry_point = item["entry_point"]
    prompt = item["prompt"].rstrip()
    return f"""Problem:
Complete the following Python function.

```python
{prompt}
```

Implement callable `{entry_point}`. The evaluator imports the code and calls the function directly.
Do not read stdin or print the return value.

Tool budget: 4. Public test count: {num_public}. Choose the first action."""


def convert(input_path: Path, output_path: Path) -> None:
    rows = []
    for item in read_jsonl_gz(input_path):
        entry_point = item["entry_point"]
        public = build_public_test(item["prompt"], entry_point)
        public_tests = {"tests": [public] if public else []}
        hidden_tests = {
            "tests": [
                {
                    "mode": "unit_test",
                    "fn_name": entry_point,
                    "test_code": item["test"],
                }
            ]
        }
        rows.append(
            {
                "prompt": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt(item, len(public_tests["tests"]))},
                ],
                "label": json.dumps(hidden_tests, ensure_ascii=False),
                "metadata": {
                    "id": item["task_id"],
                    "source": "openai_humaneval",
                    "difficulty": "humaneval",
                    "execution_protocol": "unit_test",
                    "fn_name": entry_point,
                    "public_tests": public_tests,
                    "num_public_tests": len(public_tests["tests"]),
                    "num_hidden_tests": 1,
                    "tool_budget": 4,
                    "canonical_solution": item.get("canonical_solution", ""),
                },
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows to {output_path}")


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    convert(root / "data/HumanEval.jsonl.gz", root / "data/humaneval_code_r1_eval.jsonl")


if __name__ == "__main__":
    main()
