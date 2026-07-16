from __future__ import annotations

from copy import deepcopy

import pytest

from analysis.result_validation import EXPECTED_DATASET_SHA256, validate_result_payload


METRICS = {
    "exact_match": 0.0,
    "f1": 0.25,
    "rouge1_f": 0.3,
    "meteor": 0.2,
    "bert_f1": 0.8,
    "sbert_similarity": 0.7,
}


def complete_result() -> dict:
    questions = [
        {
            "sample_id": 0,
            "question": f"question {index}",
            "reference": f"reference {index}",
            "category": index + 1,
            "metrics": dict(METRICS),
        }
        for index in range(2)
    ]
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
    total = {key: value * 2 for key, value in phase.items()}
    return {
        "model": "gpt-4o-mini",
        "memory_layer": "robust",
        "total_questions": 2,
        "metadata": {
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
            "duration_seconds": 1.0,
            "timestamp_start_utc": "2026-07-15T00:00:00+00:00",
            "timestamp_end_utc": "2026-07-15T00:00:01+00:00",
            "repo_commit": "base-commit",
            "python_version": "3.11.15",
            "platform": "test-platform",
            "command": "test command",
            "memories_cache_dir": "cache",
            "replicate_id": "R1",
            "retrieve_k": 3,
            "seed": 20260715,
            "schedule_position": 1,
            "cache_namespace": "entrega3_r1",
            "usage": {
                "memory_build": dict(phase),
                "evaluation": dict(phase),
                "total": total,
            },
        },
        "individual_results": questions,
        "aggregate_metrics": {
            "overall": {
                metric: {"mean": value} for metric, value in METRICS.items()
            }
        },
    }


def test_accepts_complete_consistent_result() -> None:
    validated = validate_result_payload(complete_result(), expected_questions=2)

    assert validated["replicate_id"] == "R1"
    assert validated["retrieve_k"] == 3
    assert validated["questions"] == 2
    assert validated["mean_f1"] == pytest.approx(0.25)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda result: result["individual_results"].pop(), "exactly 2 questions"),
        (lambda result: result["metadata"].update(sample_ids=[1]), "sample_ids"),
        (lambda result: result["metadata"].update(model="other"), "metadata.model"),
        (lambda result: result["metadata"].update(dataset_sha256="bad"), "dataset_sha256"),
        (
            lambda result: result["aggregate_metrics"]["overall"]["f1"].update(mean=0.9),
            "aggregate mean for f1",
        ),
        (
            lambda result: result["metadata"]["usage"]["total"].update(requests=99),
            "inconsistent",
        ),
    ],
)
def test_rejects_incomplete_or_inconsistent_results(mutate, message: str) -> None:
    result = complete_result()
    mutate(result)

    with pytest.raises(ValueError, match=message):
        validate_result_payload(result, expected_questions=2)


def test_rejects_question_identity_or_order_changes() -> None:
    first = complete_result()
    expected = validate_result_payload(first, expected_questions=2)["question_keys"]
    changed = deepcopy(first)
    changed["individual_results"].reverse()

    with pytest.raises(ValueError, match="identities or order"):
        validate_result_payload(
            changed,
            expected_questions=2,
            expected_question_keys=expected,
        )
