#!/usr/bin/env python3
"""Summarize A-Mem evaluation results.

Reads one or more `results_*.json` files produced by `test_advanced_robust.py`
and produces a markdown report with:

  1. Overall aggregate metrics per file (with bootstrap 95% CI for the mean).
  2. Per-category breakdown per file.
  3. Per-question table per file.
  4. Paired deltas between files, matched by question text (e.g. k3 vs k10),
     including the mean paired delta and its bootstrap 95% CI, plus counts of
     improved / regressed / unchanged questions.
  5. Qualitative error analysis: worst-scoring questions, exact-match
     failures, and per-category error patterns.

The script is robust to JSONs without a `metadata` block (the existing Etapa 2
runs predate that block) and to JSONs that include it (future runs).

Usage:
    python analysis/summarize_results.py results/a.json results/b.json ...
    python analysis/summarize_results.py results/*.json --output report.md
    python analysis/summarize_results.py results/*.json --pairs 0:1 0:2 1:2 \
        --output report.md

Bootstrap CIs use a fixed seed (default 0) so the report is reproducible.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Iterable

import numpy as np


# Metrics surfaced in the summary tables, in display order.
PRIMARY_METRICS = [
    "exact_match",
    "f1",
    "bleu1",
    "rouge1_f",
    "meteor",
    "sbert_similarity",
]

CATEGORY_NAMES = {
    1: "1 (single-hop)",
    2: "2 (temporal)",
    3: "3 (multi-hop)",
    4: "4 (open-ended)",
    5: "5 (adversarial / unanswerable)",
}


def _load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["_file"] = path.name
    data["_file_path"] = str(path)
    return data


def _label(data: dict) -> str:
    """Short human label for a result file, robust to missing metadata."""
    meta = data.get("metadata", {}) or {}
    k = meta.get("retrieve_k")
    if k is None:
        # Fall back to parsing k from the filename (e.g. ..._k10.json).
        name = data["_file"]
        for tok in name.replace(".json", "").split("_"):
            if tok.startswith("k") and tok[1:].isdigit():
                k = tok[1:]
                break
    if k is not None:
        return f"k={k}"
    return data["_file"]


def _retrieve_k(data: dict) -> int | None:
    meta = data.get("metadata", {}) or {}
    k = meta.get("retrieve_k")
    if k is not None:
        return int(k)
    for tok in data["_file"].replace(".json", "").split("_"):
        if tok.startswith("k") and tok[1:].isdigit():
            return int(tok[1:])
    return None


def _overall_mean(data: dict, metric: str) -> float:
    return data["aggregate_metrics"]["overall"][metric]["mean"]


def _per_question_metric(individual: list[dict], metric: str) -> np.ndarray:
    return np.array(
        [float(r["metrics"].get(metric, 0.0)) for r in individual],
        dtype=float,
    )


def bootstrap_mean_ci(
    values: np.ndarray,
    n_boot: int = 10000,
    confidence: float = 0.95,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Return (mean, ci_low, ci_high) for the mean of `values` via bootstrap.

    If `values` is empty, returns (nan, nan, nan).
    """
    if values.size == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    n = values.size
    mean = float(values.mean())
    if n == 1:
        return mean, mean, mean
    idx = rng.integers(0, n, size=(n_boot, n))
    boot_means = values[idx].mean(axis=1)
    alpha = (1.0 - confidence) / 2.0
    lo = float(np.quantile(boot_means, alpha))
    hi = float(np.quantile(boot_means, 1.0 - alpha))
    return mean, lo, hi


