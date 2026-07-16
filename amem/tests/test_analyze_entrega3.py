import json

import pytest

from analysis.analyze_entrega3 import analyze_runs, write_outputs
from analysis.result_validation import EXPECTED_DATASET_SHA256


RUN_MEANS = {
    1: {3: 0.20, 5: 0.25, 10: 0.30},
    2: {3: 0.22, 5: 0.28, 10: 0.34},
    3: {3: 0.24, 5: 0.27, 10: 0.35},
    4: {3: 0.21, 5: 0.29, 10: 0.30},
    5: {3: 0.23, 5: 0.30, 10: 0.36},
}


def synthetic_runs() -> list[dict]:
    runs = []
    for replicate_number, by_k in RUN_MEANS.items():
        for position, (retrieve_k, mean_f1) in enumerate(by_k.items(), start=1):
            metrics = {
                "exact_match": 0.1,
                "f1": mean_f1,
                "rouge1_f": mean_f1 + 0.01,
                "meteor": mean_f1 - 0.01,
                "bert_f1": 0.8,
                "sbert_similarity": 0.7,
            }
            phase = {
                "requests": 1,
                "attempts_total": 1,
                "failed_attempts": 0,
                "input_tokens": 10 * retrieve_k,
                "cached_input_tokens": 0,
                "output_tokens": 2,
                "total_tokens": 10 * retrieve_k + 2,
                "estimated_cost_usd": retrieve_k / 1000,
            }
            runs.append(
                {
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
                        "duration_seconds": float(retrieve_k),
                        "timestamp_start_utc": "2026-07-15T00:00:00+00:00",
                        "timestamp_end_utc": "2026-07-15T00:00:01+00:00",
                        "repo_commit": "base-commit",
                        "python_version": "3.11.15",
                        "platform": "test-platform",
                        "command": "test command",
                        "memories_cache_dir": f"cache-r{replicate_number}",
                        "replicate_id": f"R{replicate_number}",
                        "retrieve_k": retrieve_k,
                        "seed": 20260714 + replicate_number,
                        "schedule_position": position,
                        "cache_namespace": f"entrega3_r{replicate_number}",
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
                            "category": index + 1,
                            "metrics": dict(metrics),
                        }
                        for index in range(2)
                    ],
                    "aggregate_metrics": {
                        "overall": {
                            metric: {"mean": value} for metric, value in metrics.items()
                        }
                    },
                }
            )
    return runs


def test_analyzes_five_complete_blocks_and_writes_reproduction_outputs(tmp_path) -> None:
    result = analyze_runs(synthetic_runs(), expected_questions=2)

    assert result["scope"] == {
        "sample_id": 0,
        "statement": "Results are conditioned on LoCoMo sample 0 and do not generalize to the full dataset.",
    }
    assert result["design"] == {
        "replicates": 5,
        "retrieve_k": [3, 5, 10],
        "runs": 15,
    }
    assert len(result["runs"]) == 15
    assert {
        key: result["runs"][0][key]
        for key in ("replicate_id", "retrieve_k", "questions", "mean_f1")
    } == {
        "replicate_id": "R1",
        "retrieve_k": 3,
        "questions": 2,
        "mean_f1": pytest.approx(0.20),
    }

    comparison = result["comparisons"]["3_to_10"]
    assert comparison["deltas"] == pytest.approx([0.10, 0.12, 0.11, 0.09, 0.13])
    assert comparison["descriptive"]["mean"] == pytest.approx(0.11)
    assert comparison["descriptive"]["median"] == pytest.approx(0.11)
    assert comparison["descriptive"]["sd"] == pytest.approx(0.0158113883)
    assert comparison["descriptive"]["iqr"] == pytest.approx(0.02)
    assert comparison["descriptive"]["min"] == pytest.approx(0.09)
    assert comparison["descriptive"]["max"] == pytest.approx(0.13)
    assert comparison["base_mean_f1"] == pytest.approx(0.22)
    assert comparison["relative_difference"] == pytest.approx(0.50)
    assert (
        comparison["relative_difference_definition"]
        == "mean_delta / mean_f1_of_base_scenario"
    )
    assert comparison["bootstrap_95_ci"][0] <= 0.11 <= comparison["bootstrap_95_ci"][1]
    assert comparison["effect_size_dz"] == pytest.approx(6.95701085)
    assert set(comparison["shapiro_wilk"]) == {"statistic", "p_value", "diagnostic_only"}
    assert comparison["shapiro_wilk"]["diagnostic_only"] is True

    assert result["inference"]["primary"] == {
        "comparison": "3_to_10",
        "alternative": "greater",
        "null_hypothesis": "P(delta > 0) <= 0.5",
        "method": "one-sided exact sign test",
        "p_value": pytest.approx(0.03125),
    }
    secondary = result["inference"]["secondary"]
    assert set(secondary["p_values_raw"]) == {"3_to_5", "5_to_10"}
    assert set(secondary["p_values_holm"]) == {"3_to_5", "5_to_10"}
    assert all(
        secondary["p_values_holm"][key] >= secondary["p_values_raw"][key]
        for key in secondary["p_values_raw"]
    )

    json_path = tmp_path / "analysis.json"
    markdown_path = tmp_path / "analysis.md"
    write_outputs(result, json_path=json_path, markdown_path=markdown_path)
    assert json.loads(json_path.read_text(encoding="utf-8"))["scope"]["sample_id"] == 0
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "LoCoMo sample 0" in markdown
    assert "3 → 10" in markdown
    assert "Shapiro-Wilk" in markdown
    assert "mín." in markdown
    assert "máx." in markdown
    assert "dif. relativa" in markdown
    assert "média do delta / média de F1 do cenário-base" in markdown


def test_rejects_an_incomplete_block_matrix() -> None:
    runs = synthetic_runs()
    runs.pop()

    with pytest.raises(ValueError, match="incomplete experiment matrix"):
        analyze_runs(runs, expected_questions=2)


def test_rejects_duplicate_replicate_and_k_runs() -> None:
    runs = synthetic_runs()
    runs.append(runs[0])

    with pytest.raises(ValueError, match="duplicate run"):
        analyze_runs(runs, expected_questions=2)


def test_holm_adjustment_contains_only_the_two_secondary_comparisons() -> None:
    secondary = analyze_runs(synthetic_runs(), expected_questions=2)["inference"]["secondary"]

    assert set(secondary["p_values_raw"]) == {"3_to_5", "5_to_10"}
    assert set(secondary["p_values_holm"]) == {"3_to_5", "5_to_10"}


def test_relative_difference_is_null_when_the_base_scenario_mean_is_zero() -> None:
    runs = synthetic_runs()
    for run in runs:
        if run["metadata"]["retrieve_k"] == 3:
            for item in run["individual_results"]:
                item["metrics"]["f1"] = 0.0
            run["aggregate_metrics"]["overall"]["f1"]["mean"] = 0.0

    result = analyze_runs(runs, expected_questions=2)

    assert result["comparisons"]["3_to_5"]["relative_difference"] is None
    assert result["comparisons"]["3_to_10"]["relative_difference"] is None
