#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "10-Automation/data/problems-v3.json"
OLD = ROOT / "10-Automation/data/revision-v3.json"
OUT = ROOT / "10-Automation/data/revision-v4.json"

INTERVALS = [1, 3, 7, 14, 30, 60]

def load_json(path, default):
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def problem_id(p):
    return str(
        p.get("id")
        or p.get("number")
        or p.get("problem_id")
        or ""
    )

raw_problems = load_json(INPUT, [])
old_data = load_json(OLD, [])

if isinstance(raw_problems, dict):
    problems = raw_problems.get("problems", raw_problems.get("records", []))
else:
    problems = raw_problems if isinstance(raw_problems, list) else []

if isinstance(old_data, dict):
    old_records = old_data.get("problems", old_data.get("records", []))
else:
    old_records = old_data if isinstance(old_data, list) else []

old_map = {
    problem_id(x): x
    for x in old_records
    if isinstance(x, dict) and problem_id(x)
}

records = []

for p in problems:
    if not isinstance(p, dict):
        continue

    pid = problem_id(p)
    if not pid:
        continue

    old = old_map.get(pid, {})

    record = {
        "id": pid,
        "title": p.get("title", ""),
        "difficulty": p.get("difficulty", "Unknown"),
        "category": p.get("category", "Unknown"),
        "topics": p.get("topics", []),
        "patterns": p.get("patterns", []),

        # Preserve all human-controlled revision state.
        "must_revise": old.get("must_revise", False),
        "important": old.get("important", False),
        "mistake_count": old.get("mistake_count", 0),
        "confidence": old.get("confidence", 0),
        "last_reviewed": old.get("last_reviewed"),
        "next_review": old.get("next_review"),

        # New tracking fields.
        "review_count": old.get("review_count", 0),
        "revision_level": old.get("revision_level", 0),
        "notes": old.get("notes", ""),
    }

    # Preserve any additional user fields from previous revision data.
    for key, value in old.items():
        if key not in record:
            record[key] = value

    records.append(record)

payload = {
    "version": "4.0",
    "generated_by": "build_revision_v4.py",
    "preserves_manual_state": True,
    "review_intervals_days": INTERVALS,
    "total_problems": len(records),
    "problems": records,
}

OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open("w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)
    f.write("\n")

# Keep the old filename as a compatibility mirror.
with OLD.open("w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"✅ Revision V4 generated: {len(records)} problems")
print("🔒 Manual revision state preserved")
