"""Strict validation for Entrega 3 result JSON files."""

from __future__ import annotations

import math
from typing import Any, Iterable


EXPECTED_DATASET_SHA256 = (
    "79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4"
)
EXPECTED_METRICS = (
    "exact_match",
    "f1",
    "rouge1_f",
    "meteor",
    "bert_f1",
    "sbert_similarity",
)
EXPECTED_METADATA = {
    "schema_version": 1,
    "sample_ids": [0],
    "ratio": 0.1,
    "backend": "openai",
    "model": "gpt-4o-mini",
    "dataset_sha256": EXPECTED_DATASET_SHA256,
    "temperature_answer": 0.0,
    "temperature_c5": 0.5,
    "schedule_seed": 20260714,
    "memory_layer": "robust",
}
USAGE_PHASES = ("memory_build", "evaluation", "total")
USAGE_COUNTS = (
    "requests",
    "attempts_total",
    "failed_attempts",
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "total_tokens",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def question_keys(items: Iterable[dict[str, Any]]) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        (item.get("sample_id"), item.get("question"), item.get("reference"), item.get("category"))
        for item in items
    )


def _validate_usage(metadata: dict[str, Any]) -> None:
    usage = metadata.get("usage")
    _require(isinstance(usage, dict), "metadata.usage is required")
    for phase in USAGE_PHASES:
        values = usage.get(phase)
        _require(isinstance(values, dict), f"metadata.usage.{phase} is required")
        for field in USAGE_COUNTS:
            value = values.get(field)
            _require(
                isinstance(value, int) and not isinstance(value, bool) and value >= 0,
                f"metadata.usage.{phase}.{field} must be a non-negative integer",
            )
        cost = values.get("estimated_cost_usd")
        _require(
            isinstance(cost, (int, float)) and math.isfinite(cost) and cost >= 0,
            f"metadata.usage.{phase}.estimated_cost_usd must be non-negative",
        )
        _require(
            values["attempts_total"] == values["requests"] + values["failed_attempts"],
            f"metadata.usage.{phase} attempts are inconsistent",
        )

    build = usage["memory_build"]
    evaluation = usage["evaluation"]
    total = usage["total"]
    for field in (*USAGE_COUNTS, "estimated_cost_usd"):
        _require(
            math.isclose(total[field], build[field] + evaluation[field], abs_tol=1e-9),
            f"metadata.usage.total.{field} is inconsistent with phase totals",
        )


def validate_result_payload(
    result: dict[str, Any],
    *,
    expected_run: dict[str, Any] | None = None,
    expected_questions: int = 199,
    expected_question_keys: tuple[tuple[Any, ...], ...] | None = None,
) -> dict[str, Any]:
    """Validate one completed result and return its auditable identity."""
    _require(isinstance(result, dict), "result must be a JSON object")
    metadata = result.get("metadata")
    _require(isinstance(metadata, dict), "metadata is required")
    for field, expected in EXPECTED_METADATA.items():
        if field == "schedule_seed" and expected_run is not None:
            expected = expected_run["schedule_seed"]
        _require(metadata.get(field) == expected, f"metadata.{field} must equal {expected!r}")
    duration = metadata.get("duration_seconds")
    _require(
        isinstance(duration, (int, float)) and math.isfinite(duration) and duration > 0,
        "metadata.duration_seconds must be positive",
    )
    for field in (
        "timestamp_start_utc",
        "timestamp_end_utc",
        "repo_commit",
        "python_version",
        "platform",
        "command",
        "memories_cache_dir",
    ):
        _require(isinstance(metadata.get(field), str) and metadata[field], f"metadata.{field} is required")

    replicate_id = metadata.get("replicate_id")
    _require(
        isinstance(replicate_id, str)
        and len(replicate_id) == 2
        and replicate_id[0] == "R"
        and replicate_id[1] in "12345",
        "metadata.replicate_id must be one of R1..R5",
    )
    retrieve_k = metadata.get("retrieve_k")
    _require(retrieve_k in (3, 5, 10), "metadata.retrieve_k must be 3, 5, or 10")
    _require(
        metadata.get("seed") == metadata["schedule_seed"] + int(replicate_id[1]),
        "metadata.seed is inconsistent with replicate_id",
    )
    _require(
        metadata.get("schedule_position") in (1, 2, 3),
        "metadata.schedule_position must be 1, 2, or 3",
    )
    _require(
        metadata.get("cache_namespace") == f"entrega3_{replicate_id.lower()}",
        "metadata.cache_namespace is inconsistent with replicate_id",
    )

    if expected_run is not None:
        expected_fields = {
            "replicate_id": expected_run["replicate_id"],
            "retrieve_k": expected_run["retrieve_k"],
            "schedule_seed": expected_run["schedule_seed"],
            "schedule_position": expected_run["position"],
            "cache_namespace": expected_run["cache_namespace"],
            "seed": expected_run["run_seed"],
        }
        for field, expected in expected_fields.items():
            _require(metadata.get(field) == expected, f"metadata.{field} does not match schedule")

    _require(result.get("model") == "gpt-4o-mini", "result.model is inconsistent")
    _require(result.get("memory_layer") == "robust", "result.memory_layer is inconsistent")
    items = result.get("individual_results")
    _require(isinstance(items, list), "individual_results must be a list")
    _require(
        len(items) == expected_questions and result.get("total_questions") == expected_questions,
        f"result must contain exactly {expected_questions} questions",
    )

    for index, item in enumerate(items):
        _require(item.get("sample_id") == 0, f"question {index} must belong to sample 0")
        _require(isinstance(item.get("question"), str), f"question {index} text is required")
        _require(
            isinstance(item.get("reference"), (str, int, float, bool)),
            f"question {index} reference is required",
        )
        _require(item.get("category") in (1, 2, 3, 4, 5), f"question {index} category is invalid")
        metrics = item.get("metrics")
        _require(isinstance(metrics, dict), f"question {index} metrics are required")
        for metric in EXPECTED_METRICS:
            value = metrics.get(metric)
            _require(
                isinstance(value, (int, float)) and math.isfinite(value),
                f"question {index} metric {metric} must be finite",
            )

    keys = question_keys(items)
    if expected_question_keys is not None:
        _require(keys == expected_question_keys, "question identities or order differ between runs")

    aggregate = result.get("aggregate_metrics", {}).get("overall", {})
    for metric in EXPECTED_METRICS:
        reported = aggregate.get(metric, {}).get("mean")
        observed = sum(item["metrics"][metric] for item in items) / len(items)
        _require(
            isinstance(reported, (int, float))
            and math.isfinite(reported)
            and math.isclose(reported, observed, abs_tol=1e-12),
            f"aggregate mean for {metric} is inconsistent",
        )

    _validate_usage(metadata)
    return {
        "replicate_id": replicate_id,
        "retrieve_k": retrieve_k,
        "questions": len(items),
        "question_keys": keys,
        "mean_f1": float(aggregate["f1"]["mean"]),
    }
