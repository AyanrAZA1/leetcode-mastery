#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PROBLEM_RE = re.compile(r"^\d{1,6}-.+")
SOLUTION_EXT = {
    ".java", ".cpp", ".c", ".py", ".js", ".ts",
    ".go", ".rs", ".kt", ".swift", ".rb", ".php", ".sql"
}

errors = []
warnings = []

def fail(message):
    errors.append(message)

def warn(message):
    warnings.append(message)

def load_json(path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        fail(f"Invalid JSON: {path} -> {e}")
        return None

# ------------------------------------------------------------
# Discover real problem directories
# ------------------------------------------------------------

problems = []

for path in ROOT.iterdir():
    if not path.is_dir():
        continue

    if not PROBLEM_RE.match(path.name):
        continue

    solutions = [
        p for p in path.rglob("*")
        if p.is_file() and p.suffix.lower() in SOLUTION_EXT
    ]

    if solutions:
        problems.append(path)

ids = []

for problem in problems:
    match = re.match(r"^(\d+)-", problem.name)

    if not match:
        fail(f"Invalid problem folder: {problem.name}")
        continue

    pid = match.group(1)

    if pid in ids:
        fail(f"Duplicate problem ID: {pid}")

    ids.append(pid)

    readme = problem / "README.md"

    if not readme.exists():
        fail(f"Missing README: {problem.name}")

    if not solutions:
        fail(f"Missing solution: {problem.name}")

# ------------------------------------------------------------
# Validate generated JSON
# ------------------------------------------------------------

json_files = [
    ROOT / "10-Automation/data/inventory-v3.json",
    ROOT / "10-Automation/data/problems-v3.json",
    ROOT / "10-Automation/data/revision-v3.json",
]

for path in json_files:
    if path.exists():
        load_json(path)

# ------------------------------------------------------------
# Validate classification
# ------------------------------------------------------------

classification = ROOT / "10-Automation/data/problems-v3.json"

if classification.exists():
    data = load_json(classification)

    if isinstance(data, dict):
        records = data.get("problems", data.get("records", []))
    elif isinstance(data, list):
        records = data
    else:
        records = []

    seen = set()

    for p in records:
        if not isinstance(p, dict):
            fail("Classification contains non-object record")
            continue

        pid = str(
            p.get("id")
            or p.get("number")
            or p.get("problem_id")
            or ""
        )

        if not pid:
            fail("Classification record missing problem ID")
            continue

        if pid in seen:
            fail(f"Duplicate classification ID: {pid}")

        seen.add(pid)

        difficulty = p.get("difficulty", "Unknown")

        if difficulty not in {"Easy", "Medium", "Hard", "Unknown"}:
            fail(f"Invalid difficulty for {pid}: {difficulty}")

# ------------------------------------------------------------
# Validate revision
# ------------------------------------------------------------

revision = ROOT / "10-Automation/data/revision-v3.json"

if revision.exists():
    data = load_json(revision)

    if isinstance(data, dict):
        records = data.get("problems", data.get("records", []))
    elif isinstance(data, list):
        records = data
    else:
        records = []

    revision_ids = {
        str(
            p.get("id")
            or p.get("number")
            or p.get("problem_id")
            or ""
        )
        for p in records
        if isinstance(p, dict)
    }

    for pid in ids:
        if pid not in revision_ids:
            warn(f"Problem missing from revision index: {pid}")

# ------------------------------------------------------------
# Validate generated indexes
# ------------------------------------------------------------

index_dir = ROOT / "10-Automation/indexes"

if index_dir.exists():
    for path in index_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() == ".json":
            load_json(path)

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print()
print("=" * 60)
print("🔍 REPOSITORY VALIDATION V4")
print("=" * 60)
print(f"Problems discovered : {len(problems)}")
print(f"Unique problem IDs  : {len(set(ids))}")
print(f"Errors              : {len(errors)}")
print(f"Warnings            : {len(warnings)}")

if warnings:
    print()
    print("⚠️ WARNINGS")
    for item in warnings:
        print(" -", item)

if errors:
    print()
    print("❌ ERRORS")
    for item in errors:
        print(" -", item)

    print()
    print("❌ VALIDATION FAILED")
    sys.exit(1)

print()
print("✅ VALIDATION PASSED")
