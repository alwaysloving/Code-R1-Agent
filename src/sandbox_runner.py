from __future__ import annotations

import ast
import json
import math
import os
import pickle
import platform
import re
import resource
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


PYTHON_BLOCK_RE = re.compile(r"```(?:python|py)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)

DANGEROUS_PATTERNS = [
    r"\bimport\s+subprocess\b",
    r"\bfrom\s+subprocess\s+import\b",
    r"\bimport\s+socket\b",
    r"\bfrom\s+socket\s+import\b",
    r"\bimport\s+requests\b",
    r"\bfrom\s+requests\s+import\b",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"__import__\s*\(",
    r"\bopen\s*\(",
]

SANDBOX_ENV = {
    "PYTHONIOENCODING": "utf-8",
    "PATH": os.environ.get("PATH", ""),
    "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH", ""),
    "OPENBLAS_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "BLIS_NUM_THREADS": "1",
}


@dataclass
class TestCase:
    mode: str
    input: str = ""
    output: str = ""
    fn_name: str = ""
    args: list[Any] | None = None
    expected: Any = None
    test_code: str = ""


@dataclass
class RunResult:
    score: float
    status: str
    protocol: str = ""
    function: str = ""
    passed: int = 0
    total: int = 0
    detail: str = ""
    failed_input: str = ""
    expected: str = ""
    got: str = ""
    stderr: str = ""


def extract_code(text: str) -> tuple[str, str]:
    if not text:
        return "", "empty"
    matches = PYTHON_BLOCK_RE.findall(text)
    if matches:
        return matches[-1].strip(), "fenced_code"
    stripped = text.strip()
    return (stripped, "plain_code") if stripped else ("", "empty")


def parse_tests(raw: Any) -> list[TestCase]:
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = json.loads(raw)
    if isinstance(raw, dict) and "input_output" in raw:
        raw = raw["input_output"]
    if isinstance(raw, dict) and isinstance(raw.get("input_output"), str):
        raw = json.loads(raw["input_output"])
    if isinstance(raw, dict) and "tests" in raw:
        return parse_tests(raw["tests"])
    if isinstance(raw, dict):
        inputs = raw.get("inputs") or []
        outputs = raw.get("outputs") or []
        return [
            TestCase(mode="stdio", input=_normalize_stdio(i), output=_normalize_stdio(o))
            for i, o in zip(inputs, outputs, strict=False)
        ]
    if isinstance(raw, list):
        tests = []
        for item in raw:
            if isinstance(item, dict):
                mode = item.get("mode", "stdio")
                if mode == "call_based":
                    tests.append(
                        TestCase(
                            mode=mode,
                            fn_name=str(item.get("fn_name", "")),
                            args=_decode_protocol_value(item.get("args"))
                            if isinstance(item.get("args"), list)
                            else [_decode_protocol_value(item.get("args"))],
                            expected=_decode_protocol_value(item.get("expected")),
                        )
                    )
                elif mode == "unit_test":
                    tests.append(
                        TestCase(
                            mode=mode,
                            fn_name=str(item.get("fn_name", "")),
                            test_code=str(item.get("test_code", "")),
                        )
                    )
                else:
                    tests.append(
                        TestCase(
                            mode="stdio",
                            input=_normalize_stdio(item.get("input", "")),
                            output=_normalize_stdio(item.get("output", "")),
                        )
                    )
        return tests
    return []


def _normalize_stdio(value: Any) -> str:
    if isinstance(value, list):
        text = "\n".join(str(item) for item in value)
    else:
        text = str(value)
    return text if text.endswith("\n") else text + "\n"


def _decode_protocol_value(value: Any) -> Any:
    if isinstance(value, list):
        return [_decode_protocol_value(item) for item in value]
    if isinstance(value, dict):
        value_type = value.get("__apps_type__")
        if value_type == "int":
            return int(value["value"])
        if value_type == "set":
            return {_decode_protocol_value(item) for item in value.get("items", [])}
        if value_type == "tuple":
            return tuple(_decode_protocol_value(item) for item in value.get("items", []))
        if value_type == "dict":
            return {
                _decode_protocol_value(key): _decode_protocol_value(item)
                for key, item in value.get("items", [])
            }
        return {key: _decode_protocol_value(item) for key, item in value.items()}
    return value