def bootstrap_paired_delta_ci(
    a: np.ndarray,
    b: np.ndarray,
    n_boot: int = 10000,
    confidence: float = 0.95,
    seed: int = 0,
) -> tuple[float, float, float, int, int, int]:
    """Bootstrap CI for the mean of (b - a) on matched questions.

    Returns (mean_delta, ci_low, ci_high, n_improved, n_regressed, n_unchanged).
    `n_improved` counts questions where b > a by more than 1e-9, etc.
    """
    assert a.shape == b.shape, "paired delta requires matched arrays"
    diffs = b - a
    mean_delta = float(diffs.mean())
    rng = np.random.default_rng(seed)
    n = diffs.size
    if n == 0:
        return float("nan"), float("nan"), float("nan"), 0, 0, 0
    if n == 1:
        return mean_delta, mean_delta, mean_delta, 0, 0, 0
    idx = rng.integers(0, n, size=(n_boot, n))
    boot = diffs[idx].mean(axis=1)
    alpha = (1.0 - confidence) / 2.0
    lo = float(np.quantile(boot, alpha))
    hi = float(np.quantile(boot, 1.0 - alpha))
    eps = 1e-9
    improved = int((diffs > eps).sum())
    regressed = int((diffs < -eps).sum())
    unchanged = int((abs(diffs) <= eps).sum())
    return mean_delta, lo, hi, improved, regressed, unchanged


def _fmt(x: float, digits: int = 4) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x:.{digits}f}"


def _ci_str(lo: float, hi: float, digits: int = 4) -> str:
    return f"[{_fmt(lo, digits)}, {_fmt(hi, digits)}]"


def _range_str(lo: float, hi: float, digits: int = 4) -> str:
    return f"{_fmt(lo, digits)} a {_fmt(hi, digits)}"


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------


def section_overview(datasets: list[dict], out) -> None:
    out.write("## Visao geral\n\n")
    out.write(
        "Metricas agregadas (media) por arquivo, com intervalo de confianca "
        "bootstrap de 95% para a media (10.000 reamostragens, seed=0).\n\n"
    )
    header = "| arquivo | k | perguntas | " + " | ".join(PRIMARY_METRICS) + " |"
    sep = "|" + "---|" * (3 + len(PRIMARY_METRICS))
    out.write(header + "\n")
    out.write(sep + "\n")
    for d in datasets:
        cells = [d["_file"], str(_retrieve_k(d)), str(d["total_questions"])]
        for m in PRIMARY_METRICS:
            vals = _per_question_metric(d["individual_results"], m)
            mean, lo, hi = bootstrap_mean_ci(vals, seed=0)
            cells.append(f"{_fmt(mean)} {_ci_str(lo, hi)}")
        out.write("| " + " | ".join(cells) + " |\n")
    out.write("\n")


def section_per_category(datasets: list[dict], out) -> None:
    out.write("## Analise por categoria\n\n")
    out.write(
        "Cada categoria do LoCoMo tem poucas perguntas nesta execucao, entao "
        "as medias por categoria tem alta variancia. Use como indicador "
        "qualitativo, nao como estimativa robusta.\n\n"
    )
    for d in datasets:
        out.write(f"### {_label(d)} (`{d['_file']}`)\n\n")
        agg = d["aggregate_metrics"]
        # Discover categories present (skip 'overall').
        cats = sorted(
            int(k.split("_")[1])
            for k in agg
            if k.startswith("category_") and k.split("_")[1].isdigit()
        )
        header = "| categoria | n | " + " | ".join(PRIMARY_METRICS) + " |"
        sep = "|" + "---|" * (2 + len(PRIMARY_METRICS))
        out.write(header + "\n")
        out.write(sep + "\n")
        for c in cats:
            key = f"category_{c}"
            if key not in agg:
                continue
            n = agg[key].get("f1", {}).get("count", "?")
            cells = [CATEGORY_NAMES.get(c, str(c)), str(n)]
            for m in PRIMARY_METRICS:
                mean = agg[key].get(m, {}).get("mean", float("nan"))
                cells.append(_fmt(mean))
            out.write("| " + " | ".join(cells) + " |\n")
        out.write("\n")


