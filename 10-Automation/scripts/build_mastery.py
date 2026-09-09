#!/usr/bin/env python3

import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "10-Automation" / "data"
INDEX = ROOT / "10-Automation" / "indexes"

DATA.mkdir(parents=True, exist_ok=True)
INDEX.mkdir(parents=True, exist_ok=True)

EXTENSIONS = {
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".sql": "SQL",
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
}

SQL_WORDS = {
    "sql", "database", "mysql", "postgresql",
    "join", "subquery", "group by", "having",
    "select", "where", "window function", "cte"
}

PATTERNS = {
    "Sliding Window": [
        "sliding window", "window"
    ],
    "Two Pointers": [
        "two pointers", "two-pointer", "two pointer"
    ],
    "Binary Search": [
        "binary search", "binary-search"
    ],
    "Prefix Sum": [
        "prefix sum", "prefix-sum", "running sum"
    ],
    "Fast Slow Pointers": [
        "fast slow", "fast and slow", "slow pointer", "fast pointer"
    ],
    "Merge Intervals": [
        "merge intervals", "intervals"
    ],
    "Monotonic Stack": [
        "monotonic stack", "next greater", "next smaller"
    ],
    "Backtracking": [
        "backtracking", "backtrack"
    ],
    "Dynamic Programming": [
        "dynamic programming", "dynamic-programming", "dp"
    ],
    "Greedy": [
        "greedy"
    ],
    "DFS": [
        "depth first search", "dfs"
    ],
    "BFS": [
        "breadth first search", "bfs"
    ],
    "Divide and Conquer": [
        "divide and conquer"
    ],
    "Heap": [
        "heap", "priority queue"
    ],
    "Hashing": [
        "hash map", "hash table", "hashing", "dictionary"
    ],
    "Sorting": [
        "sorting", "sort"
    ],
    "Recursion": [
        "recursion", "recursive"
    ],
    "Bit Manipulation": [
        "bit manipulation", "bitwise"
    ],
}

TOPIC_ALIASES = {
    "array": "Array",
    "arrays": "Array",
    "string": "String",
    "strings": "String",
    "hash-table": "Hash Table",
    "hash table": "Hash Table",
    "hashing": "Hash Table",
    "linked-list": "Linked List",
    "linked list": "Linked List",
    "stack": "Stack",
    "queue": "Queue",
    "heap": "Heap",
    "binary-tree": "Binary Tree",
    "tree": "Tree",
    "binary search tree": "Binary Search Tree",
    "graph": "Graph",
    "graphs": "Graph",
    "matrix": "Matrix",
    "sorting": "Sorting",
    "math": "Math",
    "simulation": "Simulation",
    "prefix-sum": "Prefix Sum",
    "prefix sum": "Prefix Sum",
    "two-pointers": "Two Pointers",
    "two pointers": "Two Pointers",
    "binary-search": "Binary Search",
    "binary search": "Binary Search",
    "backtracking": "Backtracking",
    "greedy": "Greedy",
    "dynamic-programming": "Dynamic Programming",
    "dynamic programming": "Dynamic Programming",
    "divide-and-conquer": "Divide and Conquer",
    "divide and conquer": "Divide and Conquer",
    "bit-manipulation": "Bit Manipulation",
    "database": "Database",
    "sql": "Database",
}

def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

def problem_id_slug(path):
    m = re.match(r"^(\d+)-(.+)$", path.name)
    if not m:
        return None, None
    return m.group(1), m.group(2)

def detect_language(files):
    langs = []
    for f in files:
        if f.suffix.lower() in EXTENSIONS:
            langs.append(EXTENSIONS[f.suffix.lower()])
    if not langs:
        return "Unknown"
    return Counter(langs).most_common(1)[0][0]

def detect_category(language, text, files):
    if language == "SQL":
        return "SQL"

    lower = text.lower()

    sql_score = sum(1 for word in SQL_WORDS if word in lower)

    if sql_score >= 3:
        return "SQL"

    if any(f.suffix.lower() == ".sql" for f in files):
        return "SQL"

    return "DSA"