def run_tests_from_response(response: str, raw_tests: Any, timeout: float = 3.0) -> RunResult:
    code, extraction_status = extract_code(response)
    result = run_tests(code, parse_tests(raw_tests), timeout=timeout)
    if extraction_status == "fenced_code" and result.score > 0:
        result.score = min(1.0, result.score + 0.02)
    result.detail = f"{extraction_status} {result.detail}".strip()
    return result


def run_tests(code: str, tests: list[TestCase], timeout: float = 3.0) -> RunResult:
    protocol = tests[0].mode if tests else ""
    function = tests[0].fn_name if tests and protocol == "call_based" else ""
    if not code.strip():
        return RunResult(
            score=-0.2,
            status="format_error",
            protocol=protocol,
            function=function,
            total=len(tests),
            detail="empty code",
        )
    if _contains_dangerous_code(code):
        return RunResult(
            score=-0.4,
            status="dangerous_code",
            protocol=protocol,
            function=function,
            total=len(tests),
        )
    try:
        ast.parse(code)
    except (SyntaxError, ValueError) as exc:
        return RunResult(
            score=-0.2,
            status="compile_error",
            protocol=protocol,
            function=function,
            total=len(tests),
            detail=str(exc),
            stderr=str(exc),
        )
    if not tests:
        return RunResult(score=0.0, status="no_tests", total=0)

    passed = 0
    first_failure: RunResult | None = None
    with tempfile.TemporaryDirectory(prefix="apps_agent_") as tmpdir:
        path = Path(tmpdir) / "candidate.py"
        path.write_text(code, encoding="utf-8")
        for test in tests:
            if test.mode == "call_based":
                result = _run_call_test(path, test, tmpdir, timeout)
                if result.status == "passed":
                    passed += 1
                else:
                    first_failure = first_failure or result
                continue
            if test.mode == "unit_test":
                result = _run_unit_test(path, test, tmpdir, timeout)
                if result.status == "passed":
                    passed += 1
                else:
                    first_failure = first_failure or result
                continue

            try:
                proc = subprocess.run(
                    [sys.executable, str(path)],
                    input=test.input,
                    cwd=tmpdir,
                    text=True,
                    capture_output=True,
                    timeout=timeout,
                    env=SANDBOX_ENV,
                    preexec_fn=_limit_child_process if platform.system() == "Linux" else None,
                )
            except subprocess.TimeoutExpired:
                fail = RunResult(
                    score=0.0,
                    status="timeout",
                    protocol="stdio",
                    passed=passed,
                    total=len(tests),
                    failed_input=_shorten(test.input),
                    expected=_shorten(test.output),
                    got="",
                    stderr="timeout",
                )
                first_failure = first_failure or fail
                continue

            got = proc.stdout
            if proc.returncode == 0 and _normalize_output(got) == _normalize_output(test.output):
                passed += 1
                continue

            fail = RunResult(
                score=0.0,
                status="runtime_error" if proc.returncode != 0 else "wrong_answer",
                protocol="stdio",
                passed=passed,
                total=len(tests),
                failed_input=_shorten(test.input),
                expected=_shorten(test.output),
                got=_shorten(got),
                stderr=_shorten(proc.stderr),
            )
            first_failure = first_failure or fail

    pass_rate = passed / max(len(tests), 1)
    if passed == len(tests):
        return RunResult(
            score=1.0,
            status="passed",
            protocol=protocol,
            function=function,
            passed=passed,
            total=len(tests),
        )
    if first_failure is None:
        first_failure = RunResult(score=0.0, status="wrong_answer", total=len(tests))
    first_failure.passed = passed
    first_failure.total = len(tests)
    first_failure.score = 0.2 + 0.6 * pass_rate if passed > 0 else 0.0
    return first_failure


