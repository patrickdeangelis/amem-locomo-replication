#!/usr/bin/env python3
"""Export tables and figures for the Etapa 2 article from ratio01 result JSONs."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = PROJECT_ROOT / "local-article-assets"
FIGURE_DIR = PROJECT_ROOT / "local-figures"
RESULTS = [
    PROJECT_ROOT / "amem/results/results_amem_gpt4omini_ratio01_k3.json",
    PROJECT_ROOT / "amem/results/results_amem_gpt4omini_ratio01_k5.json",
    PROJECT_ROOT / "amem/results/results_amem_gpt4omini_ratio01_k10.json",
]
METRICS = ["exact_match", "f1", "bleu1", "rouge1_f", "meteor", "sbert_similarity"]
CATEGORY_LABELS = {
    "1": "single-hop",
    "2": "temporal",
    "3": "multi-hop",
    "4": "open-ended",
    "5": "adversarial",
}


def load_runs() -> list[dict]:
    runs = []
    for path in RESULTS:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        runs.append(data)
    return sorted(runs, key=lambda run: run["metadata"]["retrieve_k"])


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def bootstrap_ci(values: list[float], *, seed: int = 0, n: int = 10000) -> tuple[float, float]:
    rng = random.Random(seed)
    samples = []
    size = len(values)
    for _ in range(n):
        samples.append(mean([values[rng.randrange(size)] for _ in range(size)]))
    samples.sort()
    return samples[int(0.025 * n)], samples[int(0.975 * n)]


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_aggregate_table(runs: list[dict]) -> list[dict]:
    rows = []
    for run in runs:
        overall = run["aggregate_metrics"]["overall"]
        row = {
            "retrieve_k": run["metadata"]["retrieve_k"],
            "questions": run["total_questions"],
            "duration_seconds": run["metadata"]["duration_seconds"],
        }
        for metric in METRICS:
            values = [item["metrics"][metric] for item in run["individual_results"]]
            lo, hi = bootstrap_ci(values)
            row[metric] = overall[metric]["mean"]
            row[f"{metric}_ci_low"] = lo
            row[f"{metric}_ci_high"] = hi
        rows.append(row)

    fields = ["retrieve_k", "questions", "duration_seconds"]
    for metric in METRICS:
        fields += [metric, f"{metric}_ci_low", f"{metric}_ci_high"]
    write_csv(ASSET_DIR / "table_aggregate_metrics.csv", rows, fields)
    return rows


def export_category_table(runs: list[dict]) -> list[dict]:
    rows = []
    for run in runs:
        k = run["metadata"]["retrieve_k"]
        metrics = run["aggregate_metrics"]
        for category, label in CATEGORY_LABELS.items():
            block = metrics[f"category_{category}"]
            rows.append(
                {
                    "retrieve_k": k,
                    "category": category,
                    "label": label,
                    "questions": block["f1"]["count"],
                    "exact_match": block["exact_match"]["mean"],
                    "f1": block["f1"]["mean"],
                    "bleu1": block["bleu1"]["mean"],
                    "rouge1_f": block["rouge1_f"]["mean"],
                    "meteor": block["meteor"]["mean"],
                    "sbert_similarity": block["sbert_similarity"]["mean"],
                }
            )
    fields = [
        "retrieve_k",
        "category",
        "label",
        "questions",
        "exact_match",
        "f1",
        "bleu1",
        "rouge1_f",
        "meteor",
        "sbert_similarity",
    ]
    write_csv(ASSET_DIR / "table_category_metrics.csv", rows, fields)
    return rows


def result_key(item: dict) -> tuple[int, str]:
    return item["sample_id"], item["question"]


def export_pairwise_table(runs: list[dict]) -> list[dict]:
    by_k = {
        run["metadata"]["retrieve_k"]: {
            result_key(item): item for item in run["individual_results"]
        }
        for run in runs
    }
    pairs = [(3, 5), (3, 10), (5, 10)]
    rows = []
    for left, right in pairs:
        keys = sorted(set(by_k[left]) & set(by_k[right]))
        for metric in METRICS:
            diffs = [
                by_k[right][key]["metrics"][metric] - by_k[left][key]["metrics"][metric]
                for key in keys
            ]
            lo, hi = bootstrap_ci(diffs)
            rows.append(
                {
                    "comparison": f"k={left} -> k={right}",
                    "metric": metric,
                    "questions": len(keys),
                    "mean_diff": mean(diffs),
                    "ci_low": lo,
                    "ci_high": hi,
                    "improved": sum(1 for value in diffs if value > 0),
                    "worsened": sum(1 for value in diffs if value < 0),
                    "unchanged": sum(1 for value in diffs if value == 0),
                }
            )
    fields = [
        "comparison",
        "metric",
        "questions",
        "mean_diff",
        "ci_low",
        "ci_high",
        "improved",
        "worsened",
        "unchanged",
    ]
    write_csv(ASSET_DIR / "table_pairwise_deltas.csv", rows, fields)
    return rows


def export_worst_examples(runs: list[dict]) -> None:
    rows = []
    for run in runs:
        k = run["metadata"]["retrieve_k"]
        ordered = sorted(run["individual_results"], key=lambda item: item["metrics"]["f1"])
        for rank, item in enumerate(ordered[:10], start=1):
            rows.append(
                {
                    "retrieve_k": k,
                    "rank": rank,
                    "category": item["category"],
                    "f1": item["metrics"]["f1"],
                    "exact_match": item["metrics"]["exact_match"],
                    "question": item["question"],
                    "prediction": item["prediction"],
                    "reference": item["reference"],
                }
            )
    fields = [
        "retrieve_k",
        "rank",
        "category",
        "f1",
        "exact_match",
        "question",
        "prediction",
        "reference",
    ]
    write_csv(ASSET_DIR / "table_worst_f1_examples.csv", rows, fields)


def export_cost_table() -> None:
    manifest_path = PROJECT_ROOT / "docs/manifest-etapa-2.json"
    with manifest_path.open(encoding="utf-8") as f:
        usage = json.load(f)["api_usage"]
    rows = [
        {
            "bucket_start_utc": usage["bucket_utc"]["start"],
            "bucket_end_utc": usage["bucket_utc"]["end"],
            "model": usage["model"],
            "requests": usage["num_model_requests"],
            "input_tokens": usage["input_tokens"],
            "input_cached_tokens": usage["input_cached_tokens"],
            "input_uncached_tokens": usage["input_uncached_tokens"],
            "output_tokens": usage["output_tokens"],
            "amount_value": usage["amount_value"],
            "amount_currency": usage["amount_currency"],
            "aggregation": usage["aggregation"],
        }
    ]
    write_csv(ASSET_DIR / "table_openai_usage_cost.csv", rows, list(rows[0]))


def save_f1_by_k(rows: list[dict]) -> None:
    ks = [row["retrieve_k"] for row in rows]
    f1 = [row["f1"] for row in rows]
    lo = [row["f1_ci_low"] for row in rows]
    hi = [row["f1_ci_high"] for row in rows]
    plt.figure(figsize=(4.2, 2.8))
    plt.errorbar(
        ks,
        f1,
        yerr=[[y - l for y, l in zip(f1, lo)], [h - y for y, h in zip(f1, hi)]],
        marker="o",
        linewidth=1.8,
        capsize=4,
    )
    plt.xticks(ks, [str(k) for k in ks])
    plt.xlabel("retrieve_k")
    plt.ylabel("F1 medio")
    plt.ylim(0.18, 0.40)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "f1_por_k.pdf")
    plt.close()


def save_metrics_by_k(rows: list[dict]) -> None:
    ks = [row["retrieve_k"] for row in rows]
    plt.figure(figsize=(5.4, 3.2))
    for metric in METRICS:
        plt.plot(ks, [row[metric] for row in rows], marker="o", label=metric)
    plt.xticks(ks, [str(k) for k in ks])
    plt.xlabel("retrieve_k")
    plt.ylabel("media")
    plt.ylim(0, 0.55)
    plt.grid(axis="y", alpha=0.25)
    plt.legend(fontsize=7, ncol=2)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "metricas_por_k.pdf")
    plt.close()


def save_category_f1(category_rows: list[dict]) -> None:
    categories = list(CATEGORY_LABELS)
    labels = [CATEGORY_LABELS[c] for c in categories]
    ks = [3, 5, 10]
    width = 0.24
    xs = list(range(len(categories)))
    plt.figure(figsize=(5.6, 3.2))
    for offset, k in enumerate(ks):
        values = [
            next(
                row["f1"]
                for row in category_rows
                if row["retrieve_k"] == k and row["category"] == category
            )
            for category in categories
        ]
        positions = [x + (offset - 1) * width for x in xs]
        plt.bar(positions, values, width=width, label=f"k={k}")
    plt.xticks(xs, labels, rotation=25, ha="right")
    plt.ylabel("F1 medio")
    plt.ylim(0, 0.58)
    plt.grid(axis="y", alpha=0.25)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "f1_por_categoria.pdf")
    plt.close()


def save_duration_by_k(rows: list[dict]) -> None:
    ks = [row["retrieve_k"] for row in rows]
    minutes = [row["duration_seconds"] / 60 for row in rows]
    plt.figure(figsize=(4.2, 2.8))
    plt.bar([str(k) for k in ks], minutes)
    plt.xlabel("retrieve_k")
    plt.ylabel("duracao (min)")
    plt.ylim(0, max(minutes) * 1.2)
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "tempo_por_k.pdf")
    plt.close()


def main() -> int:
    ASSET_DIR.mkdir(exist_ok=True)
    FIGURE_DIR.mkdir(exist_ok=True)
    runs = load_runs()
    aggregate_rows = export_aggregate_table(runs)
    category_rows = export_category_table(runs)
    export_pairwise_table(runs)
    export_worst_examples(runs)
    export_cost_table()
    save_f1_by_k(aggregate_rows)
    save_metrics_by_k(aggregate_rows)
    save_category_f1(category_rows)
    save_duration_by_k(aggregate_rows)
    print(f"wrote article assets to {ASSET_DIR}")
    print(f"wrote figures to {FIGURE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
