from __future__ import annotations

import argparse
import ast
import json
import random
import re
from pathlib import Path
from typing import Any

from sandbox_runner import parse_tests, run_tests


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


DIFFICULTY_QUOTAS = {
    "easy": 0.90,
    "medium": 0.09,
    "hard": 0.01,
}

DANGEROUS_RE = re.compile(
    r"\b(import\s+subprocess|from\s+subprocess\s+import|import\s+socket|from\s+socket\s+import|"
    r"import\s+requests|from\s+requests\s+import|eval\s*\(|exec\s*\(|__import__\s*\(|open\s*\()"
)


class UnsupportedTest(ValueError):
    pass


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def function_info(row: dict[str, Any]) -> dict[str, str] | None:
    infos = row.get("test_info") or []
    if not infos:
        return None
    info = infos[0] or {}
    fn_name = str(info.get("function_name") or "").strip()
    declaration = str(info.get("function_declaration") or "").strip()
    if not fn_name or not declaration.startswith("def "):
        return None
    return {
        "function_name": fn_name,
        "function_declaration": declaration,
        "docstring": str(info.get("docstring") or "").strip(),
        "parameter_list": str(info.get("parameter_list") or "").strip(),
    }


def safe_eval_expr(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [safe_eval_expr(item) for item in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(safe_eval_expr(item) for item in node.elts)
    if isinstance(node, ast.Set):
        return {safe_eval_expr(item) for item in node.elts}
    if isinstance(node, ast.Dict):
        return {safe_eval_expr(k): safe_eval_expr(v) for k, v in zip(node.keys, node.values, strict=False)}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        value = safe_eval_expr(node.operand)
        if isinstance(value, (int, float)):
            return -value
    if isinstance(node, ast.BinOp):
        left = safe_eval_expr(node.left)
        right = safe_eval_expr(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Mult):
            if isinstance(left, int) or isinstance(right, int):
                return left * right
    raise UnsupportedTest(f"unsupported expression: {ast.unparse(node)}")


def jsonable(value: Any) -> Any:
    if isinstance(value, complex):
        raise UnsupportedTest("complex values are not supported")
    if isinstance(value, tuple):
        return {"__apps_type__": "tuple", "items": [jsonable(item) for item in value]}
    if isinstance(value, set):
        return {"__apps_type__": "set", "items": [jsonable(item) for item in value]}
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {
            "__apps_type__": "dict",
            "items": [[jsonable(key), jsonable(item)] for key, item in value.items()],
        }
    return value


def extract_call(node: ast.AST, fn_name: str) -> list[Any]:
    if not isinstance(node, ast.Call):
        raise UnsupportedTest("assertion side is not a call")
    if not isinstance(node.func, ast.Name) or node.func.id != fn_name:
        raise UnsupportedTest("call does not target expected function")
    if node.keywords:
        raise UnsupportedTest("keyword arguments are not supported")
    return [jsonable(safe_eval_expr(arg)) for arg in node.args]


def parse_assert_test(assertion: ast.Assert, fn_name: str) -> dict[str, Any]:
    expr = assertion.test
    if not isinstance(expr, ast.Compare) or len(expr.ops) != 1 or len(expr.comparators) != 1:
        raise UnsupportedTest("only simple compare assertions are supported")
    left = expr.left
    right = expr.comparators[0]
    op = expr.ops[0]

    if isinstance(op, ast.Eq):
        try:
            args = extract_call(left, fn_name)
            expected = jsonable(safe_eval_expr(right))
        except UnsupportedTest:
            args = extract_call(right, fn_name)
            expected = jsonable(safe_eval_expr(left))
        return {"mode": "call_based", "fn_name": fn_name, "args": args, "expected": expected}

    if isinstance(op, ast.In):
        args = extract_call(left, fn_name)
        expected = safe_eval_expr(right)
        if not isinstance(expected, (list, tuple, set)):
            raise UnsupportedTest("membership target must be a literal collection")
        return {
            "mode": "call_based",
            "fn_name": fn_name,
            "args": args,
            "expected": {"__any_of__": [jsonable(item) for item in expected]},
        }

    raise UnsupportedTest(f"unsupported compare operator: {type(op).__name__}")


def extract_tests(test_code: str, fn_name: str) -> list[dict[str, Any]]:
    tree = ast.parse(test_code or "")
    tests: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            try:
                tests.append(parse_assert_test(node, fn_name))
            except UnsupportedTest:
                continue
    return tests


def is_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, ensure_ascii=False)
        return True
    except TypeError:
        return False


def canonical_solution(row: dict[str, Any], fn_name: str) -> str:
    candidates = [str(row.get("solution") or "").strip(), str(row.get("r1_solution") or "").strip()]
    for candidate in candidates:
        if re.search(rf"\bdef\s+{re.escape(fn_name)}\s*\(", candidate):
            return candidate
    return candidates[0]


def make_prompt(row: dict[str, Any], info: dict[str, str], public_tests: list[dict[str, Any]]) -> list[dict[str, str]]:
    lines = [
        "Problem:",
        str(row.get("question") or "").strip(),
        "",
        f"Implement callable `{info['function_name']}`.",
        f"Function declaration: `{info['function_declaration']}`",
    ]
    if info.get("docstring"):
        lines.extend(["", "Docstring:", info["docstring"]])
    lines.append("")
    for idx, test in enumerate(public_tests):
        expected = test["expected"]
        if isinstance(expected, dict) and "__any_of__" in expected:
            expected_text = f"one of {expected['__any_of__']!r}"
        else:
            expected_text = repr(expected)
        lines.extend(
            [
                f"Public test index {idx}",
                f"Function: {test['fn_name']}",
                f"Arguments: {test['args']!r}",
                f"Expected return: {expected_text}",
                "",
            ]
        )
    lines.extend(
        [
            "The evaluator imports the code and calls the function directly with structured arguments.",
            "Do not read stdin or print the return value.",
            f"Tool budget: 4. Public test indices: 0..{len(public_tests) - 1}. Choose the first action.",
        ]
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "\n".join(lines).strip()},
    ]


