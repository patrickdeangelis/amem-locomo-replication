import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import test_advanced_robust as evaluator


def snapshot(
    requests,
    input_tokens,
    cached,
    output,
    total,
    model="gpt-4o-mini",
    attempts_total=None,
    failed_attempts=0,
):
    return {
        "requests": requests,
        "attempts_total": requests if attempts_total is None else attempts_total,
        "failed_attempts": failed_attempts,
        "input_tokens": input_tokens,
        "cached_input_tokens": cached,
        "output_tokens": output,
        "total_tokens": total,
        "model": model,
    }


def test_cache_namespace_is_safe_separate_and_optional(tmp_path, monkeypatch):
    dataset = tmp_path / "dataset.json"
    dataset.write_text('{"sample": 1}', encoding="utf-8")
    monkeypatch.setattr(evaluator, "__file__", str(tmp_path / "evaluator.py"))

    legacy_compatible = evaluator.resolve_memories_dir(
        "openai", "gpt-4o-mini", str(dataset)
    )
    block_a = evaluator.resolve_memories_dir(
        "openai", "gpt-4o-mini", str(dataset), cache_namespace="block-a"
    )
    block_b = evaluator.resolve_memories_dir(
        "openai", "gpt-4o-mini", str(dataset), cache_namespace="block-b"
    )

    assert Path(legacy_compatible).name.startswith(
        "cached_memories_robust_openai_gpt-4o-mini_dataset_"
    )
    assert Path(block_a).name.endswith("_ns-block-a")
    assert Path(block_b).name.endswith("_ns-block-b")
    assert len({legacy_compatible, block_a, block_b}) == 3
    with pytest.raises(ValueError, match="cache namespace"):
        evaluator.resolve_memories_dir(
            "openai", "gpt-4o-mini", str(dataset), cache_namespace="../escape"
        )


def test_usage_helpers_combine_diff_and_estimate_phase_costs():
    before = evaluator.combine_usage_snapshots(
        [snapshot(1, 100, 20, 10, 110), snapshot(2, 200, 30, 20, 220)]
    )
    after = evaluator.combine_usage_snapshots(
        [
            snapshot(2, 600_100, 200_020, 50_010, 650_110),
            snapshot(3, 400_200, 200_030, 50_020, 450_220),
        ]
    )

    phase = evaluator.diff_usage_snapshots(after, before)
    assert phase == snapshot(2, 1_000_000, 400_000, 100_000, 1_100_000)
    assert evaluator.estimate_usage_cost_usd(phase) == pytest.approx(0.18)


def test_agent_snapshot_aggregates_both_openai_controllers():
    class Controller:
        def __init__(self, current):
            self.current = current

        def get_usage_snapshot(self):
            return self.current

    agent = SimpleNamespace(
        memory_system=SimpleNamespace(
            llm_controller=SimpleNamespace(
                llm=Controller(snapshot(2, 100, 10, 20, 120))
            )
        ),
        retriever_llm=SimpleNamespace(
            llm=Controller(snapshot(3, 200, 20, 30, 230))
        ),
    )

    assert evaluator.get_agent_usage_snapshot(agent, "gpt-4o-mini") == snapshot(
        5, 300, 30, 50, 350
    )


def test_tracking_metadata_contains_run_identity_phases_total_and_prices():
    memory_build = snapshot(2, 1_000, 200, 100, 1_100)
    evaluation = snapshot(3, 2_000, 500, 300, 2_300)

    tracking = evaluator.build_run_tracking_metadata(
        replicate_id="r03",
        schedule_seed=47,
        cache_namespace="block-03",
        memory_build=memory_build,
        evaluation=evaluation,
        schedule_position=2,
        sample_ids=[0],
    )

    assert tracking["replicate_id"] == "r03"
    assert tracking["schedule_seed"] == 47
    assert tracking["cache_namespace"] == "block-03"
    assert tracking["schedule_position"] == 2
    assert tracking["sample_ids"] == [0]
    assert tracking["usage"]["memory_build"]["requests"] == 2
    assert tracking["usage"]["evaluation"]["requests"] == 3
    assert tracking["usage"]["total"] == {
        **snapshot(5, 3_000, 700, 400, 3_400),
        "estimated_cost_usd": pytest.approx(0.0006375),
    }
    assert tracking["usage"]["pricing_usd_per_million"] == {
        "input_tokens": 0.15,
        "cached_input_tokens": 0.075,
        "output_tokens": 0.60,
    }
    assert tracking["usage"]["pricing_metadata"] == {
        "as_of": "2026-07-14",
        "currency": "USD",
        "source_url": "https://openai.com/api/pricing/",
    }
    assert json.loads(json.dumps(tracking))["replicate_id"] == "r03"


def test_cli_accepts_run_identity_options():
    args = evaluator.build_argument_parser().parse_args(
        [
            "--replicate-id",
            "r02",
            "--schedule-seed",
            "99",
            "--cache-namespace",
            "block-02",
            "--schedule-position",
            "3",
        ]
    )

    assert args.replicate_id == "r02"
    assert args.schedule_seed == 99
    assert args.cache_namespace == "block-02"
    assert args.schedule_position == 3


def test_worktree_provenance_hashes_code_and_records_dirty_state(tmp_path, monkeypatch):
    evaluator_file = tmp_path / "test_advanced_robust.py"
    evaluator_file.write_text("print('test')\n", encoding="utf-8")
    (tmp_path / "memory_layer_robust.py").write_text("VALUE = 1\n", encoding="utf-8")
    monkeypatch.setattr(
        evaluator.subprocess,
        "check_output",
        lambda *args, **kwargs: b" M memory_layer_robust.py\n",
    )

    provenance = evaluator.git_worktree_provenance(str(tmp_path))

    assert provenance["git_dirty"] is True
    assert len(provenance["git_status_sha256"]) == 64
    assert set(provenance["code_sha256"]) == {
        "test_advanced_robust.py",
        "memory_layer_robust.py",
    }
    assert all(len(value) == 64 for value in provenance["code_sha256"].values())
