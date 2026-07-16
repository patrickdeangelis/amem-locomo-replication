#!/usr/bin/env python3
"""Export deterministic article assets from the Entrega 3 analysis JSON."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


COMPARISON_ORDER = ("3_to_5", "3_to_10", "5_to_10")
F1_FIELDS = (
    "sample_id",
    "total_blocks",
    "replicate_id",
    "retrieve_k",
    "questions",
    "mean_f1",
)
CONTRAST_FIELDS = (
    "sample_id",
    "total_blocks",
    "comparison",
    "delta_R1",
    "delta_R2",
    "delta_R3",
    "delta_R4",
    "delta_R5",
    "mean_delta",
    "min_delta",
    "max_delta",
    "base_mean_f1",
    "relative_difference",
    "relative_difference_definition",
    "ci_low",
    "ci_high",
    "p_value",
    "p_adjusted_holm",
    "p_method",
    "effect_size_dz",
)
METRIC_FIELDS = (
    "retrieve_k",
    "exact_match_mean",
    "f1_mean",
    "rouge1_f_mean",
    "meteor_mean",
    "bert_f1_mean",
    "sbert_similarity_mean",
)
OPERATION_FIELDS = (
    "retrieve_k",
    "duration_seconds_mean",
    "duration_seconds_sd",
    "total_tokens_mean",
    "total_tokens_sd",
    "estimated_cost_usd_mean",
    "estimated_cost_usd_sd",
)
CATEGORY_FIELDS = ("retrieve_k", "category", "f1_mean", "f1_sd")
FIXED_PDF_DATE = dt.datetime(2026, 7, 14, tzinfo=dt.timezone.utc)
PDF_SUBJECT = "LoCoMo sample 0 - five blocks"


def format_float(value: float | None) -> str:
    if value is None or not math.isfinite(float(value)):
        return ""
    return f"{float(value):.6f}"


def validate_analysis(analysis: dict) -> None:
    if analysis.get("scope", {}).get("sample_id") != 0:
        raise ValueError("analysis must describe LoCoMo sample 0")
    if analysis.get("design", {}).get("replicates") != 5:
        raise ValueError("analysis must contain five blocks")
    if len(analysis.get("runs", [])) != 15:
        raise ValueError("analysis must contain 15 block-by-k runs")
    if set(analysis.get("comparisons", {})) != set(COMPARISON_ORDER):
        raise ValueError("analysis must contain the three expected comparisons")


def f1_rows(analysis: dict) -> list[dict[str, str | int]]:
    rows = sorted(
        analysis["runs"], key=lambda row: (str(row["replicate_id"]), row["retrieve_k"])
    )
    return [
        {
            "sample_id": 0,
            "total_blocks": 5,
            "replicate_id": row["replicate_id"],
            "retrieve_k": row["retrieve_k"],
            "questions": row["questions"],
            "mean_f1": format_float(row["mean_f1"]),
        }
        for row in rows
    ]


def contrast_rows(analysis: dict) -> list[dict[str, str | int]]:
    primary = analysis["inference"]["primary"]
    secondary = analysis["inference"]["secondary"]
    rows = []
    for key in COMPARISON_ORDER:
        comparison = analysis["comparisons"][key]
        if key == primary["comparison"]:
            p_value = primary["p_value"]
            adjusted = None
            method = "one-sided exact sign test"
        else:
            p_value = secondary["p_values_raw"][key]
            adjusted = secondary["p_values_holm"][key]
            method = "two-sided exact sign test; Holm adjusted"
        low, high = comparison["bootstrap_95_ci"]
        row: dict[str, str | int] = {
            "sample_id": 0,
            "total_blocks": 5,
            "comparison": key,
            "mean_delta": format_float(comparison["descriptive"]["mean"]),
            "min_delta": format_float(comparison["descriptive"]["min"]),
            "max_delta": format_float(comparison["descriptive"]["max"]),
            "base_mean_f1": format_float(comparison["base_mean_f1"]),
            "relative_difference": format_float(comparison["relative_difference"]),
            "relative_difference_definition": comparison[
                "relative_difference_definition"
            ],
            "ci_low": format_float(low),
            "ci_high": format_float(high),
            "p_value": format_float(p_value),
            "p_adjusted_holm": format_float(adjusted),
            "p_method": method,
            "effect_size_dz": format_float(comparison["effect_size_dz"]),
        }
        for index, delta in enumerate(comparison["deltas"], start=1):
            row[f"delta_R{index}"] = format_float(delta)
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict], fields: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_f1_latex(path: Path, rows: list[dict]) -> None:
    lines = [
        "% Generated deterministically from the Entrega 3 analysis JSON.",
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{F1 por bloco e por $k$ no LoCoMo sample 0, em cinco blocos.}",
        "\\label{tab:entrega3-f1-blocos}",
        "\\begin{tabular}{rrrr}",
        "\\hline",
        "Bloco & $k$ & Perguntas & F1 médio \\\\",
        "\\hline",
    ]
    for row in rows:
        lines.append(
            f"{row['replicate_id']} & {row['retrieve_k']} & {row['questions']} & "
            f"{row['mean_f1']} \\\\"
        )
    lines.extend(["\\hline", "\\end{tabular}", "\\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_contrast_latex(path: Path, rows: list[dict]) -> None:
    lines = [
        "% Generated deterministically from the Entrega 3 analysis JSON.",
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Contrastes pareados de F1 no LoCoMo sample 0, em cinco blocos.}",
        "\\label{tab:entrega3-contrastes}",
        "\\begin{tabular}{lrrrrrrrr}",
        "\\hline",
        "Contraste & Delta médio & Delta mín. & Delta máx. & Dif. relativa & IC 95\\% & $p$ & $p_{Holm}$ & $d_z$ \\\\",
        "\\hline",
    ]
    for row in rows:
        left, right = row["comparison"].split("_to_")
        adjusted = row["p_adjusted_holm"] or "--"
        lines.append(
            f"${left} \\to {right}$ & {row['mean_delta']} & {row['min_delta']} & "
            f"{row['max_delta']} & {row['relative_difference'] or '--'} & "
            f"[{row['ci_low']}, {row['ci_high']}] & {row['p_value']} & "
            f"{adjusted} & {row['effect_size_dz']} \\\\"
        )
    lines.extend(["\\hline", "\\end{tabular}", "\\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def metric_rows(analysis: dict) -> list[dict[str, str | int]]:
    rows = []
    for k in (3, 5, 10):
        metrics = analysis["scenario_summaries"][str(k)]["metrics"]
        rows.append(
            {
                "retrieve_k": k,
                **{
                    f"{metric}_mean": format_float(metrics[metric]["mean"])
                    for metric in (
                        "exact_match",
                        "f1",
                        "rouge1_f",
                        "meteor",
                        "bert_f1",
                        "sbert_similarity",
                    )
                },
            }
        )
    return rows


def operation_rows(analysis: dict) -> list[dict[str, str | int]]:
    rows = []
    for k in (3, 5, 10):
        operations = analysis["scenario_summaries"][str(k)]["operations"]
        rows.append(
            {
                "retrieve_k": k,
                "duration_seconds_mean": format_float(operations["duration_seconds"]["mean"]),
                "duration_seconds_sd": format_float(operations["duration_seconds"]["sd"]),
                "total_tokens_mean": format_float(operations["total_tokens"]["mean"]),
                "total_tokens_sd": format_float(operations["total_tokens"]["sd"]),
                "estimated_cost_usd_mean": format_float(
                    operations["estimated_cost_usd"]["mean"]
                ),
                "estimated_cost_usd_sd": format_float(
                    operations["estimated_cost_usd"]["sd"]
                ),
            }
        )
    return rows


def category_rows(analysis: dict) -> list[dict[str, str | int]]:
    rows = []
    for k in (3, 5, 10):
        categories = analysis["scenario_summaries"][str(k)]["category_f1"]
        for category in sorted(categories, key=int):
            rows.append(
                {
                    "retrieve_k": k,
                    "category": int(category),
                    "f1_mean": format_float(categories[category]["mean"]),
                    "f1_sd": format_float(categories[category]["sd"]),
                }
            )
    return rows


def write_metric_latex(path: Path, rows: list[dict]) -> None:
    lines = [
        "% Generated deterministically from the Entrega 3 analysis JSON.",
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{Médias entre blocos das métricas por cenário no LoCoMo sample 0.}",
        "\\label{tab:metricas-secundarias}",
        "\\begin{tabular}{rrrrrrr}",
        "\\toprule",
        "$k$ & Exact match & F1 & ROUGE-1 F & METEOR & BERT F1 & SBERT \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            f"{row['retrieve_k']} & {row['exact_match_mean']} & {row['f1_mean']} & "
            f"{row['rouge1_f_mean']} & {row['meteor_mean']} & {row['bert_f1_mean']} & "
            f"{row['sbert_similarity_mean']} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table*}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def pdf_metadata(title: str) -> dict:
    return {
        "Title": title,
        "Author": "Patrick Santos",
        "Subject": PDF_SUBJECT,
        "Keywords": "A-Mem, LoCoMo, sample 0, five blocks, reproducibility",
        "Creator": "export_entrega3_assets.py",
        "CreationDate": FIXED_PDF_DATE,
        "ModDate": FIXED_PDF_DATE,
    }


def save_f1_figure(path: Path, rows: list[dict]) -> None:
    fig, axis = plt.subplots(figsize=(6.2, 3.8))
    for retrieve_k in (3, 5, 10):
        selected = [row for row in rows if row["retrieve_k"] == retrieve_k]
        axis.plot(
            [str(row["replicate_id"]) for row in selected],
            [float(row["mean_f1"]) for row in selected],
            marker="o",
            linewidth=1.6,
            label=f"k={retrieve_k}",
        )
    axis.set_title("F1 por bloco — LoCoMo sample 0, cinco blocos")
    axis.set_xlabel("Bloco")
    axis.set_ylabel("F1 médio")
    axis.grid(axis="y", alpha=0.25)
    axis.legend(frameon=False, ncol=3)
    fig.tight_layout()
    fig.savefig(path, metadata=pdf_metadata("F1 by block"))
    plt.close(fig)


def save_delta_figure(path: Path, rows: list[dict]) -> None:
    fig, axis = plt.subplots(figsize=(6.2, 3.8))
    for row in rows:
        left, right = row["comparison"].split("_to_")
        axis.plot(
            range(1, 6),
            [float(row[f"delta_R{index}"]) for index in range(1, 6)],
            marker="o",
            linewidth=1.6,
            label=f"k={left} → k={right}",
        )
    axis.axhline(0.0, color="black", linewidth=0.8)
    axis.set_title("Deltas pareados de F1 — LoCoMo sample 0, cinco blocos")
    axis.set_xlabel("Bloco")
    axis.set_ylabel("Delta de F1")
    axis.set_xticks(range(1, 6), [f"R{index}" for index in range(1, 6)])
    axis.grid(axis="y", alpha=0.25)
    axis.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, metadata=pdf_metadata("Paired F1 deltas"))
    plt.close(fig)


def export_assets(analysis: dict, output_dir: Path) -> None:
    validate_analysis(analysis)
    output_dir.mkdir(parents=True, exist_ok=True)
    runs = f1_rows(analysis)
    contrasts = contrast_rows(analysis)
    metrics = metric_rows(analysis)
    operations = operation_rows(analysis)
    categories = category_rows(analysis)
    write_csv(output_dir / "f1_por_bloco_k.csv", runs, F1_FIELDS)
    write_f1_latex(output_dir / "f1_por_bloco_k.tex", runs)
    write_csv(output_dir / "contrastes_f1.csv", contrasts, CONTRAST_FIELDS)
    write_contrast_latex(output_dir / "contrastes_f1.tex", contrasts)
    write_csv(output_dir / "metricas_por_k.csv", metrics, METRIC_FIELDS)
    write_metric_latex(output_dir / "metricas_por_k.tex", metrics)
    write_csv(output_dir / "operacionais_por_k.csv", operations, OPERATION_FIELDS)
    write_csv(output_dir / "categorias_f1_por_k.csv", categories, CATEGORY_FIELDS)
    save_f1_figure(output_dir / "f1_por_bloco.pdf", runs)
    save_delta_figure(output_dir / "deltas_f1.pdf", contrasts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis_json", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    analysis = json.loads(args.analysis_json.read_text(encoding="utf-8"))
    export_assets(analysis, args.output_dir)


if __name__ == "__main__":
    main()
