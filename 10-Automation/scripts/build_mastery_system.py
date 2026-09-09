#!/usr/bin/env python3

import json
import re
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "10-Automation" / "data"
INDEX = ROOT / "10-Automation" / "indexes"

DATA.mkdir(parents=True, exist_ok=True)
INDEX.mkdir(parents=True, exist_ok=True)

def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except:
        return None

def problem_dirs():
    result = []
    for p in ROOT.iterdir():
        if not p.is_dir():
            continue
        if not re.match(r"^\d{1,6}-.+", p.name):
            continue

        files = list(p.iterdir())
        if any(x.suffix.lower() in {
            ".java",".cpp",".c",".py",".js",".ts",".go",".rs",
            ".kt",".swift",".rb",".php",".sql"
        } for x in files):
            result.append(p)

    return sorted(result)

def metadata_for(folder):
    m = load(folder / "metadata.json")
    return m if isinstance(m, dict) else {}

def slug_id(folder):
    m = re.match(r"^(\d+)-", folder.name)
    return m.group(1).zfill(4) if m else folder.name

def title(folder, m):
    return m.get("title") or re.sub(
        r"\s+", " ",
        re.sub(r"[-_]+", " ", re.sub(r"^\d+-", "", folder.name))
    ).strip().title()

def link(folder):
    return f"../../{folder.name}/README.md"

def build_structured_views(problems):
    buckets = {
        "Easy": [],
        "Medium": [],
        "Hard": [],
        "Unknown": [],
        "SQL": []
    }

    for p in problems:
        diff = p.get("difficulty", "Unknown")
        category = p.get("category", "DSA")

        item = {
            "id": p["id"],
            "title": p["title"],
            "slug": p["slug"],
            "difficulty": diff,
            "category": category,
            "language": p.get("language", "Unknown"),
            "algorithm": p.get("algorithm", "Unknown"),
            "topics": p.get("topics", []),
            "patterns": p.get("patterns", [])
        }

        if category == "SQL":
            buckets["SQL"].append(item)
        else:
            buckets.setdefault(diff, []).append(item)

    # DSA difficulty indexes
    for diff in ["Easy", "Medium", "Hard"]:
        path = ROOT / "01-DSA" / diff / "INDEX.md"

        lines = [
            f"# DSA — {diff}",
            "",
            f"Problems currently classified as **{diff}**.",
            "",
            "| ID | Problem | Language | Algorithm | Topics |",
            "|---:|---|---|---|---|"
        ]

        for p in sorted(buckets[diff], key=lambda x: int(x["id"])):
            topics = ", ".join(p["topics"]) or "—"
            lines.append(
                f"| {p['id']} | "
                f"[{p['title']}](../../{p['slug']}/README.md) | "
                f"{p['language']} | "
                f"{p['algorithm']} | "
                f"{topics} |"
            )

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # SQL
    for diff in ["Easy", "Medium", "Hard"]:
        path = ROOT / "03-SQL" / diff / "INDEX.md"

        sql = [
            p for p in buckets["SQL"]
            if p["difficulty"] == diff
        ]

        lines = [
            f"# SQL — {diff}",
            "",
            "| ID | Problem | Language | SQL Type |",
            "|---:|---|---|---|"
        ]

        for p in sorted(sql, key=lambda x: int(x["id"])):
            sql_type = p.get("sql_type", "Unknown")
            lines.append(
                f"| {p['id']} | "
                f"[{p['title']}](../../{p['slug']}/README.md) | "
                f"{p['language']} | {sql_type} |"
            )

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def build_topic_indexes(problems):
    topics = defaultdict(list)
    patterns = defaultdict(list)
    algorithms = defaultdict(list)
    languages = defaultdict(list)

    for p in problems:
        item = {
            "id": p["id"],
            "title": p["title"],
            "slug": p["slug"]
        }

        for x in p.get("topics", []):
            topics[x].append(item)

        for x in p.get("patterns", []):
            patterns[x].append(item)

        algorithms[p.get("algorithm", "Unknown")].append(item)
        languages[p.get("language", "Unknown")].append(item)

    for name, groups, directory in [
        ("Topics", topics, ROOT / "04-Data-Structures"),
        ("Patterns", patterns, ROOT / "05-Patterns"),
        ("Algorithms", algorithms, ROOT / "12-Learning" / "Algorithms"),
        ("Languages", languages, ROOT / "10-Automation" / "indexes")
    ]:
        directory.mkdir(parents=True, exist_ok=True)

        for group, items in groups.items():
            safe = re.sub(r"[^A-Za-z0-9]+", "-", group).strip("-")
            if not safe:
                safe = "Unknown"

            if name == "Languages":
                path = directory / f"by-{safe}.md"
            else:
                path = directory / safe / "INDEX.md"
                path.parent.mkdir(parents=True, exist_ok=True)

            lines = [
                f"# {group}",
                "",
                f"Problems classified under **{group}**.",
                "",
                "| ID | Problem |",
                "|---:|---|"
            ]

            for p in sorted(
                items,
                key=lambda x: int(x["id"])
            ):
                lines.append(
                    f"| {p['id']} | "
                    f"[{p['title']}](../../{p['slug']}/README.md) |"
                )

            path.write_text(
                "\n".join(lines) + "\n",
                encoding="utf-8"
            )