def convert_row(
    row: dict[str, Any],
    min_tests: int,
    public_tests: int,
    timeout: float,
    *,
    validate_solution: bool = True,
) -> dict[str, Any] | None:
    info = function_info(row)
    if not info:
        return None
    fn_name = info["function_name"]
    tests = extract_tests(str(row.get("test") or ""), fn_name)
    tests = [test for test in tests if is_json_serializable(test)]
    if len(tests) < min_tests:
        return None
    solution = canonical_solution(row, fn_name)
    if not solution:
        return None
    if DANGEROUS_RE.search(solution):
        return None
    if validate_solution and run_tests(solution, parse_tests({"tests": tests}), timeout=timeout).status != "passed":
        return None

    n_public = max(1, min(public_tests, len(tests) - 1))
    visible = tests[:n_public]
    hidden = tests[n_public:]
    if not hidden:
        return None
    difficulty = str(row.get("gpt_difficulty") or "unknown")
    return {
        "prompt": make_prompt(row, info, visible),
        "label": json.dumps({"tests": hidden}, ensure_ascii=False),
        "metadata": {
            "id": row.get("question_id"),
            "source": "kodcode_light_rl_10k",
            "difficulty": difficulty,
            "subset": row.get("subset"),
            "style": row.get("style"),
            "execution_protocol": "call_based",
            "fn_name": fn_name,
            "public_tests": {"tests": visible},
            "num_public_tests": len(visible),
            "num_hidden_tests": len(hidden),
            "num_available_tests": len(tests),
            "tool_budget": 4,
            "allowed_tools": ["public_tests"],
            "gpt_pass_percentage": row.get("gpt_pass_percentage"),
            "r1_correctness": row.get("r1_correctness"),
            "solution": solution,
            "raw_metadata": row.get("metadata"),
        },
    }


