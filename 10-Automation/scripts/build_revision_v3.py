#!/usr/bin/env python3

import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "10-Automation" / "data"
INDEXES = ROOT / "10-Automation" / "indexes"

SOURCE = DATA / "problems-v3.json"

def load():
    return json.loads(SOURCE.read_text(encoding="utf-8"))

def main():
    data = load()
    problems = data.get("problems", [])

    revision = []

    for p in problems:
        item = {
            "id": p["id"],
            "title": p["title"],
            "slug": p["slug"],
            "category": p.get("category", "Unknown"),
            "difficulty": p.get("difficulty", "Unknown"),
            "languages": p.get("languages", []),
            "topics": p.get("topics", []),
            "patterns": p.get("patterns", []),
            "status": "solved",
            "must_revise": False,
            "important": False,
            "mistake_count": 0,
            "confidence": 0,
            "last_reviewed": None,
            "next_review": None,
            "review_intervals_days": [1, 3, 7, 14, 30, 60]
        }
        revision.append(item)

    payload = {
        "version": "3.0",
        "description": "Revision and spaced-repetition system",
        "intervals_days": [1, 3, 7, 14, 30, 60],
        "total_problems": len(revision),
        "problems": revision
    }

    (DATA / "revision-v3.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    groups = defaultdict(list)

    for p in revision:
        if p["must_revise"]:
            groups["Must Revise"].append(p)
        if p["important"]:
            groups["Important"].append(p)

    def write(name, title, items):
        lines = [
            f"# {title}",
            "",
            "> Automatically maintained revision index.",
            ""
        ]

        if not items:
            lines.append("No problems currently assigned.")
            lines.append("")
        else:
            for p in sorted(items, key=lambda x: x["id"]):
                lines.append(
                    f"- [{p['id']} — {p['title']}](../../{p['slug']}/)"
                )

        (ROOT / "07-Revision" / name).write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8"
        )

    write("Must-Revise/README.md", "🧠 Must Revise", groups["Must Revise"])
    write("Important/README.md", "⭐ Important", groups["Important"])

    mistakes = [
        "# ❌ Mistake Log",
        "",
        "> Add mistakes here when a problem is solved incorrectly or requires revision.",
        "",
        "| Problem | Mistake | Fix | Date |",
        "|---|---|---|---|",
        "| — | — | — | — |",
        ""
    ]

    (ROOT / "07-Revision/Mistakes/README.md").write_text(
        "\n".join(mistakes),
        encoding="utf-8"
    )

    frequent = [
        "# 🔥 Frequently Asked",
        "",
        "> Problems marked frequently-asked will appear here.",
        "",
        "No problems currently assigned.",
        ""
    ]

    (ROOT / "07-Revision/Frequently-Asked/README.md").write_text(
        "\n".join(frequent),
        encoding="utf-8"
    )

    spaced = [
        "# 📅 Spaced Repetition",
        "",
        "Review schedule:",
        "",
        "| Review | Interval |",
        "|---|---:|",
        "| R1 | 1 day |",
        "| R2 | 3 days |",
        "| R3 | 7 days |",
        "| R4 | 14 days |",
        "| R5 | 30 days |",
        "| R6 | 60 days |",
        "",
        "> `last_reviewed` and `next_review` are populated when review activity is recorded.",
        ""
    ]

    (ROOT / "07-Revision/Spaced-Repetition/README.md").write_text(
        "\n".join(spaced),
        encoding="utf-8"
    )

    print(f"Revision system generated for {len(revision)} problems.")

if __name__ == "__main__":
    main()
