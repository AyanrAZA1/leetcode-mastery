#!/usr/bin/env python3

import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "10-Automation/data"
STATS = ROOT / "09-Statistics"

def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))

def main():

    data = load("problems-v3.json")
    problems = data["problems"]

    difficulty = Counter(
        p.get("difficulty", "Unknown")
        for p in problems
    )

    languages = Counter()

    for p in problems:
        for lang in p.get("languages", []):
            languages[lang] += 1

    categories = Counter(
        p.get("category", "Unknown")
        for p in problems
    )

    topics = Counter()

    for p in problems:
        for topic in p.get("topics", []):
            topics[topic] += 1

    patterns = Counter()

    for p in problems:
        for pattern in p.get("patterns", []):
            patterns[pattern] += 1

    revision = load("revision-v3.json")

    must_revise = sum(
        p["must_revise"]
        for p in revision["problems"]
    )

    important = sum(
        p["important"]
        for p in revision["problems"]
    )

    mistakes = sum(
        p["mistake_count"] > 0
        for p in revision["problems"]
    )

    lines = [
        "# 📊 LeetCode Mastery Dashboard",
        "",
        f"**Total Solved:** {len(problems)}",
        "",
        "## Categories",
        "",
        "| Category | Count |",
        "|---|---:|"
    ]

    for k, v in sorted(categories.items()):
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Difficulty",
        "",
        "| Difficulty | Count |",
        "|---|---:|"
    ]

    for k, v in sorted(difficulty.items()):
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Languages",
        "",
        "| Language | Problems |",
        "|---|---:|"
    ]

    for k, v in sorted(languages.items()):
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Top Topics",
        "",
        "| Topic | Problems |",
        "|---|---:|"
    ]

    for k, v in sorted(
        topics.items(),
        key=lambda x: (-x[1], x[0])
    ):
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Patterns",
        "",
        "| Pattern | Problems |",
        "|---|---:|"
    ]

    for k, v in sorted(
        patterns.items(),
        key=lambda x: (-x[1], x[0])
    ):
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Revision",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Must Revise | {must_revise} |",
        f"| Important | {important} |",
        f"| With Mistakes | {mistakes} |",
        "",
        "## Automation Pipeline",
        "",
        "```text",
        "LeetCode",
        "   ↓",
        "LeetHub-Neo",
        "   ↓",
        "GitHub",
        "   ↓",
        "Inventory",
        "   ↓",
        "Classification V3",
        "   ↓",
        "Metadata",
        "   ↓",
        "Indexes",
        "   ↓",
        "Statistics",
        "   ↓",
        "Revision",
        "   ↓",
        "Interview Preparation",
        "```",
        ""
    ]

    STATS.mkdir(parents=True, exist_ok=True)

    (STATS / "MASTER_DASHBOARD.md").write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print(f"Dashboard generated: {STATS / 'MASTER_DASHBOARD.md'}")

if __name__ == "__main__":
    main()