def detect_difficulty(text):
    lines = text.splitlines()

    # Prefer explicit metadata-style lines.
    patterns = [
        r"\*\*difficulty\*\*\s*:\s*(easy|medium|hard)",
        r"difficulty\s*:\s*(easy|medium|hard)",
        r"^\s*(easy|medium|hard)\s*$",
    ]

    for line in lines:
        clean = line.strip().lower()
        for p in patterns:
            m = re.search(p, clean, re.I)
            if m:
                return m.group(1).capitalize()

    # LeetHub README often contains difficulty near title/metadata.
    first = "\n".join(lines[:20]).lower()

    for difficulty in ("Hard", "Medium", "Easy"):
        if re.search(rf"\b{difficulty.lower()}\b", first):
            return difficulty

    return "Unknown"

def detect_topics(slug, text):
    topics = set()
    lower = (slug + "\n" + text).lower()

    for alias, canonical in TOPIC_ALIASES.items():
        if alias in lower:
            topics.add(canonical)

    # Topic directories from LeetHub.
    topics_dir = ROOT / "Topics"
    if topics_dir.exists():
        for d in topics_dir.iterdir():
            if not d.is_dir():
                continue

            pjson = d / "problems.json"
            if not pjson.exists():
                continue

            raw = read_text(pjson)

            if slug.lower() in raw.lower():
                canonical = TOPIC_ALIASES.get(d.name.lower(), d.name.replace("-", " ").title())
                topics.add(canonical)

    return sorted(topics)

def detect_patterns(text):
    lower = text.lower()
    found = set()

    for pattern, words in PATTERNS.items():
        for word in words:
            if word in lower:
                found.add(pattern)
                break

    return sorted(found)

def clean_title(slug):
    title = re.sub(r"^\d+-", "", slug)
    return title.replace("-", " ").title()

def discover():
    problems = []

    for p in ROOT.iterdir():
        if not p.is_dir():
            continue

        pid, slug = problem_id_slug(p)

        if not pid:
            continue

        files = [
            f for f in p.iterdir()
            if f.is_file() and f.name != "metadata.json"
        ]

        if not files:
            continue

        readme = p / "README.md"
        text = read_text(readme) if readme.exists() else ""

        language = detect_language(files)
        category = detect_category(language, text, files)
        difficulty = detect_difficulty(text)
        topics = detect_topics(slug, text)
        patterns = detect_patterns(text)

        existing = {}
        metadata_file = p / "metadata.json"

        if metadata_file.exists():
            try:
                existing = json.loads(read_text(metadata_file))
            except Exception:
                existing = {}

        metadata = {
            **existing,
            "leetcode_id": int(pid),
            "slug": slug,
            "title": existing.get("title") or clean_title(slug),
            "language": existing.get("language") or language,
            "category": existing.get("category") or category,
            "difficulty": existing.get("difficulty") or difficulty,
            "topics": sorted(set(existing.get("topics", [])) | set(topics)),
            "patterns": sorted(set(existing.get("patterns", [])) | set(patterns)),
            "companies": existing.get("companies", []),
            "revision": existing.get("revision", {
                "must_revise": False,
                "important": False,
                "mistake": False,
                "frequently_asked": False
            }),
            "complexity": existing.get("complexity", {
                "time": "Unknown",
                "space": "Unknown"
            }),
            "notes": existing.get("notes", ""),
            "solution_files": sorted(
                str(f.relative_to(p))
                for f in files
                if f.suffix.lower() in EXTENSIONS
            )
        }

        dump(metadata_file, metadata)

        problems.append(metadata)

    problems.sort(key=lambda x: x["leetcode_id"])

    return problems

def build_indexes(problems):
    difficulty = defaultdict(list)
    language = defaultdict(list)
    category = defaultdict(list)
    topic = defaultdict(list)
    pattern = defaultdict(list)
    revision = defaultdict(list)

    for p in problems:
        ref = {
            "id": p["leetcode_id"],
            "slug": p["slug"],
            "title": p["title"]
        }

        difficulty[p["difficulty"]].append(ref)
        language[p["language"]].append(ref)
        category[p["category"]].append(ref)

        for t in p.get("topics", []):
            topic[t].append(ref)

        for pat in p.get("patterns", []):
            pattern[pat].append(ref)

        rev = p.get("revision", {})

        for key, enabled in rev.items():
            if enabled:
                revision[key].append(ref)

    dump(INDEX / "by-difficulty.json", dict(sorted(difficulty.items())))
    dump(INDEX / "by-language.json", dict(sorted(language.items())))
    dump(INDEX / "by-category.json", dict(sorted(category.items())))
    dump(INDEX / "by-topic.json", dict(sorted(topic.items())))
    dump(INDEX / "by-pattern.json", dict(sorted(pattern.items())))
    dump(INDEX / "by-revision.json", dict(sorted(revision.items())))