def section_per_question(datasets: list[dict], out, top: int = 5) -> None:
    out.write("## Analise por pergunta (piores e melhores)\n\n")
    out.write(
        f"Para cada arquivo, as {top} perguntas com menor F1 e as {top} com maior "
        "F1. Util para inspecao qualitativa de erros.\n\n"
    )
    for d in datasets:
        out.write(f"### {_label(d)} (`{d['_file']}`)\n\n")
        indiv = sorted(d["individual_results"], key=lambda r: r["metrics"]["f1"])
        out.write(
            "| rank | categoria | F1 | exact | predicao | referencia | pergunta |\n"
        )
        out.write("|---|---|---|---|---|---|---|\n")
        rows = indiv[:top] + list(reversed(indiv[-top:]))
        for i, r in enumerate(rows, 1):
            q = r["question"][:80].replace("|", "/")
            pred = str(r["prediction"])[:60].replace("|", "/").replace("\n", " ")
            ref = str(r["reference"])[:60].replace("|", "/").replace("\n", " ")
            out.write(
                f"| {i} | {r['category']} | {_fmt(r['metrics']['f1'])} | "
                f"{r['metrics']['exact_match']} | {pred} | {ref} | {q} |\n"
            )
        out.write("\n")


def section_qualitative(datasets: list[dict], out) -> None:
    out.write("## Analise qualitativa de erros\n\n")
    out.write(
        "Falhas de exact match por arquivo, com a predicao e a referencia. "
        "Para categoria 5 (adversarial), uma predicao 'Not mentioned in the "
        "conversation' conta como acerto quando a referencia tambem e essa.\n\n"
    )
    for d in datasets:
        out.write(f"### {_label(d)} (`{d['_file']}`)\n\n")
        fails = [r for r in d["individual_results"] if r["metrics"]["exact_match"] == 0]
        out.write(f"- total de perguntas: {d['total_questions']}\n")
        out.write(f"- falhas de exact match: {len(fails)}\n")
        if not fails:
            continue
        out.write("\n| cat | F1 | predicao | referencia | pergunta |\n")
        out.write("|---|---|---|---|---|\n")
        # Sort by F1 ascending so the worst failures come first.
        for r in sorted(fails, key=lambda r: r["metrics"]["f1"])[:15]:
            q = str(r["question"])[:70].replace("|", "/")
            pred = str(r["prediction"])[:50].replace("|", "/").replace("\n", " ")
            ref = str(r["reference"])[:50].replace("|", "/").replace("\n", " ")
            out.write(
                f"| {r['category']} | {_fmt(r['metrics']['f1'])} | {pred} | {ref} | {q} |\n"
            )
        out.write("\n")

    # Per-category error pattern across files.
    out.write("### Padroes de erro por categoria (consolidado)\n\n")
    out.write(
        "| categoria | descricao | n total | media F1 (min-max entre arquivos) |\n"
    )
    out.write("|---|---|---|---|\n")
    # Union of categories across files.
    all_cats: set[int] = set()
    for d in datasets:
        agg = d["aggregate_metrics"]
        for k in agg:
            if k.startswith("category_") and k.split("_")[1].isdigit():
                all_cats.add(int(k.split("_")[1]))
    for c in sorted(all_cats):
        means = []
        n_total = 0
        for d in datasets:
            agg = d["aggregate_metrics"]
            key = f"category_{c}"
            if key in agg:
                means.append(agg[key]["f1"]["mean"])
                n_total = max(n_total, agg[key]["f1"].get("count", 0))
        lo = min(means) if means else float("nan")
        hi = max(means) if means else float("nan")
        out.write(
            f"| {c} | {CATEGORY_NAMES.get(c, str(c))} | {n_total} | "
            f"{_range_str(lo, hi)} |\n"
        )
    out.write("\n")


