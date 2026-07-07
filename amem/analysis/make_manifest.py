#!/usr/bin/env python3
"""Generate `manifest-etapa-2.json`: a versionable, auditable manifest of the
Etapa 2 execution.

The manifest records, for every artifact that matters for reproducibility:
  - sha256 hash
  - size in bytes
  - relative path

It also records the base A-Mem commit, the commands used, observed timings and
run parameters. Results JSONs are versioned in this public repository; logs and
local caches are intentionally omitted.

Run from the repository root:

    python amem/analysis/make_manifest.py

Writes `docs/manifest-etapa-2.json`.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


BASE_AMEM_COMMIT = "0c8039f28fdcc08189a23c07a3437d9d2482f9c2"
BASE_AMEM_REMOTE = "https://github.com/WujiangXu/A-mem.git"

# Files to hash, relative to the repository root.
ARTIFACTS = [
    # Datasets.
    "amem/data/locomo10.json",
    "amem/data/locomo_etapa2_reduced_s2.json",
    "amem/data/locomo_smoke_min.json",
    # Primary ratio01 results JSONs.
    "amem/results/results_amem_gpt4omini_ratio01_k3.json",
    "amem/results/results_amem_gpt4omini_ratio01_k5.json",
    "amem/results/results_amem_gpt4omini_ratio01_k10.json",
    # Results JSONs. These are the post-correction reduced runs
    # (seed=0, temperature=0.0, with metadata block).
    "amem/results/results_amem_gpt4omini_smoke_min_k10.json",
    "amem/results/results_amem_gpt4omini_reduced_s2_k3.json",
    "amem/results/results_amem_gpt4omini_reduced_s2_k5.json",
    "amem/results/results_amem_gpt4omini_reduced_s2_k10.json",
    # Pre-correction JSONs preserved for the before/after comparison.
    "amem/results/before-correction/results_amem_gpt4omini_reduced_s2_k3.json",
    "amem/results/before-correction/results_amem_gpt4omini_reduced_s2_k5.json",
    "amem/results/before-correction/results_amem_gpt4omini_reduced_s2_k10.json",
    # Analysis scripts.
    "amem/analysis/make_smoke_dataset.py",
    "amem/analysis/make_reduced_dataset.py",
    "amem/analysis/summarize_results.py",
    "amem/analysis/export_article_assets.py",
    "amem/analysis/estimate_cost.py",
    "amem/analysis/make_manifest.py",
    "amem/analysis/relatorio-etapa-2-ratio01.md",
    "amem/analysis/relatorio-etapa-2.md",
    "amem/analysis/relatorio-etapa-2-before.md",
    "docs/openai-api-usage-2026-07-07.md",
    # Harness + run scripts.
    "amem/test_advanced_robust.py",
    "amem/run_etapa2_smoke.sh",
    "amem/run_etapa2_reduced.sh",
    "amem/run_etapa2_ratio01.sh",
    "amem/run_etapa2_final.sh",
    # Docs.
    "README.md",
    "docs/comandos-etapa-2.md",
    "docs/resultados-etapa-2-ratio01.md",
    "docs/resultados-etapa-2.md",
    "docs/resultados-antes-pos-correcao.md",
    "paper/article-assets/table_aggregate_metrics.csv",
    "paper/article-assets/table_category_metrics.csv",
    "paper/article-assets/table_openai_usage_cost.csv",
    "paper/article-assets/table_pairwise_deltas.csv",
    "paper/article-assets/table_worst_f1_examples.csv",
    "paper/figures/f1_por_k.pdf",
    "paper/figures/f1_por_categoria.pdf",
    "paper/figures/metricas_por_k.pdf",
    "paper/figures/tempo_por_k.pdf",
    "paper/entrega_2_reprodutibilidade_patrick_santos.pdf",
]


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# Observed timings. Durations for post-correction and ratio01 runs come from
# the metadata blocks in the result JSONs.
OBSERVED_RUNS = [
    {
        "label": "ratio01_k3",
        "dataset": "data/locomo10.json",
        "ratio": 0.1,
        "retrieve_k": 3,
        "cold": False,
        "wall_seconds": 755.474,
        "log": "logs/eval_robust_gpt-4o-mini_openai_ratio0.1_2026-07-07-12-43.log",
        "result_file": "results/results_amem_gpt4omini_ratio01_k3.json",
        "seed": 0,
        "temperature_answer": 0.0,
        "temperature_c5": 0.5,
        "note": "Primary ratio01 rerun with caffeinate; reusou cache existente.",
    },
    {
        "label": "ratio01_k5",
        "dataset": "data/locomo10.json",
        "ratio": 0.1,
        "retrieve_k": 5,
        "cold": False,
        "wall_seconds": 810.171,
        "log": "logs/eval_robust_gpt-4o-mini_openai_ratio0.1_2026-07-07-12-55.log",
        "result_file": "results/results_amem_gpt4omini_ratio01_k5.json",
        "seed": 0,
        "temperature_answer": 0.0,
        "temperature_c5": 0.5,
        "note": "Primary ratio01 rerun with caffeinate; reusou cache existente.",
    },
    {
        "label": "ratio01_k10",
        "dataset": "data/locomo10.json",
        "ratio": 0.1,
        "retrieve_k": 10,
        "cold": False,
        "wall_seconds": 899.266,
        "log": "logs/eval_robust_gpt-4o-mini_openai_ratio0.1_2026-07-07-13-09.log",
        "result_file": "results/results_amem_gpt4omini_ratio01_k10.json",
        "seed": 0,
        "temperature_answer": 0.0,
        "temperature_c5": 0.5,
        "note": "Primary ratio01 rerun with caffeinate; reusou cache existente.",
    },
    {
        "label": "smoke_min_k10 (pre-correction)",
        "dataset": "data/locomo_smoke_min.json",
        "retrieve_k": 10,
        "cold": True,
        "wall_seconds_estimated": 74.46,
        "log": "logs/eval_robust_gpt-4o-mini_openai_ratio1.0_2026-07-07-09-20.log",
        "result_file": "results/results_amem_gpt4omini_smoke_min_k10.json",
        "seed": None,
        "temperature_answer": 0.7,
        "note": "Pre-correction smoke run; no seed, temp 0.7. Inclui warmup do SentenceTransformer.",
    },
    {
        "label": "reduced_s2_k3 (pre-correction)",
        "dataset": "data/locomo_etapa2_reduced_s2.json",
        "retrieve_k": 3,
        "cold": True,
        "wall_seconds_estimated": 300.0,
        "log": "logs/eval_robust_gpt-4o-mini_openai_ratio1.0_2026-07-07-09-23.log",
        "result_file": "results/before-correction/results_amem_gpt4omini_reduced_s2_k3.json",
        "seed": None,
        "temperature_answer": 0.7,
        "note": "Pre-correction; criou o cache de memorias. Sem seed, temp 0.7.",
    },
    {
        "label": "reduced_s2_k5 (pre-correction)",
        "dataset": "data/locomo_etapa2_reduced_s2.json",
        "retrieve_k": 5,
        "cold": False,
        "wall_seconds_estimated": 60.0,
        "log": "logs/eval_robust_gpt-4o-mini_openai_ratio1.0_2026-07-07-09-28.log",
        "result_file": "results/before-correction/results_amem_gpt4omini_reduced_s2_k5.json",
        "seed": None,
        "temperature_answer": 0.7,
        "note": "Pre-correction; reusou cache. Sem seed, temp 0.7.",
    },
    {
        "label": "reduced_s2_k10 (pre-correction)",
        "dataset": "data/locomo_etapa2_reduced_s2.json",
        "retrieve_k": 10,
        "cold": False,
        "wall_seconds_estimated": 60.0,
        "log": "logs/eval_robust_gpt-4o-mini_openai_ratio1.0_2026-07-07-09-30.log",
        "result_file": "results/before-correction/results_amem_gpt4omini_reduced_s2_k10.json",
        "seed": None,
        "temperature_answer": 0.7,
        "note": "Pre-correction; reusou cache. Sem seed, temp 0.7.",
    },
    {
        "label": "reduced_s2_k3 (post-correction)",
        "dataset": "data/locomo_etapa2_reduced_s2.json",
        "retrieve_k": 3,
        "cold": False,
        "wall_seconds": 91.561,
        "log": "logs/eval_robust_gpt-4o-mini_openai_ratio1.0_2026-07-07-10-08.log",
        "result_file": "results/results_amem_gpt4omini_reduced_s2_k3.json",
        "seed": 0,
        "temperature_answer": 0.0,
        "note": "Post-correction; reusou cache. seed=0, temp=0.0.",
    },
    {
        "label": "reduced_s2_k5 (post-correction)",
        "dataset": "data/locomo_etapa2_reduced_s2.json",
        "retrieve_k": 5,
        "cold": False,
        "wall_seconds": 107.837,
        "log": "logs/eval_robust_gpt-4o-mini_openai_ratio1.0_2026-07-07-10-10.log",
        "result_file": "results/results_amem_gpt4omini_reduced_s2_k5.json",
        "seed": 0,
        "temperature_answer": 0.0,
        "note": "Post-correction; reusou cache. seed=0, temp=0.0.",
    },
    {
        "label": "reduced_s2_k10 (post-correction)",
        "dataset": "data/locomo_etapa2_reduced_s2.json",
        "retrieve_k": 10,
        "cold": False,
        "wall_seconds": 93.378,
        "log": "logs/eval_robust_gpt-4o-mini_openai_ratio1.0_2026-07-07-10-12.log",
        "result_file": "results/results_amem_gpt4omini_reduced_s2_k10.json",
        "seed": 0,
        "temperature_answer": 0.0,
        "note": "Post-correction; reusou cache. seed=0, temp=0.0.",
    },
]

# Commands actually executed (kept in sync with comandos-etapa-2.md).
COMMANDS = {
    "clone": "git clone https://github.com/WujiangXu/amem.git",
    "env_setup": ".venv/bin/python -m pip install -r requirements.txt",
    "smoke": "./run_etapa2_smoke.sh",
    "reduced": "./run_etapa2_reduced.sh",
    "ratio01": "./run_etapa2_ratio01.sh",
    "ratio01_caffeinate": "/usr/bin/caffeinate -dimsu ./run_etapa2_ratio01.sh",
    "final": "./run_etapa2_final.sh",
    "summarize_ratio01": (
        ".venv/bin/python analysis/summarize_results.py "
        "results/results_amem_gpt4omini_ratio01_k3.json "
        "results/results_amem_gpt4omini_ratio01_k5.json "
        "results/results_amem_gpt4omini_ratio01_k10.json "
        "--output analysis/relatorio-etapa-2-ratio01.md"
    ),
    "summarize": (
        ".venv/bin/python analysis/summarize_results.py "
        "results/results_amem_gpt4omini_reduced_s2_k3.json "
        "results/results_amem_gpt4omini_reduced_s2_k5.json "
        "results/results_amem_gpt4omini_reduced_s2_k10.json "
        "--output analysis/relatorio-etapa-2.md"
    ),
    "estimate": ".venv/bin/python analysis/estimate_cost.py --print-md",
    "article_assets": (
        "MPLCONFIGDIR=../.cache/matplotlib "
        ".venv/bin/python analysis/export_article_assets.py"
    ),
}

# Run parameters for the planned primary ratio01 execution.
RUN_PARAMETERS = {
    "backend": "openai",
    "model": "gpt-4o-mini",
    "dataset": "data/locomo10.json",
    "dataset_sha256": "79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4",
    "ratio": 0.1,
    "dataset_origin": "sample 0 inteiro de data/locomo10.json selecionado por --ratio 0.1",
    "samples": 1,
    "sessions": 19,
    "turns": 419,
    "questions": 199,
    "category_distribution": {"1": 32, "2": 37, "3": 13, "4": 70, "5": 47},
    "retrieve_k_values": [3, 5, 10],
    "seed": 0,
    "temperature_categories_1_4": 0.0,
    "temperature_c5": 0.5,
    "metadata_block": True,
    "result_files": "results/results_amem_gpt4omini_ratio01_k*.json",
    "memory_cache_dir": "cached_memories_robust_openai_gpt-4o-mini_locomo10_79fa87e90f04",
    "cache_shared_across_k": True,
    "cache_shared_note": (
        "A reexecucao com caffeinate reutilizou o cache existente de 419 "
        "memorias para k=3, k=5 e k=10."
    ),
    "preserved_reduced_run": {
        "dataset": "data/locomo_etapa2_reduced_s2.json",
        "dataset_origin": "sample 0 de data/locomo10.json, sessoes 1-2, perguntas com evidencia restrita",
        "samples": 1,
        "sessions": 2,
        "turns": 35,
        "questions": 20,
        "result_files": "results/results_amem_gpt4omini_reduced_s2_k*.json",
        "before_correction_result_files": "results/before-correction/results_amem_gpt4omini_reduced_s2_k*.json",
        "note": "Rodada preservada apenas como historico de depuracao e comparacao de reprodutibilidade.",
    },
}

API_USAGE = {
    "source_exports": [
        "/Users/patrick/Downloads/cost_2026-06-07_2026-07-07.csv",
        "/Users/patrick/Downloads/completions_usage_2026-06-07_2026-07-07.csv",
    ],
    "aggregation": "daily",
    "bucket_utc": {
        "start": "2026-07-07T00:00:00+00:00",
        "end": "2026-07-08T00:00:00+00:00",
    },
    "project_name": "Default Project",
    "organization_name": "Personal",
    "model": "gpt-4o-mini-2024-07-18",
    "service_tier": "default",
    "batch": False,
    "num_model_requests": 4228,
    "input_tokens": 5789342,
    "input_cached_tokens": 229120,
    "input_uncached_tokens": 5560222,
    "output_tokens": 106885,
    "amount_value": 0.9153483,
    "amount_currency": "usd",
    "interpretation": (
        "Custo medido pela API para o projeto no dia da execucao ratio01; "
        "como o export e diario, pode incluir tentativas e smoke tests do mesmo dia."
    ),
}


def build_manifest(project_root: Path) -> dict:
    artifacts = []
    for rel in ARTIFACTS:
        p = project_root / rel
        if not p.is_file():
            artifacts.append({"path": rel, "exists": False})
            continue
        artifacts.append(
            {
                "path": rel,
                "exists": True,
                "size_bytes": p.stat().st_size,
                "sha256": sha256_of_file(p),
            }
        )

    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project": "reprodutibilidade-em-pesquisa / etapa-2",
        "amem_repo": {
            "commit": BASE_AMEM_COMMIT,
            "remote": BASE_AMEM_REMOTE,
            "path": "amem",
        },
        "run_parameters": RUN_PARAMETERS,
        "commands": COMMANDS,
        "api_usage": API_USAGE,
        "observed_runs": OBSERVED_RUNS,
        "artifacts": artifacts,
        "notes": [
            "Results JSONs sao versionados neste repositorio publicado; logs "
            "brutos e caches locais nao foram incluidos.",
            "A execucao ratio01 e a evidencia principal da Etapa 2; a rodada "
            "reduzida foi preservada apenas como historico de comparacao e "
            "auditoria.",
            "Para verificar um artefato: sha256sum <path> e comparar com o "
            "campo sha256 aqui.",
            "Tempos das execucoes pos-correcao e ratio01 vêm dos metadados "
            "dos JSONs de resultado.",
        ],
    }


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent.parent
    manifest = build_manifest(project_root)
    out_path = project_root / "docs/manifest-etapa-2.json"
    out_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    n_ok = sum(1 for a in manifest["artifacts"] if a.get("exists"))
    n_missing = sum(1 for a in manifest["artifacts"] if not a.get("exists"))
    print(f"wrote {out_path}")
    print(f"artefatos: {n_ok} presentes, {n_missing} ausentes")
    print(f"commit amem: {manifest['amem_repo']['commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
