#!/usr/bin/env python3
import copy
import json
from pathlib import Path


SOURCE = Path("data/locomo10.json")
TARGET = Path("data/locomo_etapa2_reduced_s2.json")
SESSION_LIMIT = 2


def evidence_sessions(qa):
    sessions = set()
    for evidence in qa.get("evidence", []):
        if ":" in evidence:
            sessions.add(evidence.split(":", 1)[0])
    return sessions


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    sample = copy.deepcopy(data[0])

    allowed_sessions = {f"D{i}" for i in range(1, SESSION_LIMIT + 1)}
    allowed_numbers = range(1, SESSION_LIMIT + 1)

    conversation = sample["conversation"]
    reduced_conversation = {
        "speaker_a": conversation["speaker_a"],
        "speaker_b": conversation["speaker_b"],
    }
    for i in allowed_numbers:
        reduced_conversation[f"session_{i}_date_time"] = conversation[f"session_{i}_date_time"]
        reduced_conversation[f"session_{i}"] = conversation[f"session_{i}"]

    sample["conversation"] = reduced_conversation
    sample["qa"] = [
        qa for qa in sample["qa"]
        if evidence_sessions(qa) and evidence_sessions(qa) <= allowed_sessions
    ]
    sample["event_summary"] = {
        f"events_session_{i}": sample["event_summary"].get(f"events_session_{i}", {})
        for i in allowed_numbers
    }
    sample["observation"] = {
        f"session_{i}_observation": sample["observation"].get(f"session_{i}_observation", {})
        for i in allowed_numbers
    }
    sample["session_summary"] = {
        f"session_{i}_summary": sample["session_summary"].get(f"session_{i}_summary", "")
        for i in allowed_numbers
    }
    sample["sample_id"] = f"{sample.get('sample_id', 'sample0')}-reduced-s{SESSION_LIMIT}"

    TARGET.write_text(json.dumps([sample], ensure_ascii=False, indent=2), encoding="utf-8")

    turns = sum(len(reduced_conversation[f"session_{i}"]) for i in allowed_numbers)
    categories = {}
    for qa in sample["qa"]:
        categories[str(qa.get("category"))] = categories.get(str(qa.get("category")), 0) + 1

    print(f"wrote {TARGET}")
    print(f"samples=1 sessions={SESSION_LIMIT} turns={turns} qas={len(sample['qa'])}")
    print(f"categories={categories}")


if __name__ == "__main__":
    main()