def section_paired_deltas(
    datasets: list[dict], out, pairs: list[tuple[int, int]]
) -> None:
    if not pairs:
        return
    out.write("## Deltas pareados por pergunta\n\n")
    out.write(
        "Para cada par (A para B), o diff corresponde a metrica(B) menos "
        "metrica(A) em cada pergunta emparelhada por texto. IC bootstrap de "
        "95% para a media do diff "
        "(10.000 reamostragens, seed=0). Como a execucao cobre apenas uma "
        "amostra do LoCoMo, os IC devem ser lidos como direcao, nao como teste "
        "formal.\n\n"
    )
    # Build question -> index map per file.
    qmaps = []
    for d in datasets:
        m = {}
        for i, r in enumerate(d["individual_results"]):
            m.setdefault(r["question"], i)
        qmaps.append(m)
    for ai, bi in pairs:
        if ai >= len(datasets) or bi >= len(datasets):
            out.write(f"- par {ai} para {bi}: indices fora do intervalo\n")
            continue
        a, b = datasets[ai], datasets[bi]
        common = [q for q in qmaps[ai] if q in qmaps[bi]]
        out.write(
            f"### {_label(a)} para {_label(b)} ({len(common)} perguntas emparelhadas)\n\n"
        )
        if not common:
            out.write("- sem perguntas em comum para emparelhar.\n\n")
            continue
        out.write("| metrica | diff medio | IC 95% | melhorou | piorou | igual |\n")
        out.write("|---|---|---|---|---|---|\n")
        for m in PRIMARY_METRICS:
            av = np.array(
                [a["individual_results"][qmaps[ai][q]]["metrics"][m] for q in common],
                dtype=float,
            )
            bv = np.array(
                [b["individual_results"][qmaps[bi][q]]["metrics"][m] for q in common],
                dtype=float,
            )
            delta, lo, hi, imp, reg, unch = bootstrap_paired_delta_ci(av, bv, seed=0)
            out.write(
                f"| {m} | {_fmt(delta)} | {_ci_str(lo, hi)} | {imp} | {reg} | {unch} |\n"
            )
        out.write("\n")


def section_reproducibility(datasets: list[dict], out) -> None:
    out.write("## Rastreabilidade\n\n")
    with_meta = [d for d in datasets if d.get("metadata")]
    without_meta = [d for d in datasets if not d.get("metadata")]
    if without_meta and not with_meta:
        out.write(
            "Nenhum dos arquivos possui bloco de metadados: eles foram gerados "
            "antes da inclusao desse bloco no script. A rastreabilidade vem do "
            "`manifest-etapa-2.json`.\n\n"
        )
    elif with_meta and not without_meta:
        out.write(
            "Todos os arquivos possuem bloco de metadados registrado no proprio "
            "JSON (seed, temperaturas, retrieve_k, hash do dataset, commit, "
            "comando, timestamps e duracao).\n\n"
        )
    elif with_meta and without_meta:
        out.write(
            f"{len(with_meta)} arquivo(s) com bloco de metadados e "
            f"{len(without_meta)} sem. Os sem metadados foram gerados antes da "
            "inclusao desse bloco; a rastreabilidade deles vem do "
            "`manifest-etapa-2.json`.\n\n"
        )
    out.write(
        "| arquivo | seed | temp. (cat 1-4) | temp_c5 | retrieve_k | commit | dataset_sha256 |\n"
    )
    out.write("|---|---|---|---|---|---|---|\n")
    for d in datasets:
        m = d.get("metadata", {}) or {}
        sha = m.get("dataset_sha256", "")
        sha_short = sha[:12] if sha else "n/a"
        out.write(
            f"| {d['_file']} | {m.get('seed', 'n/a')} | "
            f"{m.get('temperature_answer', 'n/a')} | "
            f"{m.get('temperature_c5', 'n/a')} | "
            f"{m.get('retrieve_k', _retrieve_k(d))} | "
            f"{(m.get('repo_commit') or 'n/a')[:12]} | {sha_short} |\n"
        )
    out.write("\n")


def _scope_summary(datasets: list[dict]) -> str:
    first = datasets[0]
    meta = first.get("metadata", {}) or {}
    total_questions = first.get("total_questions", len(first.get("individual_results", [])))
    sample_ids = sorted(
        {
            r.get("sample_id")
            for r in first.get("individual_results", [])
            if r.get("sample_id") is not None
        }
    )
    sample_text = (
        f"{len(sample_ids)} sample(s): {', '.join(map(str, sample_ids))}"
        if sample_ids
        else "sample(s) nao registrados"
    )
    dataset = Path(meta.get("dataset_path", first.get("dataset", "dataset"))).name
    ratio = meta.get("ratio")
    ratio_text = f" com --ratio {ratio}" if ratio is not None else ""
    return f"{total_questions} perguntas em {sample_text} de {dataset}{ratio_text}"