def build_statistics(problems):
    difficulty = Counter(p["difficulty"] for p in problems)
    language = Counter(p["language"] for p in problems)
    category = Counter(p["category"] for p in problems)

    topics = Counter()
    patterns = Counter()

    for p in problems:
        topics.update(p.get("topics", []))
        patterns.update(p.get("patterns", []))

    stats = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(problems),
        "difficulty": dict(difficulty),
        "language": dict(language),
        "category": dict(category),
        "topics": dict(topics.most_common()),
        "patterns": dict(patterns.most_common()),
    }

    dump(DATA / "statistics.json", stats)
    return stats

def build_progress(stats):
    d = stats["difficulty"]
    l = stats["language"]
    c = stats["category"]

    md = f"""# 📊 LeetCode Progress

> Automatically generated by `10-Automation/scripts/build_mastery.py`.

## Overall

| Category | Solved |
|---|---:|
| DSA | {c.get("DSA", 0)} |
| SQL | {c.get("SQL", 0)} |
| Total | {stats["total"]} |

## Difficulty

| Difficulty | Solved |
|---|---:|
| 🟢 Easy | {d.get("Easy", 0)} |
| 🟡 Medium | {d.get("Medium", 0)} |
| 🔴 Hard | {d.get("Hard", 0)} |
| ❓ Unknown | {d.get("Unknown", 0)} |

## Languages

| Language | Problems |
|---|---:|
"""

    for lang, count in sorted(l.items(), key=lambda x: (-x[1], x[0])):
        md += f"| {lang} | {count} |\n"

    md += """
## Top Topics

| Topic | Problems |
|---|---:|
"""

    for topic, count in list(stats["topics"].items())[:25]:
        md += f"| {topic} | {count} |\n"

    md += """
## Top Patterns

| Pattern | Problems |
|---|---:|
"""

    for pattern, count in list(stats["patterns"].items())[:20]:
        md += f"| {pattern} | {count} |\n"

    (ROOT / "PROGRESS.md").write_text(md, encoding="utf-8")

def build_master_readme(stats):
    path = ROOT / "README.md"

    old = read_text(path)

    marker = "<!-- AUTO-STATS-START -->"
    end = "<!-- AUTO-STATS-END -->"

    block = f"""
{marker}

## 📈 Live Repository Statistics

**Total solved:** {stats["total"]}

| Metric | Count |
|---|---:|
| DSA | {stats["category"].get("DSA", 0)} |
| SQL | {stats["category"].get("SQL", 0)} |
| Easy | {stats["difficulty"].get("Easy", 0)} |
| Medium | {stats["difficulty"].get("Medium", 0)} |
| Hard | {stats["difficulty"].get("Hard", 0)} |

### Languages

"""

    for lang, count in sorted(stats["language"].items(), key=lambda x: (-x[1], x[0])):
        block += f"- **{lang}:** {count}\n"

    block += f"""
{end}
"""

    if marker in old and end in old:
        old = re.sub(
            re.escape(marker) + r".*?" + re.escape(end),
            block.strip(),
            old,
            flags=re.S
        )
    else:
        old += "\n" + block

    path.write_text(old.rstrip() + "\n", encoding="utf-8")

def main():
    problems = discover()

    dump(DATA / "problems.json", problems)

    build_indexes(problems)
    stats = build_statistics(problems)
    build_progress(stats)
    build_master_readme(stats)

    print()
    print("=" * 60)
    print("        LEETCODE MASTERY BUILD COMPLETE")
    print("=" * 60)
    print(f"Problems          : {stats['total']}")
    print(f"DSA               : {stats['category'].get('DSA', 0)}")
    print(f"SQL               : {stats['category'].get('SQL', 0)}")
    print(f"Easy              : {stats['difficulty'].get('Easy', 0)}")
    print(f"Medium            : {stats['difficulty'].get('Medium', 0)}")
    print(f"Hard              : {stats['difficulty'].get('Hard', 0)}")
    print(f"Unknown Difficulty: {stats['difficulty'].get('Unknown', 0)}")
    print()
    print("Languages:")
    for k, v in stats["language"].items():
        print(f"  {k}: {v}")
    print()
    print(f"Topics detected   : {len(stats['topics'])}")
    print(f"Patterns detected : {len(stats['patterns'])}")
    print("=" * 60)

if __name__ == "__main__":
    main()