def build_revision_system(problems):
    revision_path = DATA / "revision.json"

    old = load(revision_path)
    if not isinstance(old, dict):
        old = {}

    records = {}

    for p in problems:
        pid = p["id"]

        previous = old.get(pid, {})

        records[pid] = {
            "id": pid,
            "title": p["title"],
            "slug": p["slug"],
            "difficulty": p.get("difficulty", "Unknown"),
            "category": p.get("category", "DSA"),

            "last_reviewed": previous.get("last_reviewed"),
            "next_review": previous.get("next_review"),

            "confidence": previous.get("confidence", 0),
            "mistake_count": previous.get("mistake_count", 0),

            "must_revise": previous.get("must_revise", False),
            "important": previous.get("important", False),
            "frequently_asked": previous.get(
                "frequently_asked", False
            ),

            "revision_notes": previous.get(
                "revision_notes", ""
            )
        }

    revision_path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    for folder in [
        "Must-Revise",
        "Mistakes",
        "Important",
        "Frequently-Asked"
    ]:
        path = ROOT / "07-Revision" / folder / "INDEX.md"

        key = {
            "Must-Revise": "must_revise",
            "Mistakes": "mistake_count",
            "Important": "important",
            "Frequently-Asked": "frequently_asked"
        }[folder]

        lines = [
            f"# {folder}",
            "",
            "Problems in this revision queue.",
            "",
            "| ID | Problem | Status |",
            "|---:|---|---|"
        ]

        for pid, r in sorted(
            records.items(),
            key=lambda x: int(x[0])
        ):
            active = (
                r[key] > 0
                if key == "mistake_count"
                else r[key] is True
            )

            if active:
                lines.append(
                    f"| {pid} | "
                    f"[{r['title']}](../../{r['slug']}/README.md) | "
                    f"ACTIVE |"
                )

        if len(lines) == 5:
            lines.append(
                "| — | No problems added yet | — |"
            )

        path.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8"
        )

def build_roadmap_framework():
    files = {
        ROOT / "11-Interview" / "Blind-75" / "README.md": """# Blind 75

Interview preparation roadmap.

Use:

- [ ] Easy
- [ ] Medium
- [ ] Hard
- [ ] Revision
- [ ] Re-solve without looking

Problem membership should be populated from a verified problem list before being marked complete.
""",

        ROOT / "11-Interview" / "NeetCode-150" / "README.md": """# NeetCode 150

Structured interview roadmap.

Sections:

1. Arrays & Hashing
2. Two Pointers
3. Sliding Window
4. Stack
5. Binary Search
6. Linked List
7. Trees
8. Tries
9. Heap / Priority Queue
10. Backtracking
11. Graphs
12. Advanced Graphs
13. 1-D Dynamic Programming
14. 2-D Dynamic Programming
15. Greedy
16. Intervals
17. Math & Geometry
18. Bit Manipulation

Progress will be tracked separately from raw LeetCode synchronization.
""",

        ROOT / "11-Interview" / "Top-Interview-150" / "README.md": """# Top Interview 150

Interview preparation roadmap.

Track:

- [ ] Solved
- [ ] Understood
- [ ] Re-solved
- [ ] Added revision notes
- [ ] Interview ready
""",

        ROOT / "11-Interview" / "SQL" / "README.md": """# SQL Interview Roadmap

Core SQL areas:

- SELECT / WHERE
- ORDER BY
- GROUP BY
- HAVING
- JOIN
- Subqueries
- CTE
- Aggregation
- Window Functions
- CASE
- Date / Time
- String Functions
- NULL handling
- Set Operations
- Ranking
- Advanced SQL
""",

        ROOT / "11-Interview" / "Company-Wise" / "README.md": """# Company-Wise Interview Preparation

Planned company indexes:

- Google
- Amazon
- Microsoft
- Meta
- Apple
- Netflix
- Adobe
- Uber
- Atlassian
- Bloomberg
- Goldman Sachs
- JPMorgan
- Walmart

Problem membership should be based on a verified source before being treated as authoritative.
"""
    }

    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