def _threats_to_validity(datasets: list[dict], out) -> None:
    first = datasets[0]
    meta = first.get("metadata", {}) or {}
    total_questions = first.get("total_questions", len(first.get("individual_results", [])))
    sample_ids = sorted(
        {
            r.get("sample_id")
            for r in first.get("individual_results", [])
            if r.get("sample_id") is not None
        }
    )
    ratio = meta.get("ratio")
    temp_answer = meta.get("temperature_answer", "n/a")
    temp_c5 = meta.get("temperature_c5", "n/a")
    cache_dir = meta.get("memories_cache_dir", "cache nao registrado")

    out.write("\n## Ameacas a validade\n\n")
    if sample_ids:
        out.write(
            f"- A execucao cobre {len(sample_ids)} sample(s) "
            f"({', '.join(map(str, sample_ids))})"
        )
    else:
        out.write("- A execucao cobre uma amostra reduzida")
    if ratio is not None:
        out.write(f" selecionada por `--ratio {ratio}`")
    out.write(
        "; portanto, nao estima o desempenho geral do A-Mem em todos os "
        "dialogos do LoCoMo.\n"
    )
    out.write(
        f"- {total_questions} perguntas produzem IC bootstrap informativos para "
        "esta amostra, mas perguntas do mesmo sample/dialogo nao sao "
        "independentes; os IC podem subestimar a incerteza entre dialogos.\n"
    )
    out.write(
        f"- A avaliacao usou `temperature_answer={temp_answer}` e "
        f"`temperature_c5={temp_c5}`. Mesmo com seed registrada, chamadas a API "
        "hospedada podem variar em reexecucoes futuras.\n"
    )
    out.write(
        f"- O cache de memorias `{cache_dir}` foi reutilizado entre valores de k; "
        "isso isola a variacao de `retrieve_k`, mas uma reexecucao fria pode "
        "divergir se modelo/API/dependencias mudarem.\n"
    )


def build_report(paths: list[Path], pairs: list[tuple[int, int]], out) -> None:
    datasets = [_load(p) for p in paths]
    out.write("# Analise dos resultados da Etapa 2\n\n")
    out.write(
        "Relatorio gerado por `analysis/summarize_results.py` a partir dos "
        f"{len(datasets)} arquivos de resultado listados. As medias por "
        f"categoria e por pergunta sao calculadas sobre {_scope_summary(datasets)}. "
        "Elas descrevem a execucao planejada desta Entrega 2 e nao devem ser "
        "extrapoladas para todo o LoCoMo.\n\n"
    )
    section_overview(datasets, out)
    section_per_category(datasets, out)
    section_per_question(datasets, out)
    section_qualitative(datasets, out)
    section_paired_deltas(datasets, out, pairs)
    section_reproducibility(datasets, out)
    _threats_to_validity(datasets, out)


def _parse_pairs(specs: list[str]) -> list[tuple[int, int]]:
    pairs = []
    for s in specs:
        if ":" not in s:
            raise SystemExit(f"par invalido '{s}', use o formato A:B (indices)")
        a, b = s.split(":", 1)
        pairs.append((int(a), int(b)))
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize A-Mem evaluation results with per-category, "
        "per-question, paired-delta and qualitative analysis."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Arquivos results_*.json produzidos por test_advanced_robust.py",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Arquivo markdown de saida (default: stdout).",
    )
    parser.add_argument(
        "--pairs",
        nargs="*",
        default=["0:1", "0:2", "1:2"],
        help="Pares de indices A:B para delta pareado (default: 0:1 0:2 1:2).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Numero de melhores/piores perguntas por arquivo (default: 5).",
    )
    args = parser.parse_args()

    paths = [Path(p) for p in args.files]
    for p in paths:
        if not p.is_file():
            print(f"arquivo nao encontrado: {p}", file=sys.stderr)
            return 2

    pairs = _parse_pairs(args.pairs)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            build_report(paths, pairs, fh)
        print(f"relatorio escrito em {out_path}")
    else:
        import io

        buf = io.StringIO()
        build_report(paths, pairs, buf)
        print(buf.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
