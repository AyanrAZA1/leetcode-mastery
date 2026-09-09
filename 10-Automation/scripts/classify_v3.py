#!/usr/bin/env python3

import json
import re
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "10-Automation" / "data"
INDEXES = ROOT / "10-Automation" / "indexes"

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def normalize(value):
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")

def extract_topic_problem(item):
    if not isinstance(item, dict):
        return None

    for key in ("id", "problem_id", "question_id", "frontend_id"):
        if key in item:
            try:
                return int(item[key])
            except:
                pass

    for key in ("titleSlug", "slug", "title_slug"):
        if key in item and item[key]:
            return normalize(item[key])

    for key in ("title", "name"):
        if key in item and item[key]:
            return normalize(item[key])

    return None

def discover_topic_data():

    result = defaultdict(set)

    topics_root = ROOT / "Topics"

    if not topics_root.exists():
        return result

    for topic_dir in sorted(topics_root.iterdir()):

        if not topic_dir.is_dir():
            continue

        topic = topic_dir.name

        problem_file = topic_dir / "problems.json"

        if not problem_file.exists():
            continue

        data = load_json(problem_file)

        if not isinstance(data, list):
            if isinstance(data, dict):
                candidates = (
                    data.get("problems")
                    or data.get("questions")
                    or data.get("data")
                    or []
                )
            else:
                candidates = []
        else:
            candidates = data

        for item in candidates:

            key = extract_topic_problem(item)

            if key is not None:
                result[key].add(topic)

    return result

def discover_inventory():

    path = DATA / "inventory-v3.json"

    data = load_json(path)

    if not data:
        raise SystemExit("inventory-v3.json not found. Run inventory_v3.py first.")

    return data["problems"]

def classify_problem(problem, topic_map):

    pid = problem["id"]
    slug = normalize(problem["slug"])
    title = normalize(problem["title"])

    topics = set()

    for key in (pid, slug, title):
        if key in topic_map:
            topics.update(topic_map[key])

    # Topic aliases / cleanup
    aliases = {
        "array": "Array",
        "string": "String",
        "hash-table": "Hash Table",
        "linked-list": "Linked List",
        "binary-tree": "Binary Tree",
        "two-pointers": "Two Pointers",
        "prefix-sum": "Prefix Sum",
        "sliding-window": "Sliding Window",
        "binary-search": "Binary Search",
        "dynamic-programming": "Dynamic Programming",
        "divide-and-conquer": "Divide and Conquer",
        "bit-manipulation": "Bit Manipulation",
        "backtracking": "Backtracking",
        "greedy": "Greedy",
        "sorting": "Sorting",
        "stack": "Stack",
        "heap": "Heap",
        "graph": "Graph",
        "database": "Database / SQL",
        "math": "Math",
        "matrix": "Matrix",
        "simulation": "Simulation",
    }

    clean_topics = []

    for topic in sorted(topics):
        clean_topics.append(aliases.get(topic, topic.replace("-", " ").title()))

    language = problem["languages"][0] if problem["languages"] else "Unknown"

    category = "SQL" if language == "SQL" or pid in {
        175, 584, 595, 1148, 1683, 1757
    } else "DSA"

    # Pattern inference only when topic evidence exists
    patterns = []

    pattern_map = {
        "Sliding Window": "Sliding Window",
        "Two Pointers": "Two Pointers",
        "Binary Search": "Binary Search",
        "Prefix Sum": "Prefix Sum",
        "Fast Slow Pointers": "Fast & Slow Pointers",
        "Monotonic Stack": "Monotonic Stack",
        "Backtracking": "Backtracking",
        "Dynamic Programming": "Dynamic Programming",
        "Greedy": "Greedy",
    }

    topic_string = " ".join(clean_topics).lower()

    for key, value in pattern_map.items():
        if key.lower() in topic_string:
            patterns.append(value)

    return {
        **problem,
        "category": category,
        "topics": clean_topics,
        "patterns": sorted(set(patterns)),
        "primary_language": language,
        "revision": {
            "must_revise": False,
            "important": False,
            "mistake_count": 0,
            "confidence": 0,
            "last_reviewed": None,
            "next_review": None
        }
    }

