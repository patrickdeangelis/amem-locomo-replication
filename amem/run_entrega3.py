#!/usr/bin/env python3
"""Plan and optionally execute the budget-limited Entrega 3 experiment.

The safe default only writes a deterministic schedule. Passing ``--execute``
is required before any evaluator process (and therefore any API call) starts.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import subprocess
import sys
from pathlib import Path
from typing import Any

from analysis.result_validation import validate_result_payload


K_VALUES = (3, 5, 10)
DEFAULT_SCHEDULE_SEED = 20260714


def _position_imbalance(orders: list[tuple[int, ...]]) -> int:
    counts = [
        [sum(order[position] == k for order in orders) for k in K_VALUES]
        for position in range(len(K_VALUES))
    ]
    return max(max(row) - min(row) for row in counts)


def _balanced_random_orders(replicates: int, rng: random.Random) -> list[tuple[int, ...]]:
    permutations = list(itertools.permutations(K_VALUES))
    orders: list[tuple[int, ...]] = []

    full_pools, remainder = divmod(replicates, len(permutations))
    for _ in range(full_pools):
        pool = permutations.copy()
        rng.shuffle(pool)
        orders.extend(pool)

    if remainder:
        candidates = list(itertools.combinations(permutations, remainder))
        best_score = min(_position_imbalance(list(candidate)) for candidate in candidates)
        best = [
            list(candidate)
            for candidate in candidates
            if _position_imbalance(list(candidate)) == best_score
        ]
        selected = rng.choice(best)
        rng.shuffle(selected)
        orders.extend(selected)

    return orders


def build_schedule(
    *, replicates: int = 5, schedule_seed: int = DEFAULT_SCHEDULE_SEED
) -> dict[str, Any]:
    if replicates < 1:
        raise ValueError("replicates must be at least 1")

    rng = random.Random(schedule_seed)
    runs: list[dict[str, Any]] = []
    orders = _balanced_random_orders(replicates, rng)
    for replicate_number, order in enumerate(orders, start=1):
        replicate_id = f"R{replicate_number}"
        for position, retrieve_k in enumerate(order, start=1):
            runs.append(
                {
                    "replicate_id": replicate_id,
                    "replicate_number": replicate_number,
                    "position": position,
                    "retrieve_k": retrieve_k,
                    "run_seed": schedule_seed + replicate_number,
                    "schedule_seed": schedule_seed,
                    "cache_namespace": f"entrega3_{replicate_id.lower()}",
                    "output": (
                        "results/entrega3/"
                        f"results_amem_gpt4omini_sample0_{replicate_id.lower()}_k{retrieve_k}.json"
                    ),
                }
            )

    return {
        "schema_version": 1,
        "study_scope": "LoCoMo sample 0 only",
        "schedule_seed": schedule_seed,
        "replicates": replicates,
        "k_values": list(K_VALUES),
        "runs": runs,
    }


def build_command(
    run: dict[str, Any], *, python_executable: str = sys.executable
) -> list[str]:
    return [
        python_executable,
        "test_advanced_robust.py",
        "--backend",
        "openai",
        "--model",
        "gpt-4o-mini",
        "--dataset",
        "data/locomo10.json",
        "--ratio",
        "0.1",
        "--retrieve_k",
        str(run["retrieve_k"]),
        "--seed",
        str(run["run_seed"]),
        "--temperature",
        "0.0",
        "--temperature_c5",
        "0.5",
        "--replicate-id",
        str(run["replicate_id"]),
        "--schedule-seed",
        str(run["schedule_seed"]),
        "--schedule-position",
        str(run["position"]),
        "--cache-namespace",
        str(run["cache_namespace"]),
        "--output",
        str(run["output"]),
    ]


def classify_existing_result(run: dict[str, Any]) -> str:
    path = Path(run["output"])
    if not path.is_file():
        return "missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_result_payload(data, expected_run=run)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return "invalid"
    return "valid"


def write_schedule(schedule: dict[str, Any], output: Path) -> None:
    if output.is_file():
        try:
            existing = json.loads(output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise ValueError(f"existing schedule is invalid: {output}") from None
        if existing != schedule:
            raise ValueError(
                f"existing schedule differs from the deterministic plan: {output}"
            )
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(schedule, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def select_runs(
    schedule: dict[str, Any],
    *,
    replicate_ids: list[str] | None = None,
    max_runs: int | None = None,
) -> list[dict[str, Any]]:
    if max_runs is not None and max_runs < 1:
        raise ValueError("max_runs must be at least 1")

    runs = list(schedule["runs"])
    if replicate_ids:
        known = {run["replicate_id"] for run in runs}
        unknown = sorted(set(replicate_ids) - known)
        if unknown:
            raise ValueError(f"unknown replicate_id: {', '.join(unknown)}")
        selected = set(replicate_ids)
        runs = [run for run in runs if run["replicate_id"] in selected]

    return runs[:max_runs] if max_runs is not None else runs


def build_execution_environment(
    project_root: Path, base_environment: dict[str, str] | None = None
) -> dict[str, str]:
    environment = dict(base_environment if base_environment is not None else os.environ)
    cache_root = project_root.resolve() / ".cache"
    environment.setdefault("HF_HOME", str(cache_root / "huggingface"))
    environment.setdefault("MPLCONFIGDIR", str(cache_root / "matplotlib"))
    environment.setdefault("NLTK_DATA", str(cache_root / "nltk"))
    return environment


def execute_schedule(
    schedule: dict[str, Any],
    *,
    python_executable: str,
    force: bool = False,
    replicate_ids: list[str] | None = None,
    max_runs: int | None = None,
) -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(".env.local")
    except ImportError:
        pass

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set; execution was not started")

    environment = build_execution_environment(Path.cwd())
    for variable in ("HF_HOME", "MPLCONFIGDIR", "NLTK_DATA"):
        Path(environment[variable]).mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            python_executable,
            "-m",
            "nltk.downloader",
            "-d",
            environment["NLTK_DATA"],
            "punkt",
            "punkt_tab",
            "wordnet",
        ],
        check=True,
        env=environment,
    )

    runs = select_runs(
        schedule, replicate_ids=replicate_ids, max_runs=max_runs
    )
    print(f"Execution selection: {len(runs)} of {len(schedule['runs'])} scheduled runs")
    for run in runs:
        state = classify_existing_result(run)
        if state == "valid" and not force:
            print(f"SKIP valid result: {run['output']}")
            continue
        if state == "invalid" and not force:
            raise RuntimeError(
                f"Refusing to overwrite invalid/mismatched result: {run['output']}"
            )

        Path(run["output"]).parent.mkdir(parents=True, exist_ok=True)
        command = build_command(run, python_executable=python_executable)
        print("RUN", " ".join(command))
        subprocess.run(command, check=True, env=environment)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=5)
    parser.add_argument("--schedule-seed", type=int, default=DEFAULT_SCHEDULE_SEED)
    parser.add_argument(
        "--schedule-output",
        type=Path,
        default=Path("commands/entrega3_schedule.json"),
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run the scheduled evaluator commands. Without this flag, only plan.",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--replicate-id",
        action="append",
        help="Execute only this replicate; repeat the option to select more than one.",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        help="Execute at most this many selected runs, preserving schedule order.",
    )
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    schedule = build_schedule(
        replicates=args.replicates, schedule_seed=args.schedule_seed
    )
    write_schedule(schedule, args.schedule_output)
    print(f"Schedule written to {args.schedule_output} ({len(schedule['runs'])} runs)")

    if not args.execute:
        print("Planning only: no evaluator process or API call was started.")
        return 0

    execute_schedule(
        schedule,
        python_executable=args.python,
        force=args.force,
        replicate_ids=args.replicate_id,
        max_runs=args.max_runs,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
