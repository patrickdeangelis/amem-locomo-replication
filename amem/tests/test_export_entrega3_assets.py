from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "analysis" / "export_entrega3_assets.py"
RUN_MEANS = {
    1: {3: 0.20, 5: 0.25, 10: 0.30},
    2: {3: 0.22, 5: 0.28, 10: 0.34},
    3: {3: 0.24, 5: 0.27, 10: 0.35},
    4: {3: 0.21, 5: 0.29, 10: 0.30},
    5: {3: 0.23, 5: 0.30, 10: 0.36},
}


def analysis_fixture() -> dict:
    comparisons = {
        "3_to_5": {
            "deltas": [0.05, 0.06, 0.03, 0.08, 0.07],
            "descriptive": {
                "mean": 0.058,
                "median": 0.06,
                "sd": 0.0192,
                "iqr": 0.02,
                "min": 0.03,
                "max": 0.08,
            },
            "base_mean_f1": 0.22,
            "relative_difference": 0.263636,
            "relative_difference_definition": "mean_delta / mean_f1_of_base_scenario",
            "bootstrap_95_ci": [0.044, 0.072],
            "effect_size_dz": 3.0208,
        },
        "3_to_10": {
            "deltas": [0.10, 0.12, 0.11, 0.09, 0.13],
            "descriptive": {
                "mean": 0.11,
                "median": 0.11,
                "sd": 0.0158,
                "iqr": 0.02,
                "min": 0.09,
                "max": 0.13,
            },
            "base_mean_f1": 0.22,
            "relative_difference": 0.5,
            "relative_difference_definition": "mean_delta / mean_f1_of_base_scenario",
            "bootstrap_95_ci": [0.098, 0.122],
            "effect_size_dz": 6.9570,
        },
        "5_to_10": {
            "deltas": [0.05, 0.06, 0.08, 0.01, 0.06],
            "descriptive": {
                "mean": 0.052,
                "median": 0.06,
                "sd": 0.0268,
                "iqr": 0.01,
                "min": 0.01,
                "max": 0.08,
            },
            "base_mean_f1": 0.278,
            "relative_difference": 0.187050,
            "relative_difference_definition": "mean_delta / mean_f1_of_base_scenario",
            "bootstrap_95_ci": [0.030, 0.071],
            "effect_size_dz": 1.9403,
        },
    }
    return {
        "scope": {"sample_id": 0, "statement": "Conditioned on LoCoMo sample 0."},
        "design": {"replicates": 5, "retrieve_k": [3, 5, 10], "runs": 15},
        "runs": [
            {
                "replicate_id": replicate_id,
                "retrieve_k": retrieve_k,
                "questions": 199,
                "mean_f1": mean_f1,
            }
            for replicate_id, by_k in RUN_MEANS.items()
            for retrieve_k, mean_f1 in by_k.items()
        ],
        "comparisons": comparisons,
        "scenario_summaries": {
            str(k): {
                "metrics": {
                    metric: {"mean": value}
                    for metric, value in {
                        "exact_match": 0.1,
                        "f1": sum(RUN_MEANS[r][k] for r in RUN_MEANS) / 5,
                        "rouge1_f": 0.3,
                        "meteor": 0.2,
                        "bert_f1": 0.8,
                        "sbert_similarity": 0.7,
                    }.items()
                },
                "operations": {
                    field: {"mean": mean, "sd": sd}
                    for field, (mean, sd) in {
                        "duration_seconds": (100.0 * k, 10.0),
                        "total_tokens": (1000.0 * k, 100.0),
                        "estimated_cost_usd": (0.01 * k, 0.001),
                    }.items()
                },
                "category_f1": {
                    str(category): {"mean": 0.1 * category, "sd": 0.01}
                    for category in range(1, 6)
                },
            }
            for k in (3, 5, 10)
        },
        "inference": {
            "primary": {
                "comparison": "3_to_10",
                "alternative": "greater",
                "p_value": 0.03125,
            },
            "secondary": {
                "method": "two-sided exact sign tests with Holm adjustment",
                "p_values_raw": {"3_to_5": 0.0625, "5_to_10": 0.0625},
                "p_values_holm": {"3_to_5": 0.125, "5_to_10": 0.125},
            },
        },
    }


def digest_tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.iterdir())
        if path.is_file()
    }


def test_cli_exports_complete_deterministic_article_assets(tmp_path: Path) -> None:
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(
        json.dumps(analysis_fixture(), ensure_ascii=False), encoding="utf-8"
    )
    first = tmp_path / "first" / "assets"
    second = tmp_path / "second" / "assets"

    for output_dir in (first, second):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(analysis_path),
                "--output-dir",
                str(output_dir),
            ],
            capture_output=True,
            check=False,
            text=True,
        )
        assert result.returncode == 0, result.stderr

    expected = {
        "f1_por_bloco_k.csv",
        "f1_por_bloco_k.tex",
        "contrastes_f1.csv",
        "contrastes_f1.tex",
        "f1_por_bloco.pdf",
        "deltas_f1.pdf",
        "metricas_por_k.csv",
        "metricas_por_k.tex",
        "operacionais_por_k.csv",
        "categorias_f1_por_k.csv",
    }
    assert set(digest_tree(first)) == expected
    assert digest_tree(first) == digest_tree(second)

    with (first / "f1_por_bloco_k.csv").open(encoding="utf-8", newline="") as file:
        f1_rows = list(csv.DictReader(file))
    assert len(f1_rows) == 15
    assert f1_rows[0]["sample_id"] == "0"
    assert f1_rows[0]["total_blocks"] == "5"
    assert f1_rows[0]["mean_f1"] == "0.200000"

    with (first / "contrastes_f1.csv").open(encoding="utf-8", newline="") as file:
        contrast_rows = {row["comparison"]: row for row in csv.DictReader(file)}
    assert contrast_rows["3_to_10"]["delta_R1"] == "0.100000"
    assert contrast_rows["3_to_10"]["ci_low"] == "0.098000"
    assert contrast_rows["3_to_10"]["p_value"] == "0.031250"
    assert contrast_rows["3_to_10"]["effect_size_dz"] == "6.957000"
    assert contrast_rows["3_to_10"]["min_delta"] == "0.090000"
    assert contrast_rows["3_to_10"]["max_delta"] == "0.130000"
    assert contrast_rows["3_to_10"]["relative_difference"] == "0.500000"

    for latex_name in ("f1_por_bloco_k.tex", "contrastes_f1.tex"):
        latex = (first / latex_name).read_text(encoding="utf-8")
        assert "sample 0" in latex
        assert "cinco blocos" in latex
    contrast_latex = (first / "contrastes_f1.tex").read_text(encoding="utf-8")
    assert "Delta mín." in contrast_latex
    assert "Delta máx." in contrast_latex
    assert "Dif. relativa" in contrast_latex

    for pdf_name in ("f1_por_bloco.pdf", "deltas_f1.pdf"):
        pdf = (first / pdf_name).read_bytes()
        assert pdf.startswith(b"%PDF")
        assert b"LoCoMo sample 0 - five blocks" in pdf