def main():

    problems = discover_inventory()
    raw_topics = discover_topic_data()

    # Build aliases so topic data can match inventory reliably
    topic_map = defaultdict(set)

    for key, topics in raw_topics.items():
        topic_map[key].update(topics)

    classified = []

    for problem in problems:
        classified.append(
            classify_problem(problem, topic_map)
        )

    classified.sort(key=lambda x: x["id"])

    difficulty = Counter()
    languages = Counter()
    categories = Counter()
    topics = Counter()
    patterns = Counter()

    for p in classified:

        # Difficulty may be unavailable in current LeetHub data.
        # Keep Unknown rather than inventing it.
        diff = p.get("difficulty") or "Unknown"

        difficulty[diff] += 1
        languages[p["primary_language"]] += 1
        categories[p["category"]] += 1

        for topic in p["topics"]:
            topics[topic] += 1

        for pattern in p["patterns"]:
            patterns[pattern] += 1

    output = {
        "version": "3.0",
        "source": "inventory-v3 + Topics/*/problems.json",
        "total": len(classified),
        "statistics": {
            "difficulty": dict(sorted(difficulty.items())),
            "languages": dict(sorted(languages.items())),
            "categories": dict(sorted(categories.items())),
            "topics": dict(sorted(topics.items())),
            "patterns": dict(sorted(patterns.items())),
        },
        "problems": classified,
    }

    DATA.mkdir(parents=True, exist_ok=True)
    INDEXES.mkdir(parents=True, exist_ok=True)

    (DATA / "problems-v3.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    # ---------- INDEXES ----------

    def write_index(filename, title, groups):

        lines = [
            f"# {title}",
            "",
            f"> Generated automatically from {len(classified)} problems.",
            ""
        ]

        for group, items in sorted(groups.items()):

            lines.append(f"## {group}")
            lines.append("")

            for p in sorted(items, key=lambda x: x["id"]):
                lines.append(
                    f"- [{p['id']} — {p['title']}](../../{p['slug']}/)"
                )

            lines.append("")

        (INDEXES / filename).write_text(
            "\n".join(lines),
            encoding="utf-8"
        )

    groups_topic = defaultdict(list)
    groups_language = defaultdict(list)
    groups_category = defaultdict(list)
    groups_difficulty = defaultdict(list)
    groups_pattern = defaultdict(list)

    for p in classified:

        for topic in p["topics"]:
            groups_topic[topic].append(p)

        groups_language[p["primary_language"]].append(p)
        groups_category[p["category"]].append(p)

        diff = p.get("difficulty") or "Unknown"
        groups_difficulty[diff].append(p)

        for pattern in p["patterns"]:
            groups_pattern[pattern].append(p)

    write_index(
        "v3-by-topic.md",
        "Problems by Topic",
        groups_topic
    )

    write_index(
        "v3-by-language.md",
        "Problems by Language",
        groups_language
    )

    write_index(
        "v3-by-category.md",
        "Problems by Category",
        groups_category
    )

    write_index(
        "v3-by-difficulty.md",
        "Problems by Difficulty",
        groups_difficulty
    )

    write_index(
        "v3-by-pattern.md",
        "Problems by Pattern",
        groups_pattern
    )

    # ---------- DASHBOARD ----------

    dashboard = [
        "# 📊 Classification V3 Dashboard",
        "",
        f"**Total Problems:** {len(classified)}",
        "",
        "## Categories",
        ""
    ]

    for k, v in sorted(categories.items()):
        dashboard.append(f"- **{k}:** {v}")

    dashboard += [
        "",
        "## Languages",
        ""
    ]

    for k, v in sorted(languages.items()):
        dashboard.append(f"- **{k}:** {v}")

    dashboard += [
        "",
        "## Difficulty",
        ""
    ]

    for k, v in sorted(difficulty.items()):
        dashboard.append(f"- **{k}:** {v}")

    dashboard += [
        "",
        "## Topics",
        ""
    ]

    for k, v in sorted(topics.items(), key=lambda x: (-x[1], x[0])):
        dashboard.append(f"- **{k}:** {v}")

    dashboard += [
        "",
        "## Patterns",
        ""
    ]

    for k, v in sorted(patterns.items(), key=lambda x: (-x[1], x[0])):
        dashboard.append(f"- **{k}:** {v}")

    (DATA / "CLASSIFICATION_V3_DASHBOARD.md").write_text(
        "\n".join(dashboard) + "\n",
        encoding="utf-8"
    )

    # ---------- CONSOLE ----------

    print()
    print("=" * 75)
    print("                 CLASSIFICATION V3")
    print("=" * 75)

    print(f"Total Problems : {len(classified)}")

    print()
    print("Categories:")
    for k, v in sorted(categories.items()):
        print(f"  {k:20} {v}")

    print()
    print("Languages:")
    for k, v in sorted(languages.items()):
        print(f"  {k:20} {v}")

    print()
    print("Difficulty:")
    for k, v in sorted(difficulty.items()):
        print(f"  {k:20} {v}")

    print()
    print("Topics:")
    for k, v in sorted(topics.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {k:25} {v}")

    print()
    print("Patterns:")
    for k, v in sorted(patterns.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {k:25} {v}")

    print()
    print("Generated:")
    print("  data/problems-v3.json")
    print("  data/CLASSIFICATION_V3_DASHBOARD.md")
    print("  indexes/v3-by-topic.md")
    print("  indexes/v3-by-language.md")
    print("  indexes/v3-by-category.md")
    print("  indexes/v3-by-difficulty.md")
    print("  indexes/v3-by-pattern.md")

    print("=" * 75)

if __name__ == "__main__":
    main()