def take_by_ratio(rows: list[dict[str, Any]], total: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    by_diff: dict[str, list[dict[str, Any]]] = {"easy": [], "medium": [], "hard": []}
    for row in rows:
        diff = str((row.get("metadata") or {}).get("difficulty") or "")
        if diff in by_diff:
            by_diff[diff].append(row)
    for items in by_diff.values():
        rng.shuffle(items)

    selected: list[dict[str, Any]] = []
    used_ids: set[Any] = set()
    for diff, ratio in DIFFICULTY_QUOTAS.items():
        quota = int(round(total * ratio))
        for row in by_diff[diff][:quota]:
            selected.append(row)
            used_ids.add((row.get("metadata") or {}).get("id"))
    if len(selected) < total:
        leftovers = [
            row
            for diff in ("easy", "medium", "hard")
            for row in by_diff[diff]
            if (row.get("metadata") or {}).get("id") not in used_ids
        ]
        selected.extend(leftovers[: total - len(selected)])
    rng.shuffle(selected)
    return selected[:total]


def target_counts(total: int) -> dict[str, int]:
    counts = {diff: int(total * ratio) for diff, ratio in DIFFICULTY_QUOTAS.items()}
    remaining = total - sum(counts.values())
    for diff in ("easy", "medium", "hard"):
        if remaining <= 0:
            break
        counts[diff] += 1
        remaining -= 1
    return counts


def make_sft_rows(rows: list[dict[str, Any]], direct_answer_percent: int) -> list[dict[str, Any]]:
    result = []
    for idx, row in enumerate(rows):
        messages = list(row["prompt"])
        code = (row.get("metadata") or {}).get("solution") or ""
        use_direct = idx % 100 < direct_answer_percent
        if not use_direct:
            messages.append({"role": "assistant", "content": _action("test", code)})
            messages.append(
                {
                    "role": "user",
                    "content": '<information>{"status":"passed","passed":'
                    + str((row.get("metadata") or {}).get("num_public_tests", 0))
                    + ',"total":'
                    + str((row.get("metadata") or {}).get("num_public_tests", 0))
                    + "}</information>",
                }
            )
        messages.append({"role": "assistant", "content": _action("answer", code)})
        result.append({"messages": messages})
    return result


def _action(action: str, code: str) -> str:
    return f"<{action}>\n```python\n{code.rstrip()}\n```\n</{action}>"


def describe(name: str, rows: list[dict[str, Any]]) -> None:
    from collections import Counter

    diffs = Counter((row.get("metadata") or {}).get("difficulty") for row in rows)
    subsets = Counter((row.get("metadata") or {}).get("subset") for row in rows)
    print(f"{name}: {len(rows)} rows difficulty={dict(diffs)}")
    print(f"  top subsets={subsets.most_common(8)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/kodcode_light_rl_10k_raw.jsonl")
    parser.add_argument("--sft-prompt-output", default="data/kodcode_code_r1_sft_prompts.jsonl")
    parser.add_argument("--grpo-output", default="data/kodcode_code_r1_grpo_631.jsonl")
    parser.add_argument("--eval-output", default="data/kodcode_code_r1_eval_631.jsonl")
    parser.add_argument("--sft-output", default="data/kodcode_code_r1_sft.jsonl")
    parser.add_argument("--sft-size", type=int, default=3000)
    parser.add_argument("--grpo-size", type=int, default=2400)
    parser.add_argument("--eval-size", type=int, default=500)
    parser.add_argument("--min-tests", type=int, default=4)
    parser.add_argument("--public-tests", type=int, default=2)
    parser.add_argument("--direct-answer-percent", type=int, default=60)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test-timeout", type=float, default=2.0)
    parser.add_argument("--skip-solution-validation", action="store_true")
    args = parser.parse_args()

    raw_rows = load_jsonl(Path(args.input))
    rng = random.Random(args.seed)
    rng.shuffle(raw_rows)

    total_needed = args.sft_size + args.grpo_size + args.eval_size
    converted_rows: list[dict[str, Any]] = []
    scanned = 0
    for raw in raw_rows:
        scanned += 1
        row = convert_row(
            raw,
            args.min_tests,
            args.public_tests,
            args.test_timeout,
            validate_solution=not args.skip_solution_validation,
        )
        if row is None:
            continue
        converted_rows.append(row)

    selected = take_by_ratio(converted_rows, min(total_needed, len(converted_rows)), args.seed)

    eval_rows = take_by_ratio(selected, args.eval_size, args.seed + 1)
    eval_ids = {(row.get("metadata") or {}).get("id") for row in eval_rows}
    remaining = [row for row in selected if (row.get("metadata") or {}).get("id") not in eval_ids]

    sft_prompt_rows = take_by_ratio(remaining, args.sft_size, args.seed + 2)
    sft_ids = {(row.get("metadata") or {}).get("id") for row in sft_prompt_rows}
    grpo_pool = [row for row in remaining if (row.get("metadata") or {}).get("id") not in sft_ids]
    grpo_rows = take_by_ratio(grpo_pool, args.grpo_size, args.seed + 3)
    sft_rows = make_sft_rows(sft_prompt_rows, args.direct_answer_percent)

    write_jsonl(Path(args.sft_prompt_output), sft_prompt_rows)
    write_jsonl(Path(args.grpo_output), grpo_rows)
    write_jsonl(Path(args.eval_output), eval_rows)
    write_jsonl(Path(args.sft_output), sft_rows)

    from collections import Counter

    converted_counts = Counter((row.get("metadata") or {}).get("difficulty") for row in converted_rows)
    selected_counts = Counter((row.get("metadata") or {}).get("difficulty") for row in selected)
    print(f"raw={len(raw_rows)} scanned={scanned} converted={len(converted_rows)} selected={len(selected)}")
    print(f"converted_counts={dict(converted_counts)} selected_counts={dict(selected_counts)}")
    describe(args.sft_prompt_output, sft_prompt_rows)
    describe(args.grpo_output, grpo_rows)
    describe(args.eval_output, eval_rows)
    print(f"{args.sft_output}: {len(sft_rows)} rows")


if __name__ == "__main__":
    main()
