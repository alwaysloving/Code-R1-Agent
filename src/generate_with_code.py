from __future__ import annotations

import json
import os
import re
from dataclasses import asdict
from typing import Any

from sandbox_runner import RunResult, parse_tests, run_tests
from slime.rollout.sglang_rollout import GenerateState
from slime.utils import logging_utils
from slime.utils.http_utils import post
from slime.utils.metric_utils import compute_rollout_step
from slime.utils.types import Sample


CODE_R1_CONFIGS = {
    "max_turns": int(os.environ.get("CODE_R1_MAX_TURNS", os.environ.get("APPS_AGENT_MAX_ACTIONS", "3"))),
    "return_logprob": os.environ.get("CODE_R1_RETURN_LOGPROB", "1") == "1",
    "observation_field_chars": int(os.environ.get("CODE_R1_OBSERVATION_FIELD_CHARS", "200")),
}

ACTION_RE = re.compile(r"<(test|answer)>\s*(.*?)\s*</\1>", re.DOTALL | re.IGNORECASE)
PYTHON_BLOCK_RE = re.compile(r"```(?:python|py)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _decode_label(label: Any) -> Any:
    if isinstance(label, str):
        try:
            return json.loads(label)
        except json.JSONDecodeError:
            return label
    return label


def _tests_from_sample(sample: Sample) -> tuple[list[Any], list[Any]]:
    metadata = sample.metadata or {}
    public_tests = parse_tests(metadata.get("public_tests"))
    hidden_tests = parse_tests(_decode_label(sample.label))
    return public_tests, hidden_tests


def _parse_action(text: str) -> tuple[str | None, str, str]:
    match = ACTION_RE.search(text or "")
    if not match:
        return None, "", ""
    action = match.group(1).lower()
    content = match.group(2)
    code_blocks = PYTHON_BLOCK_RE.findall(content)
    code = code_blocks[-1].strip() if code_blocks else content.strip()
    return action, code, content


def _shorten_observation_value(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    limit = CODE_R1_CONFIGS["observation_field_chars"]
    if limit <= 0 or len(text) <= limit:
        return text
    return text[:limit] + f"...(truncated {len(text) - limit} chars)"


def _format_test_observation(result: RunResult) -> str:
    payload = {
        "status": result.status,
        "passed": result.passed,
        "total": result.total,
    }
    if result.status != "passed":
        payload.update(
            {
                "failed_input": _shorten_observation_value(result.failed_input),
                "expected": _shorten_observation_value(result.expected),
                "got": _shorten_observation_value(result.got),
                "stderr": _shorten_observation_value(result.stderr),
                "detail": _shorten_observation_value(result.detail),
            }
        )
    return "\n\n<information>" + json.dumps(payload, ensure_ascii=False) + "</information>\n\n"


def _format_invalid_observation() -> str:
    return (
        "\n\n<information>"
        + json.dumps(
            {
                "status": "invalid_action",
                "message": "Use <test> fenced Python code </test> to run public tests, or <answer> fenced Python code </answer> to submit.",
            },
            ensure_ascii=False,
        )
        + "</information>\n\n"
    )


async def generate(args, sample: Sample, sampling_params: dict[str, Any]) -> Sample:
    assert not args.partial_rollout, "Partial rollout is not supported for code tool rollouts."

    state = GenerateState(args)
    url = f"http://{args.sglang_router_ip}:{args.sglang_router_port}/generate"

    public_tests, hidden_tests = _tests_from_sample(sample)
    prompt_text = sample.prompt
    prompt_token_ids = state.tokenizer(prompt_text, add_special_tokens=False)["input_ids"]

    response = ""
    response_token_ids: list[int] = []
    loss_mask: list[int] = []
    rollout_log_probs: list[float] | None = [] if CODE_R1_CONFIGS["return_logprob"] else None
    final_result: RunResult | None = None
    final_code = ""
    answered = False
    valid_test_calls = 0
    valid_answer_calls = 0
    invalid_actions = 0
    finish_type = "stop"

    for _turn_idx in range(CODE_R1_CONFIGS["max_turns"]):
        remaining = int(args.rollout_max_response_len) - len(response_token_ids)
        if remaining <= 0:
            finish_type = "length"
            break

        turn_sampling = dict(sampling_params)
        turn_sampling["max_new_tokens"] = min(int(turn_sampling.get("max_new_tokens", remaining)), remaining)
        payload = {"text": prompt_text + response, "sampling_params": turn_sampling}
        if CODE_R1_CONFIGS["return_logprob"]:
            payload["return_logprob"] = True

        output = await post(url, payload)
        finish_type = output["meta_info"]["finish_reason"]["type"]
        if finish_type == "abort":
            sample.status = Sample.Status.ABORTED
            return sample

        cur_response = output["text"]
        if CODE_R1_CONFIGS["return_logprob"]:
            token_logprobs = output["meta_info"].get("output_token_logprobs") or []
            cur_token_ids = [item[1] for item in token_logprobs]
            cur_log_probs = [item[0] for item in token_logprobs]
        else:
            cur_token_ids = state.tokenizer(cur_response, add_special_tokens=False)["input_ids"]
            cur_log_probs = []

        response += cur_response
        response_token_ids.extend(cur_token_ids)
        loss_mask.extend([1] * len(cur_token_ids))
        if rollout_log_probs is not None:
            rollout_log_probs.extend(cur_log_probs)

        if finish_type == "length":
            break

        action, code, _content = _parse_action(cur_response)
        if action == "answer":
            valid_answer_calls += 1
            answered = True
            final_code = code
            final_result = run_tests(code, public_tests + hidden_tests)
            break
        if action == "test":
            valid_test_calls += 1
            final_code = code
            result = run_tests(code, public_tests)
            observation = _format_test_observation(result)
        else:
            invalid_actions += 1
            observation = _format_invalid_observation()

        obs_token_ids = state.tokenizer(observation, add_special_tokens=False)["input_ids"]
        response += observation
        response_token_ids.extend(obs_token_ids)
        loss_mask.extend([0] * len(obs_token_ids))
        if rollout_log_probs is not None:
            rollout_log_probs.extend([0.0] * len(obs_token_ids))

    if final_result is None:
        final_result = RunResult(score=0.0, status="no_answer", total=len(public_tests) + len(hidden_tests))

    reward = 1.0 if answered and final_result.total > 0 and final_result.passed == final_result.total else 0.0

    sample.tokens = prompt_token_ids + response_token_ids
    sample.response_length = len(response_token_ids)
    sample.response = response
    sample.loss_mask = loss_mask
    sample.prompt = prompt_text
    sample.reward = reward
    if rollout_log_probs is not None:
        sample.rollout_log_probs = rollout_log_probs if rollout_log_probs else None
    sample.metadata = {
        **(sample.metadata or {}),
        "code_r1": {
            "reward": reward,
            "final_result": asdict(final_result),
            "test_calls": valid_test_calls,
            "answer_calls": valid_answer_calls,
            "invalid_actions": invalid_actions,
            "answered": answered,
            "finish_type": finish_type,
        },
    }

    sample.status = Sample.Status.TRUNCATED if finish_type == "length" else Sample.Status.COMPLETED
    return sample


async def reward_func(args, sample: Sample, **kwargs):
    if not isinstance(sample, Sample):
        raise TypeError("Sample must be an instance of Sample class.")
    info = (sample.metadata or {}).get("code_r1") or {}
    if "reward" in info:
        return float(info["reward"])
    action, code, _ = _parse_action(sample.response)
    if action != "answer":
        return 0.0
    public_tests, hidden_tests = _tests_from_sample(sample)
    result = run_tests(code, public_tests + hidden_tests)
    return 1.0 if result.total > 0 and result.passed == result.total else 0.0


def _flatten(samples):
    result = []
    for item in samples:
        result.extend(_flatten(item) if isinstance(item, list) else [item])
    return result


def _mean(values):
    return sum(values) / len(values) if values else 0.0


def log_rollout_data(rollout_id, args, samples, rollout_extra_metrics, rollout_time):
    flat = _flatten(samples)
    if not flat:
        return False
    infos = [(sample.metadata or {}).get("code_r1") or {} for sample in flat]
    results = [info.get("final_result") or {} for info in infos]
    metrics = rollout_extra_metrics if rollout_extra_metrics is not None else {}
    metrics.clear()
    metrics.update(
        {
            "code_r1/reward": _mean([float(sample.get_reward_value(args)) for sample in flat]),
            "code_r1/pass_rate": _mean(
                [int(result.get("total", 0) > 0 and result.get("passed", 0) == result.get("total", 0)) for result in results]
            ),
            "code_r1/test_calls": _mean([int(info.get("test_calls", 0)) for info in infos]),
            "code_r1/answer_calls": _mean([int(info.get("answer_calls", 0)) for info in infos]),
            "code_r1/invalid_actions": _mean([int(info.get("invalid_actions", 0)) for info in infos]),
            "perf/rollout_time": rollout_time,
            "rollout/step": compute_rollout_step(args, rollout_id),
        }
    )
    logging_utils.log(args, metrics, step_key="rollout/step")
    return True


def log_eval_rollout_data(rollout_id, args, data, extra_metrics):
    metrics = extra_metrics if extra_metrics is not None else {}
    metrics.clear()
    for dataset_name, dataset_data in data.items():
        samples = dataset_data.get("samples") or []
        if not samples:
            continue
        infos = [(sample.metadata or {}).get("code_r1") or {} for sample in samples]
        results = [info.get("final_result") or {} for info in infos]
        full_pass = [
            int(result.get("total", 0) > 0 and result.get("passed", 0) == result.get("total", 0))
            for result in results
        ]
        group_size = max(1, int(getattr(args, "n_samples_per_eval_prompt", 1) or 1))
        pass_at_k = [
            int(any(full_pass[start : start + group_size]))
            for start in range(0, len(full_pass), group_size)
            if full_pass[start : start + group_size]
        ]
        prefix = f"eval/{dataset_name}"
        metrics.update(
            {
                f"{prefix}/reward": _mean([float(sample.get_reward_value(args)) for sample in samples]),
                f"{prefix}/pass_at_1": _mean(full_pass),
                f"{prefix}/pass_at_{group_size}": _mean(pass_at_k),
                f"{prefix}/test_calls": _mean([int(info.get("test_calls", 0)) for info in infos]),
                f"{prefix}/answer_calls": _mean([int(info.get("answer_calls", 0)) for info in infos]),
                f"{prefix}/invalid_actions": _mean([int(info.get("invalid_actions", 0)) for info in infos]),
            }
        )
    metrics["eval/step"] = compute_rollout_step(args, rollout_id)
    print(f"code_r1_eval_metrics rollout_id={rollout_id} metrics={metrics}", flush=True)
    logging_utils.log(args, metrics, step_key="eval/step")
    return True
