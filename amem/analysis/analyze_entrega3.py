#!/usr/bin/env python3
"""Analyze the five-block, single-dialogue experiment for Entrega 3."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.stats import shapiro

try:
    from analysis.result_validation import EXPECTED_METRICS, validate_result_payload
except ModuleNotFoundError:  # Direct execution: python analysis/analyze_entrega3.py
    from result_validation import EXPECTED_METRICS, validate_result_payload


EXPECTED_K = (3, 5, 10)
EXPECTED_REPLICATES = 5
COMPARISONS = ((3, 5), (3, 10), (5, 10))
SECONDARY_COMPARISONS = ((3, 5), (5, 10))
BOOTSTRAP_SEED = 0
BOOTSTRAP_SAMPLES = 10_000
SCOPE_STATEMENT = (
    "Results are conditioned on LoCoMo sample 0 and do not generalize to the full dataset."
)


def _validated_run_means(
    runs: Iterable[dict], *, expected_questions: int
) -> dict[tuple[object, int], dict]:
    indexed: dict[tuple[object, int], dict] = {}
    replicate_ids: set[object] = set()
    expected_question_keys = None
    for run in runs:
        validated = validate_result_payload(
            run,
            expected_questions=expected_questions,
            expected_question_keys=expected_question_keys,
        )
        if expected_question_keys is None:
            expected_question_keys = validated["question_keys"]
        metadata = run["metadata"]
        replicate_id = validated["replicate_id"]
        retrieve_k = validated["retrieve_k"]
        key = (replicate_id, retrieve_k)
        if key in indexed:
            raise ValueError(
                f"duplicate run for replicate_id={replicate_id!r}, retrieve_k={retrieve_k}"
            )
        overall = run["aggregate_metrics"]["overall"]
        metric_means = {metric: float(overall[metric]["mean"]) for metric in EXPECTED_METRICS}
        categories = {}
        for category in range(1, 6):
            values = [
                item["metrics"]["f1"]
                for item in run["individual_results"]
                if item["category"] == category
            ]
            categories[str(category)] = float(np.mean(values)) if values else None
        evaluation = metadata["usage"]["evaluation"]
        indexed[key] = {
            "replicate_id": replicate_id,
            "retrieve_k": retrieve_k,
            "schedule_position": int(metadata["schedule_position"]),
            "questions": validated["questions"],
            "mean_f1": validated["mean_f1"],
            "metric_means": metric_means,
            "category_f1": categories,
            "operations": {
                "duration_seconds": float(metadata["duration_seconds"]),
                "requests": int(evaluation["requests"]),
                "input_tokens": int(evaluation["input_tokens"]),
                "cached_input_tokens": int(evaluation["cached_input_tokens"]),
                "output_tokens": int(evaluation["output_tokens"]),
                "total_tokens": int(evaluation["total_tokens"]),
                "estimated_cost_usd": float(evaluation["estimated_cost_usd"]),
            },
        }
        replicate_ids.add(replicate_id)

    expected = {(replicate_id, k) for replicate_id in replicate_ids for k in EXPECTED_K}
    if (
        len(replicate_ids) != EXPECTED_REPLICATES
        or set(indexed) != expected
        or len(indexed) != EXPECTED_REPLICATES * len(EXPECTED_K)
    ):
        raise ValueError(
            "incomplete experiment matrix: expected five replicates with exactly k=3,5,10"
        )
    for replicate_id in replicate_ids:
        positions = {indexed[(replicate_id, k)]["schedule_position"] for k in EXPECTED_K}
        if positions != {1, 2, 3}:
            raise ValueError(f"invalid schedule positions for replicate {replicate_id}")
    return indexed


def _descriptive(values: np.ndarray) -> dict[str, float]:
    q1, q3 = np.quantile(values, [0.25, 0.75])
    return {
        "mean": float(values.mean()),
        "median": float(np.median(values)),
        "sd": float(values.std(ddof=1)),
        "iqr": float(q3 - q1),
        "min": float(values.min()),
        "max": float(values.max()),
    }


def _bootstrap_mean_ci(values: np.ndarray) -> list[float]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    indices = rng.integers(0, values.size, size=(BOOTSTRAP_SAMPLES, values.size))
    means = values[indices].mean(axis=1)
    low, high = np.quantile(means, [0.025, 0.975])
    return [float(low), float(high)]


def _exact_sign_test_p(values: np.ndarray, *, alternative: str) -> float:
    nonzero = values[values != 0]
    positives = int(np.sum(nonzero > 0))
    n = int(nonzero.size)
    if n == 0:
        return 1.0
    upper = sum(math.comb(n, count) for count in range(positives, n + 1)) / (2**n)
    if alternative == "greater":
        return upper
    if alternative == "two-sided":
        lower = sum(math.comb(n, count) for count in range(0, positives + 1)) / (2**n)
        return min(1.0, 2 * min(lower, upper))
    raise ValueError(f"unsupported alternative: {alternative}")


def _holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values, key=p_values.get)
    adjusted: dict[str, float] = {}
    running_max = 0.0
    total = len(ordered)
    for rank, key in enumerate(ordered):
        candidate = min(1.0, (total - rank) * p_values[key])
        running_max = max(running_max, candidate)
        adjusted[key] = running_max
    return {key: adjusted[key] for key in p_values}


def analyze_runs(runs: Iterable[dict], *, expected_questions: int = 199) -> dict:
    """Analyze exactly five paired blocks for k=3,5,10 on LoCoMo sample 0."""
    indexed = _validated_run_means(runs, expected_questions=expected_questions)
    replicate_ids = sorted({key[0] for key in indexed}, key=str)
    run_rows = [indexed[(replicate_id, k)] for replicate_id in replicate_ids for k in EXPECTED_K]

    comparisons = {}
    raw_secondary_p_values = {}
    for left, right in COMPARISONS:
        key = f"{left}_to_{right}"
        deltas = np.asarray(
            [
                indexed[(replicate_id, right)]["mean_f1"]
                - indexed[(replicate_id, left)]["mean_f1"]
                for replicate_id in replicate_ids
            ],
            dtype=float,
        )
        sd = float(deltas.std(ddof=1))
        base_mean_f1 = float(
            np.mean(
                [
                    indexed[(replicate_id, left)]["mean_f1"]
                    for replicate_id in replicate_ids
                ]
            )
        )
        shapiro_result = shapiro(deltas)
        comparisons[key] = {
            "deltas": [float(value) for value in deltas],
            "descriptive": _descriptive(deltas),
            "bootstrap_95_ci": _bootstrap_mean_ci(deltas),
            "effect_size_dz": float(deltas.mean() / sd) if sd else None,
            "base_mean_f1": base_mean_f1,
            "relative_difference": (
                float(deltas.mean() / base_mean_f1) if base_mean_f1 != 0.0 else None
            ),
            "relative_difference_definition": "mean_delta / mean_f1_of_base_scenario",
            "shapiro_wilk": {
                "statistic": float(shapiro_result.statistic),
                "p_value": float(shapiro_result.pvalue),
                "diagnostic_only": True,
            },
        }
        if (left, right) in SECONDARY_COMPARISONS:
            raw_secondary_p_values[key] = _exact_sign_test_p(
                deltas, alternative="two-sided"
            )

    primary_deltas = np.asarray(comparisons["3_to_10"]["deltas"], dtype=float)
    scenario_summaries = {}
    for k in EXPECTED_K:
        selected = [indexed[(replicate_id, k)] for replicate_id in replicate_ids]
        scenario_summaries[str(k)] = {
            "metrics": {
                metric: _descriptive(
                    np.asarray([row["metric_means"][metric] for row in selected], dtype=float)
                )
                for metric in EXPECTED_METRICS
            },
            "operations": {
                field: _descriptive(
                    np.asarray([row["operations"][field] for row in selected], dtype=float)
                )
                for field in selected[0]["operations"]
            },
            "category_f1": {
                category: _descriptive(
                    np.asarray([row["category_f1"][category] for row in selected], dtype=float)
                )
                for category in selected[0]["category_f1"]
                if all(row["category_f1"][category] is not None for row in selected)
            },
        }
    return {
        "scope": {"sample_id": 0, "statement": SCOPE_STATEMENT},
        "design": {
            "replicates": EXPECTED_REPLICATES,
            "retrieve_k": list(EXPECTED_K),
            "runs": len(run_rows),
        },
        "runs": run_rows,
        "scenario_summaries": scenario_summaries,
        "comparisons": comparisons,
        "inference": {
            "primary": {
                "comparison": "3_to_10",
                "alternative": "greater",
                "null_hypothesis": "P(delta > 0) <= 0.5",
                "method": "one-sided exact sign test",
                "p_value": _exact_sign_test_p(primary_deltas, alternative="greater"),
            },
            "secondary": {
                "method": "two-sided exact sign tests with Holm adjustment",
                "p_values_raw": raw_secondary_p_values,
                "p_values_holm": _holm_adjust(raw_secondary_p_values),
            },
        },
    }


def render_markdown(result: dict) -> str:
    lines = [
        "# Entrega 3 — análise estatística",
        "",
        f"**Escopo:** {result['scope']['statement']}",
        "",
        "## Médias de F1 por execução",
        "",
        "| bloco | k | perguntas | F1 médio |",
        "|---:|---:|---:|---:|",
    ]
    for run in result["runs"]:
        lines.append(
            f"| {run['replicate_id']} | {run['retrieve_k']} | {run['questions']} | "
            f"{run['mean_f1']:.6f} |"
        )

    lines += [
        "",
        "## Comparações pareadas por bloco",
        "",
        "| comparação | média | mediana | DP | IQR | mín. | máx. | dif. relativa | IC bootstrap 95% | dz | Shapiro-Wilk p |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|",
    ]
    for key, comparison in result["comparisons"].items():
        descriptive = comparison["descriptive"]
        low, high = comparison["bootstrap_95_ci"]
        dz = comparison["effect_size_dz"]
        dz_text = "n/a" if dz is None or not math.isfinite(dz) else f"{dz:.4f}"
        relative = comparison["relative_difference"]
        relative_text = "n/a" if relative is None else f"{relative:.6f}"
        label = key.replace("_to_", " → ")
        lines.append(
            f"| {label} | {descriptive['mean']:.6f} | {descriptive['median']:.6f} | "
            f"{descriptive['sd']:.6f} | {descriptive['iqr']:.6f} | "
            f"{descriptive['min']:.6f} | {descriptive['max']:.6f} | {relative_text} | "
            f"[{low:.6f}, {high:.6f}] | {dz_text} | "
            f"{comparison['shapiro_wilk']['p_value']:.6f} |"
        )

    lines += [
        "",
        "Diferença relativa = média do delta / média de F1 do cenário-base "
        "(lado esquerdo do contraste); é n/a quando a média-base é zero.",
        "",
        "## Métricas por cenário",
        "",
        "| k | exact match | F1 | ROUGE-1 F | METEOR | BERT F1 | SBERT |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for k, summary in result["scenario_summaries"].items():
        metrics = summary["metrics"]
        lines.append(
            f"| {k} | {metrics['exact_match']['mean']:.6f} | {metrics['f1']['mean']:.6f} | "
            f"{metrics['rouge1_f']['mean']:.6f} | {metrics['meteor']['mean']:.6f} | "
            f"{metrics['bert_f1']['mean']:.6f} | {metrics['sbert_similarity']['mean']:.6f} |"
        )
    lines += [
        "",
        "## Métricas operacionais da avaliação por cenário",
        "",
        "| k | duração média (s) | DP duração | tokens médios | DP tokens | custo médio (US$) | DP custo |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for k, summary in result["scenario_summaries"].items():
        operations = summary["operations"]
        lines.append(
            f"| {k} | {operations['duration_seconds']['mean']:.3f} | "
            f"{operations['duration_seconds']['sd']:.3f} | {operations['total_tokens']['mean']:.1f} | "
            f"{operations['total_tokens']['sd']:.1f} | "
            f"{operations['estimated_cost_usd']['mean']:.6f} | "
            f"{operations['estimated_cost_usd']['sd']:.6f} |"
        )

    primary = result["inference"]["primary"]
    secondary = result["inference"]["secondary"]
    lines += [
        "",
        "## Inferência",
        "",
        f"O teste exato de sinais unilateral para 3 → 10, com "
        f"H0: {primary['null_hypothesis']}, produziu p = {primary['p_value']:.6f}.",
        "",
        "Os testes secundários são bilaterais e seus p-valores foram ajustados por Holm.",
        "",
        "| comparação | p bruto | p ajustado por Holm |",
        "|---|---:|---:|",
    ]
    for key, raw_p in secondary["p_values_raw"].items():
        lines.append(
            f"| {key.replace('_to_', ' → ')} | {raw_p:.6f} | "
            f"{secondary['p_values_holm'][key]:.6f} |"
        )
    lines += [
        "",
        "O teste de Shapiro-Wilk é apresentado somente como diagnóstico; com cinco blocos, "
        "ele não substitui a inferência exata não paramétrica.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(result: dict, *, json_path: Path, markdown_path: Path) -> None:
    json_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(result), encoding="utf-8")


def _load_runs(paths: Iterable[Path]) -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze five complete k=3/5/10 blocks for LoCoMo sample 0."
    )
    parser.add_argument("results", nargs="+", type=Path)
    parser.add_argument("--json-output", required=True, type=Path)
    parser.add_argument("--markdown-output", required=True, type=Path)
    args = parser.parse_args()
    result = analyze_runs(_load_runs(args.results))
    write_outputs(
        result, json_path=args.json_output, markdown_path=args.markdown_output
    )


if __name__ == "__main__":
    main()