def _run_unit_test(path: Path, test: TestCase, tmpdir: str, timeout: float) -> RunResult:
    harness_path = Path(tmpdir) / "unit_harness.py"
    test_path = Path(tmpdir) / "unit_test.py"
    test_path.write_text(test.test_code, encoding="utf-8")
    harness_path.write_text(
        """
import importlib.util
import sys
import traceback

candidate_path, test_path, fn_name = sys.argv[1:]

candidate_spec = importlib.util.spec_from_file_location("candidate", candidate_path)
candidate_module = importlib.util.module_from_spec(candidate_spec)
candidate_spec.loader.exec_module(candidate_module)

test_spec = importlib.util.spec_from_file_location("unit_test", test_path)
test_module = importlib.util.module_from_spec(test_spec)
test_spec.loader.exec_module(test_module)

target = getattr(candidate_module, fn_name, None)
if not callable(target):
    raise AttributeError(f"Expected a module-level function named {fn_name!r}")

check = getattr(test_module, "check", None)
if not callable(check):
    raise AttributeError("Expected unit test code to define callable check(candidate)")

try:
    check(target)
except Exception:
    traceback.print_exc()
    raise
""".strip()
        + "\n",
        encoding="utf-8",
    )
    try:
        proc = subprocess.run(
            [sys.executable, str(harness_path), str(path), str(test_path), test.fn_name],
            cwd=tmpdir,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=SANDBOX_ENV,
            preexec_fn=_limit_child_process if platform.system() == "Linux" else None,
        )
    except subprocess.TimeoutExpired:
        return RunResult(
            score=0.0,
            status="timeout",
            protocol="unit_test",
            function=test.fn_name,
            stderr="timeout",
        )

    if proc.returncode == 0:
        return RunResult(
            score=1.0,
            status="passed",
            protocol="unit_test",
            function=test.fn_name,
            passed=1,
            total=1,
        )
    return RunResult(
        score=0.0,
        status="runtime_error" if "AssertionError" not in proc.stderr else "wrong_answer",
        protocol="unit_test",
        function=test.fn_name,
        stderr=_shorten(proc.stderr),
    )


def _run_call_test(path: Path, test: TestCase, tmpdir: str, timeout: float) -> RunResult:
    args_path = Path(tmpdir) / "args.pkl"
    result_path = Path(tmpdir) / "result.pkl"
    harness_path = Path(tmpdir) / "harness.py"
    args_path.write_bytes(pickle.dumps(test.args or []))
    harness_path.write_text(
        """
import importlib.util
import pickle
import sys

candidate_path, args_path, result_path, fn_name = sys.argv[1:]
spec = importlib.util.spec_from_file_location("candidate", candidate_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

target = getattr(module, fn_name, None)
if not callable(target):
    solution_class = getattr(module, "Solution", None)
    if solution_class is not None:
        target = getattr(solution_class(), fn_name, None)
if not callable(target):
    raise AttributeError(
        f"Expected a module-level function or Solution method named {fn_name!r}"
    )

with open(args_path, "rb") as handle:
    args = pickle.load(handle)
result = target(*args)
with open(result_path, "wb") as handle:
    pickle.dump(result, handle)
""".strip()
        + "\n",
        encoding="utf-8",
    )
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(harness_path),
                str(path),
                str(args_path),
                str(result_path),
                test.fn_name,
            ],
            cwd=tmpdir,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=SANDBOX_ENV,
            preexec_fn=_limit_child_process if platform.system() == "Linux" else None,
        )
    except subprocess.TimeoutExpired:
        return RunResult(
            score=0.0,
            status="timeout",
            protocol="call_based",
            function=test.fn_name,
            failed_input=_json_text(test.args),
            expected=_json_text(test.expected),
            stderr="timeout",
        )

    if proc.returncode != 0:
        return RunResult(
            score=0.0,
            status="runtime_error",
            protocol="call_based",
            function=test.fn_name,
            failed_input=_json_text(test.args),
            expected=_json_text(test.expected),
            stderr=_shorten(proc.stderr),
        )

    try:
        actual = pickle.loads(result_path.read_bytes())
    except (OSError, pickle.PickleError, EOFError) as exc:
        return RunResult(
            score=0.0,
            status="runtime_error",
            protocol="call_based",
            function=test.fn_name,
            failed_input=_json_text(test.args),
            expected=_json_text(test.expected),
            stderr=f"Could not read callable return value: {exc}",
        )

    if _values_equal(actual, test.expected):
        return RunResult(
            score=1.0,
            status="passed",
            protocol="call_based",
            function=test.fn_name,
            passed=1,
            total=1,
        )
    return RunResult(
        score=0.0,
        status="wrong_answer",
        protocol="call_based",
        function=test.fn_name,
        failed_input=_json_text(test.args),
        expected=_json_text(test.expected),
        got=_json_text(actual),
    )


