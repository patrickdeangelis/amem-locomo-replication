import json
from pathlib import Path

import pytest

from analysis.result_validation import EXPECTED_DATASET_SHA256
from run_entrega3 import (
    build_command,
    build_execution_environment,
    build_schedule,
    classify_existing_result,
    select_runs,
    write_schedule,
)


def completed_result(run: dict) -> dict:
    metrics = {
        "exact_match": 0.0,
        "f1": 0.25,
        "rouge1_f": 0.3,
        "meteor": 0.2,
        "bert_f1": 0.8,
        "sbert_similarity": 0.7,
    }
    phase = {
        "requests": 1,
        "attempts_total": 1,
        "failed_attempts": 0,
        "input_tokens": 10,
        "cached_input_tokens": 0,
        "output_tokens": 2,
        "total_tokens": 12,
        "estimated_cost_usd": 0.001,
    }
    return {
        "model": "gpt-4o-mini",
        "memory_layer": "robust",
        "total_questions": 199,
        "metadata": {
            "schema_version": 1,
            "sample_ids": [0],
            "ratio": 0.1,
            "backend": "openai",
            "model": "gpt-4o-mini",
            "dataset_sha256": EXPECTED_DATASET_SHA256,
            "temperature_answer": 0.0,
            "temperature_c5": 0.5,
            "schedule_seed": run["schedule_seed"],
            "memory_layer": "robust",
            "duration_seconds": 1.0,
            "timestamp_start_utc": "2026-07-15T00:00:00+00:00",
            "timestamp_end_utc": "2026-07-15T00:00:01+00:00",
            "repo_commit": "base-commit",
            "python_version": "3.11.15",
            "platform": "test-platform",
            "command": "test command",
            "memories_cache_dir": "cache",
            "replicate_id": run["replicate_id"],
            "retrieve_k": run["retrieve_k"],
            "seed": run["run_seed"],
            "schedule_position": run["position"],
            "cache_namespace": run["cache_namespace"],
            "usage": {
                "memory_build": dict(phase),
                "evaluation": dict(phase),
                "total": {key: value * 2 for key, value in phase.items()},
            },
        },
        "individual_results": [
            {
                "sample_id": 0,
                "question": f"question {index}",
                "reference": f"reference {index}",
                "category": (index % 5) + 1,
                "metrics": dict(metrics),
            }
            for index in range(199)
        ],
        "aggregate_metrics": {
            "overall": {metric: {"mean": value} for metric, value in metrics.items()}
        },
    }


def test_schedule_is_deterministic_complete_and_randomized():
    first = build_schedule(replicates=5, schedule_seed=20260714)
    second = build_schedule(replicates=5, schedule_seed=20260714)

    assert first == second
    assert len(first["runs"]) == 15

    orders = []
    for replicate_id in [f"R{i}" for i in range(1, 6)]:
        runs = [run for run in first["runs"] if run["replicate_id"] == replicate_id]
        assert sorted(run["retrieve_k"] for run in runs) == [3, 5, 10]
        assert len({run["output"] for run in runs}) == 3
        assert {run["cache_namespace"] for run in runs} == {
            f"entrega3_{replicate_id.lower()}"
        }
        orders.append(tuple(run["retrieve_k"] for run in runs))

    assert len(set(orders)) > 1
    first_position_counts = {
        k: sum(order[0] == k for order in orders) for k in [3, 5, 10]
    }
    assert max(first_position_counts.values()) - min(first_position_counts.values()) <= 1
    assert build_schedule(replicates=5, schedule_seed=7) != first


def test_build_command_carries_auditable_run_identity():
    run = build_schedule(replicates=1, schedule_seed=11)["runs"][0]
    command = build_command(run, python_executable="python-test")

    assert command[0:2] == ["python-test", "test_advanced_robust.py"]
    assert command[command.index("--replicate-id") + 1] == "R1"
    assert command[command.index("--schedule-seed") + 1] == "11"
    assert command[command.index("--schedule-position") + 1] == str(run["position"])
    assert command[command.index("--cache-namespace") + 1] == "entrega3_r1"
    assert command[command.index("--retrieve_k") + 1] in {"3", "5", "10"}
    assert "--ratio" in command
    assert command[command.index("--ratio") + 1] == "0.1"


def test_existing_result_is_skipped_only_when_identity_matches(tmp_path: Path):
    run = build_schedule(replicates=1, schedule_seed=11)["runs"][0]
    output = tmp_path / "result.json"
    run = {**run, "output": str(output)}

    assert classify_existing_result(run) == "missing"

    output.write_text("not json", encoding="utf-8")
    assert classify_existing_result(run) == "invalid"

    output.write_text(json.dumps({"metadata": {"replicate_id": "R1"}}), encoding="utf-8")
    assert classify_existing_result(run) == "invalid"

    output.write_text(json.dumps(completed_result(run)), encoding="utf-8")
    assert classify_existing_result(run) == "valid"

    data = json.loads(output.read_text(encoding="utf-8"))
    data["metadata"]["retrieve_k"] = 999
    output.write_text(json.dumps(data), encoding="utf-8")
    assert classify_existing_result(run) == "invalid"


def test_invalid_replicate_count_is_rejected():
    with pytest.raises(ValueError, match="replicates"):
        build_schedule(replicates=0, schedule_seed=1)


def test_runs_can_be_limited_for_a_budget_gate():
    schedule = build_schedule(replicates=5, schedule_seed=20260714)

    pilot = select_runs(schedule, replicate_ids=["R1"], max_runs=1)
    assert len(pilot) == 1
    assert pilot[0]["replicate_id"] == "R1"
    assert pilot[0]["position"] == 1

    block = select_runs(schedule, replicate_ids=["R1"])
    assert len(block) == 3
    assert {run["retrieve_k"] for run in block} == {3, 5, 10}

    with pytest.raises(ValueError, match="unknown replicate"):
        select_runs(schedule, replicate_ids=["R99"])
    with pytest.raises(ValueError, match="max_runs"):
        select_runs(schedule, max_runs=0)


def test_execution_environment_keeps_runtime_caches_inside_project(tmp_path: Path):
    environment = build_execution_environment(tmp_path, {"PATH": "/bin"})

    assert environment["PATH"] == "/bin"
    assert environment["HF_HOME"] == str(tmp_path / ".cache/huggingface")
    assert environment["MPLCONFIGDIR"] == str(tmp_path / ".cache/matplotlib")
    assert environment["NLTK_DATA"] == str(tmp_path / ".cache/nltk")


def test_existing_schedule_is_preserved_and_conflicts_are_rejected(tmp_path: Path):
    path = tmp_path / "schedule.json"
    schedule = build_schedule(replicates=5, schedule_seed=20260714)
    write_schedule(schedule, path)
    original = path.read_bytes()

    write_schedule(schedule, path)
    assert path.read_bytes() == original

    changed = build_schedule(replicates=5, schedule_seed=7)
    with pytest.raises(ValueError, match="differs"):
        write_schedule(changed, path)