def build_learning_templates():
    templates = {
        "DSA": """# DSA Learning System

## Learning order

1. Complexity Analysis
2. Arrays
3. Strings
4. Hashing
5. Linked Lists
6. Stack
7. Queue
8. Trees
9. Heap
10. Graph
11. Trie
12. Advanced Data Structures
""",

        "Algorithms": """# Algorithms Learning System

## Core

- Binary Search
- Two Pointers
- Sliding Window
- Prefix Sum
- Sorting
- Greedy
- Backtracking
- Divide and Conquer
- Dynamic Programming
- Graph Algorithms
- String Algorithms
- Bit Manipulation
""",

        "SQL": """# SQL Learning System

## Core progression

SQL basics → filtering → aggregation → joins → subqueries → CTE → window functions → advanced interview queries
""",

        "Patterns": """# Problem Solving Patterns

Master the pattern before memorizing individual solutions.

## Core patterns

- Two Pointers
- Sliding Window
- Fast / Slow Pointers
- Binary Search
- Prefix Sum
- Monotonic Stack
- Heap
- BFS
- DFS
- Backtracking
- Dynamic Programming
- Greedy
"""
    }

    for name, content in templates.items():
        path = ROOT / "12-Learning" / name / "README.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

def build_master_readme(problems):
    total = len(problems)
    d = Counter(p.get("difficulty", "Unknown") for p in problems)
    c = Counter(p.get("category", "DSA") for p in problems)

    content = f"""# LeetCode Mastery

A structured LeetCode, DSA, Algorithms and SQL mastery repository.

## Current Progress

| Metric | Count |
|---|---:|
| Total Problems | {total} |
| DSA | {c.get('DSA', 0)} |
| SQL | {c.get('SQL', 0)} |
| Easy | {d.get('Easy', 0)} |
| Medium | {d.get('Medium', 0)} |
| Hard | {d.get('Hard', 0)} |
| Unknown Difficulty | {d.get('Unknown', 0)} |

## Architecture

### 01 — DSA
Difficulty-based problem index.

### 02 — Algorithms
Algorithm-focused organization.

### 03 — SQL
SQL problem preparation.

### 04 — Data Structures
Data-structure based learning.

### 05 — Patterns
Interview problem-solving patterns.

### 07 — Revision
Mistakes, important problems and revision queues.

### 08 — Templates
Reusable solution templates.

### 09 — Statistics
Progress analytics.

### 10 — Automation
Metadata, classification, indexes and validation.

### 11 — Interview
Blind 75, NeetCode 150, Top Interview 150, SQL and company preparation.

### 12 — Learning
Structured learning notes.

## Automation Flow

LeetCode
→ LeetHub-Neo
→ GitHub
→ Classification Engine
→ Metadata
→ Indexes
→ Statistics
→ Revision System

## Rule

**Solve once → understand deeply → record pattern → revise → re-solve.**
"""

    (ROOT / "README.md").write_text(
        content,
        encoding="utf-8"
    )

def main():
    folders = problem_dirs()
    problems = []

    for folder in folders:
        m = metadata_for(folder)

        problems.append({
            "id": slug_id(folder),
            "title": title(folder, m),
            "slug": folder.name,
            "difficulty": m.get("difficulty", "Unknown"),
            "category": m.get("category", "DSA"),
            "language": m.get("language", "Unknown"),
            "algorithm": m.get("algorithm", "Unknown"),
            "topics": m.get("topics", []),
            "patterns": m.get("patterns", []),
            "sql_type": m.get("sql_type", "Unknown")
        })

    problems.sort(key=lambda x: int(x["id"]))

    build_structured_views(problems)
    build_topic_indexes(problems)
    build_revision_system(problems)
    build_roadmap_framework()
    build_learning_templates()
    build_master_readme(problems)

    (DATA / "mastery-system.json").write_text(
        json.dumps(
            {
                "total": len(problems),
                "problems": problems,
                "difficulty": dict(
                    Counter(p["difficulty"] for p in problems)
                ),
                "category": dict(
                    Counter(p["category"] for p in problems)
                )
            },
            indent=2,
            ensure_ascii=False
        ) + "\n",
        encoding="utf-8"
    )

    print("=" * 70)
    print("       MASTERY SYSTEM BUILD COMPLETE")
    print("=" * 70)
    print(f"Problems discovered : {len(problems)}")
    print()
    print("Generated:")
    print("  01-DSA difficulty indexes")
    print("  03-SQL difficulty indexes")
    print("  04-Data-Structures indexes")
    print("  05-Patterns indexes")
    print("  07-Revision system")
    print("  11-Interview roadmap framework")
    print("  12-Learning framework")
    print("  Master README")
    print("  mastery-system.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