def format_observation(result: RunResult) -> str:
    if result.status == "passed":
        payload = {
            "status": "passed",
            "passed": result.passed,
            "total": result.total,
            "action": "stop",
        }
    else:
        payload: dict[str, Any] = {
            "status": result.status,
            "protocol": result.protocol,
            "passed": result.passed,
            "total": result.total,
            "action": "fix_code",
        }
        if result.protocol == "call_based":
            payload.update(
                {
                    "function": result.function,
                    "arguments": _structured_feedback_value(result.failed_input),
                    "expected_return": _structured_feedback_value(result.expected),
                    "actual_return": _structured_feedback_value(result.got),
                }
            )
        else:
            payload.update(
                {
                    "stdin": result.failed_input,
                    "expected_stdout": result.expected,
                    "actual_stdout": result.got,
                }
            )
        payload["exception"] = result.stderr
        payload["detail"] = result.detail
    return (
        "\n<test_result>\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n</test_result>\n"
        + (
            ""
            if result.status == "passed"
            else "Use this exact test result to fix the code. Output only one corrected fenced Python code block.\n"
        )
    )


def result_to_dict(result: RunResult) -> dict[str, Any]:
    return asdict(result)


def _contains_dangerous_code(code: str) -> bool:
    return any(re.search(pattern, code) for pattern in DANGEROUS_PATTERNS)


def _limit_child_process() -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 * 1024 * 1024, 2 * 1024 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_FSIZE, (4 * 1024 * 1024, 4 * 1024 * 1024))


def _normalize_output(text: str) -> str:
    lines = [line.rstrip() for line in text.strip().splitlines()]
    return "\n".join(lines).strip()


def _values_equal(actual: Any, expected: Any) -> bool:
    actual = _to_builtin_value(actual)
    expected = _to_builtin_value(expected)
    if isinstance(expected, dict) and "__any_of__" in expected:
        return any(_values_equal(actual, item) for item in expected.get("__any_of__") or [])
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        if isinstance(actual, int) and isinstance(expected, int):
            return actual == expected
        try:
            return math.isclose(actual, expected, rel_tol=1e-7, abs_tol=1e-7)
        except OverflowError:
            return actual == expected
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        return len(actual) == len(expected) and all(
            _values_equal(a, e) for a, e in zip(actual, expected, strict=False)
        )
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            _values_equal(actual[key], expected[key]) for key in actual
        )
    try:
        return bool(actual == expected)
    except (TypeError, ValueError):
        return False


def _to_builtin_value(value: Any) -> Any:
    value_type = type(value)
    if value_type.__module__.startswith("numpy") and hasattr(value, "tolist"):
        return value.tolist()
    return value


def _json_text(value: Any) -> str:
    try:
        return _shorten(json.dumps(value, ensure_ascii=False))
    except (TypeError, ValueError):
        return _shorten(repr(value))


def _structured_feedback_value(value: str) -> Any:
    if not value:
        return ""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, ValueError):
        return value


def _shorten(text: str, limit: int = 1200) -> str:
    text = str(text)
    if len(text) <= limit:
        return text
    half = limit // 2
    return text[:half] + "\n...(truncated)...\n" + text[-half:]
