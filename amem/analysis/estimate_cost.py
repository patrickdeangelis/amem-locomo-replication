#!/usr/bin/env python3
"""Estimate cost and wall-clock time for A-Mem evaluations on the LoCoMo
dataset, calibrated against the observed reduced run of Etapa 2.

This is an *estimator*, not a quote. It decomposes the pipeline into two
rate-limited phases and projects them to a target dataset size using rates
measured during the Etapa 2 reduced run (35 turns / 20 questions / 1 sample).

Phases:
  1. Cold memory creation: one LLM-driven extraction per conversation turn
     (memory content, context, keywords, tags). Cached on disk and reused
     across k values and across re-runs.
  2. Warm answering: per question, ~3 LLM calls (keyword generation, relevant
     memory selection, answer generation). Repeated once per `retrieve_k`
     value being swept.

Observed calibration points (2026-07-07, gpt-4o-mini, OpenAI API):
  - Smoke min cold: 8 turns + 3 questions in ~74s (includes model warmup).
  - Reduced s2 cold (k=3): 35 turns + 20 questions in ~300s wall.
  - Reduced s2 warm (k=5, k=10): 20 questions in ~60s each (cache reused).

From these we derive (see `OBSERVED` below):
  - cold turn rate ~6.9 s/turn (after subtracting warm answering time)
  - warm question rate ~3.0 s/question
  - ~4 LLM calls per turn during cold creation
  - ~3 LLM calls per question during warm answering

Usage:
    python analysis/estimate_cost.py                       # full locomo10 defaults
    python analysis/estimate_cost.py --questions 1986 --turns 4190 --samples 10
    python analysis/estimate_cost.py --warm-runs 3 --print-md

Pricing defaults reflect gpt-4o-mini (USD per 1M tokens, mid-2024). Override
with --price-in / --price-out if pricing changes.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Observed calibration (Etapa 2 reduced run, 2026-07-07)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ObservedPoint:
    label: str
    turns: int
    questions: int
    wall_seconds: float
    cold: bool  # True if this run created the memory cache


OBSERVED = [
    ObservedPoint("smoke_min_cold", turns=8, questions=3, wall_seconds=74.0, cold=True),
    # Note: smoke_min includes model/SentenceTransformer warmup (~20s), so we
    # do not use it for rate fitting; kept here for transparency.
    ObservedPoint(
        "reduced_s2_cold_k3", turns=35, questions=20, wall_seconds=300.0, cold=True
    ),
    ObservedPoint(
        "reduced_s2_warm_k5", turns=0, questions=20, wall_seconds=60.0, cold=False
    ),
    ObservedPoint(
        "reduced_s2_warm_k10", turns=0, questions=20, wall_seconds=60.0, cold=False
    ),
]

# Derived rates (central estimates).
# From reduced_s2_warm_*: 60s / 20 q = 3.0 s/question (warm answering).
# From reduced_s2_cold_k3: 300s - (20q * 3.0 s/q) = 240s for 35 turns => 6.86 s/turn.
WARM_SECONDS_PER_QUESTION = 60.0 / 20.0
COLD_SECONDS_PER_TURN = (300.0 - 20.0 * WARM_SECONDS_PER_QUESTION) / 35.0

# LLM call counts (central). Memory creation does ~4 calls/turn (content,
# context, keywords, tags). Warm answering does ~3 calls/question (keywords,
# memory selection, answer). These are approximate; the estimator reports a
# range by varying them +/- 25%.
CALLS_PER_TURN_COLD = 4.0
CALLS_PER_QUESTION_WARM = 3.0

# Token estimates per call (central, with range for sensitivity).
TOKENS_IN_PER_CALL = 1500.0  # prompts include retrieved memory context
TOKENS_OUT_PER_CALL = 120.0

# gpt-4o-mini pricing (USD per 1M tokens). Verify before quoting.
PRICE_IN_PER_M = 0.15
PRICE_OUT_PER_M = 0.60

# Full locomo10.json defaults (per resultados-etapa-2.md and load_dataset).
LOCOMO10_TURNS_TOTAL = 4190  # ~419 turns/sample * 10 samples (approx; verify)
LOCOMO10_QUESTIONS_TOTAL = 1986
LOCOMO10_SAMPLES = 10


def fit_rates() -> dict:
    """Return derived rates plus min/max bounds from the observed points."""
    warm_points = [p for p in OBSERVED if not p.cold and p.questions > 0]
    warm_rates = [p.wall_seconds / p.questions for p in warm_points]
    cold_points = [
        p for p in OBSERVED if p.cold and p.turns > 0 and p.label != "smoke_min_cold"
    ]
    cold_rates = [
        (p.wall_seconds - p.questions * WARM_SECONDS_PER_QUESTION) / p.turns
        for p in cold_points
    ]
    return {
        "warm_s_per_q_central": WARM_SECONDS_PER_QUESTION,
        "warm_s_per_q_min": min(warm_rates)
        if warm_rates
        else WARM_SECONDS_PER_QUESTION,
        "warm_s_per_q_max": max(warm_rates)
        if warm_rates
        else WARM_SECONDS_PER_QUESTION,
        "cold_s_per_turn_central": COLD_SECONDS_PER_TURN,
        "cold_s_per_turn_min": min(cold_rates) if cold_rates else COLD_SECONDS_PER_TURN,
        "cold_s_per_turn_max": max(cold_rates) if cold_rates else COLD_SECONDS_PER_TURN,
    }


def fmt_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        return f"{seconds / 60:.1f}min"
    return f"{seconds / 3600:.2f}h"


def estimate(
    questions: int,
    turns: int,
    samples: int,
    warm_runs: int,
    cold: bool,
    price_in_per_m: float,
    price_out_per_m: float,
) -> dict:
    rates = fit_rates()
    # Time. Central estimate from observed rates; bounds from a +/-25% factor
    # that reflects single-sample uncertainty (we only have one cold point and
    # one warm rate, so the observed min/max collapse to a point).
    uncertainty = 0.25
    cold_central = turns * rates["cold_s_per_turn_central"] if cold else 0.0
    warm_central = questions * rates["warm_s_per_q_central"] * warm_runs
    total_central = cold_central + warm_central
    cold_time = cold_central
    warm_time = warm_central
    cold_time_max = cold_central * (1 + uncertainty) if cold else 0.0
    cold_time_min = cold_central * (1 - uncertainty) if cold else 0.0
    warm_time_max = warm_central * (1 + uncertainty)
    warm_time_min = warm_central * (1 - uncertainty)
    total_time = total_central

    # Tokens (central). Cold: calls_per_turn * turns. Warm: calls_per_q * questions * warm_runs.
    calls_cold = CALLS_PER_TURN_COLD * turns if cold else 0.0
    calls_warm = CALLS_PER_QUESTION_WARM * questions * warm_runs
    calls_total = calls_cold + calls_warm
    tokens_in = calls_total * TOKENS_IN_PER_CALL
    tokens_out = calls_total * TOKENS_OUT_PER_CALL
    # Range: vary calls +/- 25%.
    factor_lo, factor_hi = 0.75, 1.25
    tokens_in_lo = tokens_in * factor_lo
    tokens_in_hi = tokens_in * factor_hi
    tokens_out_lo = tokens_out * factor_lo
    tokens_out_hi = tokens_out * factor_hi

    cost_central = tokens_in / 1e6 * price_in_per_m + tokens_out / 1e6 * price_out_per_m
    cost_lo = (
        tokens_in_lo / 1e6 * price_in_per_m + tokens_out_lo / 1e6 * price_out_per_m
    )
    cost_hi = (
        tokens_in_hi / 1e6 * price_in_per_m + tokens_out_hi / 1e6 * price_out_per_m
    )

    return {
        "rates": rates,
        "time": {
            "cold_central": cold_time,
            "cold_min": cold_time_min,
            "cold_max": cold_time_max,
            "warm_central": warm_time,
            "warm_min": warm_time_min,
            "warm_max": warm_time_max,
            "total_central": total_time,
            "total_min": cold_time_min + warm_time_min,
            "total_max": cold_time_max + warm_time_max,
        },
        "tokens": {
            "calls_cold": calls_cold,
            "calls_warm": calls_warm,
            "tokens_in_central": tokens_in,
            "tokens_out_central": tokens_out,
            "tokens_in_range": (tokens_in_lo, tokens_in_hi),
            "tokens_out_range": (tokens_out_lo, tokens_out_hi),
        },
        "cost": {
            "central": cost_central,
            "low": cost_lo,
            "high": cost_hi,
            "price_in_per_m": price_in_per_m,
            "price_out_per_m": price_out_per_m,
        },
    }


def print_report(target_label: str, params: dict, est: dict, md: bool) -> None:
    t = est["time"]
    tok = est["tokens"]
    c = est["cost"]
    r = est["rates"]
    bullet = "-" if not md else "-"
    if md:
        print(f"## Estimativa de custo/tempo - {target_label}\n")
    else:
        print(f"Estimativa de custo/tempo - {target_label}")
        print("=" * 60)
    print(f"{bullet} perguntas alvo: {params['questions']}")
    print(f"{bullet} turns alvo: {params['turns']}")
    print(f"{bullet} samples alvo: {params['samples']}")
    print(f"{bullet} runs warm (varredura de k): {params['warm_runs']}")
    print(f"{bullet} inclui criacao de cache (cold): {params['cold']}\n")

    print("Calibracao observada (Etapa 2 reduced, gpt-4o-mini):")
    for p in OBSERVED:
        print(
            f"  {bullet} {p.label}: {p.turns}t/{p.questions}q em {p.wall_seconds:.0f}s cold={p.cold}"
        )
    print(
        f"\nTaxas derivadas:\n"
        f"  {bullet} cold: {r['cold_s_per_turn_central']:.2f} s/turn "
        f"[{r['cold_s_per_turn_min']:.2f}, {r['cold_s_per_turn_max']:.2f}]\n"
        f"  {bullet} warm: {r['warm_s_per_q_central']:.2f} s/question "
        f"[{r['warm_s_per_q_min']:.2f}, {r['warm_s_per_q_max']:.2f}]\n"
    )

    print("Tempo estimado (wall-clock, single-thread):")
    print(
        f"  {bullet} cold (cache): {fmt_duration(t['cold_central'])} "
        f"[{fmt_duration(t['cold_min'])}, {fmt_duration(t['cold_max'])}]"
    )
    print(
        f"  {bullet} warm (answering): {fmt_duration(t['warm_central'])} "
        f"[{fmt_duration(t['warm_min'])}, {fmt_duration(t['warm_max'])}]"
    )
    print(
        f"  {bullet} TOTAL: {fmt_duration(t['total_central'])} "
        f"[{fmt_duration(t['total_min'])}, {fmt_duration(t['total_max'])}]\n"
    )

    print("Tokens estimados (central, com faixa +/-25% nas chamadas):")
    print(
        f"  {bullet} chamadas LLM: {tok['calls_cold']:.0f} cold + {tok['calls_warm']:.0f} warm"
    )
    print(
        f"  {bullet} input: {tok['tokens_in_central'] / 1e6:.2f}M "
        f"[{tok['tokens_in_range'][0] / 1e6:.2f}, {tok['tokens_in_range'][1] / 1e6:.2f}]"
    )
    print(
        f"  {bullet} output: {tok['tokens_out_central'] / 1e6:.2f}M "
        f"[{tok['tokens_out_range'][0] / 1e6:.2f}, {tok['tokens_out_range'][1] / 1e6:.2f}]\n"
    )

    print("Custo estimado (USD):")
    print(
        f"  {bullet} precos: ${c['price_in_per_m']}/M in, ${c['price_out_per_m']}/M out"
    )
    print(f"  {bullet} central: ${c['central']:.2f}")
    print(f"  {bullet} faixa: ${c['low']:.2f} - ${c['high']:.2f}\n")

    print("Resumo para decisao:")
    print(
        f"  {bullet} tempo total ~{fmt_duration(t['total_central'])} "
        f"(faixa {fmt_duration(t['total_min'])}-{fmt_duration(t['total_max'])})"
    )
    print(
        f"  {bullet} custo total ~${c['central']:.2f} (faixa ${c['low']:.2f}-${c['high']:.2f})"
    )
    print("\nAviso: estimativa baseada em 1 amostra reduzida; incerteza e alta.")
    print("Antes de rodar o dataset completo, considere rodar 1 sample inteiro")
    print("(419 turns, 199 questions) para revalidar as taxas.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estimate cost/time for A-Mem LoCoMo evaluations."
    )
    parser.add_argument("--questions", type=int, default=LOCOMO10_QUESTIONS_TOTAL)
    parser.add_argument("--turns", type=int, default=LOCOMO10_TURNS_TOTAL)
    parser.add_argument("--samples", type=int, default=LOCOMO10_SAMPLES)
    parser.add_argument(
        "--warm-runs",
        type=int,
        default=3,
        help="Numero de runs warm (ex: 3 para varredura k=3,5,10).",
    )
    parser.add_argument(
        "--cold",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Inclui criacao de cache (default: True). Use --no-cold se o cache ja existe.",
    )
    parser.add_argument("--price-in", type=float, default=PRICE_IN_PER_M)
    parser.add_argument("--price-out", type=float, default=PRICE_OUT_PER_M)
    parser.add_argument("--print-md", action="store_true", help="Saida em markdown.")
    parser.add_argument(
        "--target",
        type=str,
        default="locomo10.json (dataset completo)",
        help="Descricao do alvo para o cabecalho do relatorio.",
    )
    args = parser.parse_args()

    params = {
        "questions": args.questions,
        "turns": args.turns,
        "samples": args.samples,
        "warm_runs": args.warm_runs,
        "cold": args.cold,
    }
    est = estimate(
        questions=args.questions,
        turns=args.turns,
        samples=args.samples,
        warm_runs=args.warm_runs,
        cold=args.cold,
        price_in_per_m=args.price_in,
        price_out_per_m=args.price_out,
    )
    print_report(args.target, params, est, md=args.print_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
