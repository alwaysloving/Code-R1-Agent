from __future__ import annotations

import argparse
import ast
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any

from sandbox_runner import parse_tests, run_tests


ACTION_RE = re.compile(r"<(test|answer)>\s*```(?:python|py)?\s*(.*?)```\s*</\1>", re.DOTALL | re.IGNORECASE)
DANGEROUS_RE = re.compile(
    r"\b(import\s+subprocess|from\s+subprocess\s+import|import\s+socket|from\s+socket\s+import|"
    r"import\s+requests|from\s+requests\s+import|eval\s*\(|exec\s*\(|__import__\s*\(|open\s*\()"
)
PSEUDO_EASY_RE = re.compile(
    r"\b(graph|tree|dynamic programming|dp\b|dijkstra|bfs|dfs|topological|segment tree|fenwick|"
    r"binary search|interpolation search|cycle sort|quick sort|merge sort|heap|trie|regex|regular expression|"
    r"parser|parse|matrix|subsequence|permutation|combin|knapsack|backtracking|recursion|"
    r"leetcode|codeforces|taco|apps|competitive)\b",
    re.IGNORECASE,
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def user_prompt(row: dict[str, Any]) -> str:
    prompt = row.get("prompt") or []
    return next((str(m.get("content", "")) for m in prompt if m.get("role") == "user"), "")


def label_tests(row: dict[str, Any]) -> list[Any]:
    return parse_tests(row.get("label"))


def public_tests(row: dict[str, Any]) -> list[Any]:
    return parse_tests((row.get("metadata") or {}).get("public_tests"))


def solution_defines_fn(solution: str, fn_name: str) -> bool:
    try:
        tree = ast.parse(solution)
    except SyntaxError:
        return False
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == fn_name:
            return True
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == fn_name:
                    return True
    return False


def validate_prompt_rows(name: str, rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    counters = Counter()
    failures: list[dict[str, Any]] = []
    lengths = []
    code_lengths = []

    rng = random.Random(args.seed + abs(hash(name)) % 10000)
    if args.run_solutions and args.sample_solutions > 0 and args.sample_solutions < len(rows):
        solution_check_indices = set(rng.sample(range(len(rows)), args.sample_solutions))
    elif args.run_solutions:
        solution_check_indices = set(range(len(rows)))
    else:
        solution_check_indices = set()

    for idx, row in enumerate(rows):
        md = row.get("metadata") or {}
        fn_name = str(md.get("fn_name") or "")
        solution = str(md.get("solution") or "")
        prompt_text = user_prompt(row)
        lengths.append(len(prompt_text))
        code_lengths.append(len(solution))

        if row.get("prompt") is None or row.get("label") is None:
            counters["missing_prompt_or_label"] += 1
        if md.get("execution_protocol") != "call_based":
            counters["bad_protocol"] += 1
        if int(md.get("num_public_tests") or 0) < args.min_public_tests:
            counters["too_few_public_tests"] += 1
        if int(md.get("num_hidden_tests") or 0) < args.min_hidden_tests:
            counters["too_few_hidden_tests"] += 1
        if len(prompt_text) > args.max_prompt_chars:
            counters["prompt_too_long"] += 1
        if len(solution) > args.max_solution_chars:
            counters["solution_too_long"] += 1
        if DANGEROUS_RE.search(solution):
            counters["dangerous_solution"] += 1
        if not solution_defines_fn(solution, fn_name):
            counters["missing_function_definition"] += 1

        if idx in solution_check_indices:
            result = run_tests(solution, public_tests(row) + label_tests(row), timeout=args.test_timeout)
            if result.status != "passed":
                counters["solution_test_failed"] += 1
                if len(failures) < args.max_failure_examples:
                    failures.append(
                        {
                            "split": name,
                            "row": idx,
                            "id": md.get("id"),
                            "fn_name": fn_name,
                            "difficulty": md.get("difficulty"),
                            "status": result.status,
                            "detail": result.detail,
                            "stderr": result.stderr[:500],
                            "failed_input": result.failed_input,
                            "expected": result.expected,
                            "got": result.got,
                        }
                    )

    return {
        "rows": len(rows),
        "difficulty": dict(Counter((row.get("metadata") or {}).get("difficulty") for row in rows)),
        "counters": dict(counters),
        "prompt_chars": summarize(lengths),
        "solution_chars": summarize(code_lengths),
        "solution_checked": len(solution_check_indices),
        "failure_examples": failures,
    }


def validate_sft(rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    counters = Counter()
    shapes = Counter()
    examples = []
    for idx, row in enumerate(rows):
        messages = row.get("messages") or []
        assistant = "\n".join(str(m.get("content", "")) for m in messages if m.get("role") == "assistant")
        user = "\n".join(str(m.get("content", "")) for m in messages if m.get("role") == "user")
        actions = ACTION_RE.findall(assistant)
        n_test = sum(1 for action, _ in actions if action.lower() == "test")
        n_answer = sum(1 for action, _ in actions if action.lower() == "answer")
        n_info = len(re.findall(r"<information>", user, re.IGNORECASE))
        shapes[(n_test, n_answer, n_info)] += 1
        if n_answer != 1 or n_info != n_test:
            counters["bad_action_shape"] += 1
        if "<tool_call>" in assistant or "<tool_result>" in user:
            counters["old_tool_protocol"] += 1
        if len(assistant) > args.max_sft_assistant_chars:
            counters["assistant_too_long"] += 1
        if counters and len(examples) < args.max_failure_examples:
            examples.append({"row": idx, "shape": [n_test, n_answer, n_info], "assistant_preview": assistant[:500]})
    return {"rows": len(rows), "shapes": {str(k): v for k, v in shapes.items()}, "counters": dict(counters), "examples": examples}


def summarize(values: list[int]) -> dict[str, int | float]:
    if not values:
        return {}
    values = sorted(values)
    return {
        "min": values[0],
        "p50": values[len(values) // 2],
        "p90": values[int(0.9 * (len(values) - 1))],
        "max": values[-1],
    }


def overlap_report(named_rows: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    ids = {
        name: {(row.get("metadata") or {}).get("id") for row in rows}
        for name, rows in named_rows.items()
    }
    report = {}
    names = list(ids)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            report[f"{a}__{b}"] = len(ids[a] & ids[b])
    return report


def easy_audit(rows_by_split: dict[str, list[dict[str, Any]]], sample_size: int, seed: int) -> list[dict[str, Any]]:
    easy_rows = []
    for split, rows in rows_by_split.items():
        for idx, row in enumerate(rows):
            md = row.get("metadata") or {}
            if md.get("difficulty") == "easy":
                easy_rows.append((split, idx, row))
    rng = random.Random(seed)
    sample = rng.sample(easy_rows, min(sample_size, len(easy_rows)))
    audit = []
    for split, idx, row in sample:
        md = row.get("metadata") or {}
        prompt = user_prompt(row)
        solution = str(md.get("solution") or "")
        flags = []
        if PSEUDO_EASY_RE.search(prompt):
            flags.append("keyword_complexity")
        if len(prompt) > 2500:
            flags.append("long_prompt")
        if len(solution) > 2500:
            flags.append("long_solution")
        if int(md.get("num_hidden_tests") or 0) < 3:
            flags.append("few_hidden_tests")
        audit.append(
            {
                "split": split,
                "row": idx,
                "id": md.get("id"),
                "fn_name": md.get("fn_name"),
                "subset": md.get("subset"),
                "prompt_chars": len(prompt),
                "solution_chars": len(solution),
                "public_tests": md.get("num_public_tests"),
                "hidden_tests": md.get("num_hidden_tests"),
                "flags": flags,
                "question": prompt.split("Public test index 0")[0].strip(),
            }
        )
    return audit


def write_easy_audit_markdown(path: Path, audit: list[dict[str, Any]]) -> None:
    parts = ["# KodCode Easy Manual Audit Sample\n\n", f"Total sampled: {len(audit)}\n\n"]
    flagged = sum(1 for item in audit if item["flags"])
    parts.append(f"Flagged by heuristic: {flagged}\n\n")
    for i, item in enumerate(audit, 1):
        parts.append(
            f"## {i:02d}. {item['id']} `{item['fn_name']}` split={item['split']} subset={item['subset']}\n\n"
        )
        parts.append(
            f"- prompt_chars: {item['prompt_chars']}\n"
            f"- solution_chars: {item['solution_chars']}\n"
            f"- tests: public={item['public_tests']} hidden={item['hidden_tests']}\n"
            f"- flags: {item['flags'] or ['looks_easy']}\n\n"
        )
        question = item["question"]
        if len(question) > 1600:
            question = question[:1600] + f"\n...(truncated {len(item['question']) - 1600} chars)"
        parts.append("```text\n" + question + "\n```\n\n")
    path.write_text("".join(parts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--sft-prompts", default="kodcode_code_r1_sft_prompts.jsonl")
    parser.add_argument("--grpo", default="kodcode_code_r1_grpo_631.jsonl")
    parser.add_argument("--eval", default="kodcode_code_r1_eval_631.jsonl")
    parser.add_argument("--sft", default="kodcode_code_r1_sft.jsonl")
    parser.add_argument("--report-output", default="data/kodcode_code_r1_validation_report_631.json")
    parser.add_argument("--easy-audit-output", default="data/kodcode_code_r1_easy_audit_631_50.md")
    parser.add_argument("--easy-audit-size", type=int, default=50)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--run-solutions", action="store_true")
    parser.add_argument("--sample-solutions", type=int, default=0, help="If >0, check this many solutions per split.")
    parser.add_argument("--test-timeout", type=float, default=1.0)
    parser.add_argument("--min-public-tests", type=int, default=2)
    parser.add_argument("--min-hidden-tests", type=int, default=2)
    parser.add_argument("--max-prompt-chars", type=int, default=6000)
    parser.add_argument("--max-solution-chars", type=int, default=6000)
    parser.add_argument("--max-sft-assistant-chars", type=int, default=12000)
    parser.add_argument("--max-failure-examples", type=int, default=20)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    prompt_rows = {
        "sft_prompts": load_jsonl(data_dir / args.sft_prompts),
        "grpo": load_jsonl(data_dir / args.grpo),
        "eval": load_jsonl(data_dir / args.eval),
    }
    sft_rows = load_jsonl(data_dir / args.sft)

    report = {
        "prompt_splits": {
            name: validate_prompt_rows(name, rows, args)
            for name, rows in prompt_rows.items()
        },
        "sft": validate_sft(sft_rows, args),
        "overlap": overlap_report(prompt_rows),
    }
    audit = easy_audit(prompt_rows, args.easy_audit_size, args.seed)
    report["easy_audit"] = {
        "sample_size": len(audit),
        "flagged": sum(1 for item in audit if item["flags"]),
        "flag_counts": dict(Counter(flag for item in audit for flag in item["flags"])),
        "items": audit,
    }

    Path(args.report_output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_easy_audit_markdown(Path(args.easy_audit_output), audit)
    print(json.dumps({k: v for k, v in report.items() if k != "easy_audit"}, ensure_ascii=False, indent=2))
    print(f"wrote report: {args.report_output}")
    print(f"wrote easy audit: {args.easy_audit_output}")


if __name__ == "__main__":
    main()
