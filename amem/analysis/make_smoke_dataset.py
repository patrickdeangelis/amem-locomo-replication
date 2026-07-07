#!/usr/bin/env python3
import copy
import json
from pathlib import Path


SOURCE = Path("data/locomo10.json")
TARGET = Path("data/locomo_smoke_min.json")


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    sample = copy.deepcopy(data[0])

    conversation = sample["conversation"]
    reduced_conversation = {
        "speaker_a": conversation["speaker_a"],
        "speaker_b": conversation["speaker_b"],
        "session_1_date_time": conversation["session_1_date_time"],
        "session_1": conversation["session_1"][:8],
    }

    sample["conversation"] = reduced_conversation
    sample["qa"] = sample["qa"][:3]
    sample["event_summary"] = {
        "events_session_1": sample["event_summary"].get("events_session_1", {})
    }
    sample["observation"] = {
        "session_1_observation": sample["observation"].get("session_1_observation", {})
    }
    sample["session_summary"] = {
        "session_1_summary": sample["session_summary"].get("session_1_summary", "")
    }
    sample["sample_id"] = f"{sample.get('sample_id', 'sample0')}-smoke-min"

    TARGET.write_text(json.dumps([sample], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {TARGET}")
    print("samples=1 sessions=1 turns=8 qas=3")


if __name__ == "__main__":
    main()

