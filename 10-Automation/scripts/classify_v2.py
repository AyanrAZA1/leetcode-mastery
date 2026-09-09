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

SOLUTION_EXTS = {
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".rb": "Ruby",
    ".php": "PHP",
    ".sql": "SQL",
}

DIFFICULTIES = {"Easy", "Medium", "Hard"}

PATTERNS = {
    "Binary Search": [
        "binary search", "bisect", "lower_bound", "upper_bound",
        "search in rotated", "minimum in rotated"
    ],
    "Sliding Window": [
        "sliding window", "window", "substring", "subarray"
    ],
    "Two Pointers": [
        "two pointer", "two pointers", "left pointer", "right pointer",
        "3sum", "3-sum", "container with most water"
    ],
    "Fast Slow Pointers": [
        "fast slow", "fast and slow", "floyd", "cycle detection"
    ],
    "Prefix Sum": [
        "prefix sum", "prefix-sum", "cumulative sum", "running sum"
    ],
    "Hashing": [
        "hash map", "hashmap", "hash table", "hashtable", "frequency map"
    ],
    "Stack": [
        "monotonic stack", "stack", "parentheses", "valid parentheses"
    ],
    "Monotonic Stack": [
        "monotonic stack", "next greater", "next smaller",
        "daily temperatures", "largest rectangle"
    ],
    "Heap / Priority Queue": [
        "priority queue", "heap", "min heap", "max heap",
        "kth largest", "kth smallest"
    ],
    "BFS": [
        "breadth first", "breadth-first", "bfs", "level order"
    ],
    "DFS": [
        "depth first", "depth-first", "dfs"
    ],
    "Backtracking": [
        "backtracking", "subsets", "permutations", "combination sum"
    ],
    "Dynamic Programming": [
        "dynamic programming", "dp", "memoization",
        "tabulation", "knapsack", "longest common subsequence"
    ],
    "Greedy": [
        "greedy", "activity selection", "jump game"
    ],
    "Divide and Conquer": [
        "divide and conquer", "merge sort", "quick sort"
    ],
    "Union Find": [
        "union find", "disjoint set", "dsu"
    ],
    "Topological Sort": [
        "topological sort", "course schedule"
    ],
    "Trie": [
        "trie", "prefix tree"
    ],
    "Bit Manipulation": [
        "bit manipulation", "bitwise", "xor", "bit mask"
    ],
}

DATA_STRUCTURES = {
    "Array": ["array", "arrays"],
    "String": ["string", "strings", "substring"],
    "Hash Table": ["hash table", "hashmap", "hash map", "hashtable"],
    "Linked List": ["linked list", "linked-list"],
    "Stack": ["stack"],
    "Queue": ["queue"],
    "Deque": ["deque"],
    "Tree": ["tree", "binary tree"],
    "Binary Tree": ["binary tree"],
    "BST": ["binary search tree", "bst"],
    "Heap": ["heap", "priority queue"],
    "Graph": ["graph", "graphs"],
    "Trie": ["trie", "prefix tree"],
    "Matrix": ["matrix", "grid"],
    "Set": ["set", "hashset"],
}

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def slug_to_title(slug):
    return re.sub(r"[-_]+", " ", slug).strip().title()

def extract_id(name):
    m = re.match(r"^(\d{1,6})-", name)
    return m.group(1).zfill(4) if m else None

def read_problem_files(folder):
    files = []
    for p in folder.iterdir():
        if p.is_file():
            files.append(p)
    return files

def find_solution_files(files):
    return [p for p in files if p.suffix.lower() in SOLUTION_EXTS]

def parse_readme(readme):
    if not readme.exists():
        return "", {}

    text = readme.read_text(encoding="utf-8", errors="ignore")
    info = {}

    patterns = {
        "difficulty": [
            r"(?im)^\s*(?:difficulty|level)\s*[:\-]\s*(easy|medium|hard)\b",
            r"(?im)\b(easy|medium|hard)\b"
        ],
        "title": [
            r"(?im)^\s*#\s+(.+)$",
            r"(?im)^\*\*title\*\*\s*[:\-]\s*(.+)"
        ],
    }

    for p in patterns["title"]:
        m = re.search(p, text)
        if m:
            title = m.group(1).strip()
            title = re.sub(r"\s+#.*$", "", title).strip()
            if title:
                info["title"] = title
                break

    for p in patterns["difficulty"]:
        m = re.search(p, text)
        if m:
            value = m.group(1).capitalize()
            if value in DIFFICULTIES:
                info["difficulty"] = value
                break

    return text, info

def detect_language(solution_files):
    langs = []
    for p in solution_files:
        lang = SOLUTION_EXTS.get(p.suffix.lower())
        if lang:
            langs.append(lang)

    if not langs:
        return "Unknown"

    return Counter(langs).most_common(1)[0][0]

def detect_category(solution_files, text):
    if any(p.suffix.lower() == ".sql" for p in solution_files):
        return "SQL"

    lower = text.lower()

    if "sql" in lower and ("select " in lower or "from " in lower):
        return "SQL"

    return "DSA"

def score_matches(text, mapping):
    lower = text.lower()
    result = []

    for name, keywords in mapping.items():
        score = 0
        for kw in keywords:
            if kw.lower() in lower:
                score += 1

        if score:
            result.append((score, name))

    result.sort(reverse=True)
    return result

def detect_topics(text):
    matches = score_matches(text, DATA_STRUCTURES)
    return [name for score, name in matches[:5]]

def detect_patterns(text):
    matches = score_matches(text, PATTERNS)
    return [name for score, name in matches[:5]]

def infer_algorithm(title, text):
    combined = f"{title} {text}".lower()

    candidates = [
        ("Binary Search", ["binary search", "lower_bound", "upper_bound"]),
        ("Sliding Window", ["sliding window"]),
        ("Two Pointers", ["two pointers", "two pointer"]),
        ("Prefix Sum", ["prefix sum"]),
        ("Dynamic Programming", ["dynamic programming", "memoization", "tabulation"]),
        ("Backtracking", ["backtracking"]),
        ("Greedy", ["greedy"]),
        ("BFS", ["bfs", "breadth first"]),
        ("DFS", ["dfs", "depth first"]),
        ("Union Find", ["union find", "disjoint set"]),
        ("Topological Sort", ["topological sort"]),
        ("Heap", ["heap", "priority queue"]),
        ("Trie", ["trie"]),
        ("Divide and Conquer", ["divide and conquer"]),
        ("Bit Manipulation", ["bit manipulation", "bitwise"]),
    ]

    for name, keywords in candidates:
        if any(k in combined for k in keywords):
            return name

    return "Unknown"

def confidence_for(value, source):
    if not value or value == "Unknown" or value == []:
        return "low"

    if source in {"readme", "solution-extension", "folder-name"}:
        return "high"

    if source == "heuristic":
        return "medium"

    return "low"

def classify_problem(folder):
    files = read_problem_files(folder)
    solution_files = find_solution_files(files)

    readme = folder / "README.md"
    text, parsed = parse_readme(readme)

    problem_id = extract_id(folder.name)

    title = parsed.get("title")
    if not title:
        title = slug_to_title(
            re.sub(r"^\d{1,6}-", "", folder.name)
        )

    difficulty = parsed.get("difficulty", "Unknown")

    language = detect_language(solution_files)

    category = detect_category(solution_files, text)

    topics = detect_topics(f"{title}\n{text}")
    patterns = detect_patterns(f"{title}\n{text}")

    algorithm = infer_algorithm(title, text)

    # SQL classification
    sql_type = None
    if category == "SQL":
        sql_lower = text.lower()
        if "join" in sql_lower:
            sql_type = "JOIN"
        elif "group by" in sql_lower:
            sql_type = "GROUP BY"
        elif "window function" in sql_lower or "over(" in sql_lower:
            sql_type = "Window Functions"
        elif "subquery" in sql_lower or "nested query" in sql_lower:
            sql_type = "Subquery"
        elif "select" in sql_lower:
            sql_type = "SELECT / Filtering"

    metadata_path = folder / "metadata.json"
    old = load_json(metadata_path) if metadata_path.exists() else {}
    if not isinstance(old, dict):
        old = {}

    metadata = dict(old)

    metadata.update({
        "leetcode_id": problem_id,
        "title": title,
        "slug": folder.name,
        "category": category,
        "difficulty": difficulty,
        "language": language,
        "topics": topics,
        "patterns": patterns,
        "algorithm": algorithm,
        "solution_files": [p.name for p in solution_files],
    })

    if sql_type:
        metadata["sql_type"] = sql_type

    metadata["classification"] = {
        "difficulty": {
            "value": difficulty,
            "source": "readme" if parsed.get("difficulty") else "unknown",
            "confidence": confidence_for(
                difficulty,
                "readme" if parsed.get("difficulty") else "unknown"
            ),
        },
        "language": {
            "value": language,
            "source": "solution-extension",
            "confidence": confidence_for(language, "solution-extension"),
        },
        "category": {
            "value": category,
            "source": "solution-extension" if category == "SQL" else "heuristic",
            "confidence": "high" if category == "SQL" else "medium",
        },
        "topics": {
            "value": topics,
            "source": "heuristic",
            "confidence": "medium" if topics else "low",
        },
        "patterns": {
            "value": patterns,
            "source": "heuristic",
            "confidence": "medium" if patterns else "low",
        },
        "algorithm": {
            "value": algorithm,
            "source": "heuristic",
            "confidence": "medium" if algorithm != "Unknown" else "low",
        },
    }

    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    return metadata

def is_problem_folder(folder):
    if not re.match(r"^\d{1,6}-.+", folder.name):
        return False

    files = read_problem_files(folder)
    solutions = find_solution_files(files)

    return bool(solutions) or (folder / "README.md").exists()

def write_indexes(problems):
    by = {
        "difficulty": defaultdict(list),
        "language": defaultdict(list),
        "category": defaultdict(list),
        "topic": defaultdict(list),
        "pattern": defaultdict(list),
        "algorithm": defaultdict(list),
    }

    for p in problems:
        item = {
            "id": p["leetcode_id"],
            "title": p["title"],
            "slug": p["slug"],
            "path": p["slug"],
        }

        by["difficulty"][p["difficulty"]].append(item)
        by["language"][p["language"]].append(item)
        by["category"][p["category"]].append(item)
        by["algorithm"][p["algorithm"]].append(item)

        for topic in p.get("topics", []):
            by["topic"][topic].append(item)

        for pattern in p.get("patterns", []):
            by["pattern"][pattern].append(item)

    for kind, groups in by.items():
        clean = {
            key: sorted(
                value,
                key=lambda x: int(x["id"]) if str(x["id"]).isdigit() else 999999
            )
            for key, value in sorted(groups.items())
        }

        (INDEX / f"v2-by-{kind}.json").write_text(
            json.dumps(clean, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )

def write_dashboard(problems):
    total = len(problems)

    difficulty = Counter(p["difficulty"] for p in problems)
    language = Counter(p["language"] for p in problems)
    category = Counter(p["category"] for p in problems)

    unknown_difficulty = difficulty.get("Unknown", 0)
    unknown_language = language.get("Unknown", 0)

    lines = [
        "# LeetCode Mastery — Classification Dashboard",
        "",
        f"**Total recognized problems:** {total}",
        "",
        "## Difficulty",
        "",
        f"- Easy: {difficulty.get('Easy', 0)}",
        f"- Medium: {difficulty.get('Medium', 0)}",
        f"- Hard: {difficulty.get('Hard', 0)}",
        f"- Unknown: {unknown_difficulty}",
        "",
        "## Language",
        "",
    ]

    for k, v in language.most_common():
        lines.append(f"- {k}: {v}")

    lines += [
        "",
        "## Category",
        "",
    ]

    for k, v in category.most_common():
        lines.append(f"- {k}: {v}")

    lines += [
        "",
        "## Problems",
        "",
        "| ID | Problem | Difficulty | Category | Language | Algorithm | Patterns |",
        "|---:|---|---|---|---|---|---|",
    ]

    for p in sorted(
        problems,
        key=lambda x: int(x["leetcode_id"])
        if str(x["leetcode_id"]).isdigit() else 999999
    ):
        patterns = ", ".join(p.get("patterns", [])) or "—"
        lines.append(
            f"| {p['leetcode_id']} | "
            f"[{p['title']}]({p['slug']}/README.md) | "
            f"{p['difficulty']} | "
            f"{p['category']} | "
            f"{p['language']} | "
            f"{p['algorithm']} | "
            f"{patterns} |"
        )

    (DATA / "CLASSIFICATION_DASHBOARD.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

def main():
    print("=" * 70)
    print("        LEETCODE MASTERY — CLASSIFICATION ENGINE V2")
    print("=" * 70)

    problems = []

    folders = sorted(
        [p for p in ROOT.iterdir() if p.is_dir()],
        key=lambda p: p.name
    )

    for folder in folders:
        if not is_problem_folder(folder):
            continue

        try:
            metadata = classify_problem(folder)
            problems.append(metadata)
            print(
                f"[OK] {metadata['leetcode_id']} | "
                f"{metadata['title']} | "
                f"{metadata['difficulty']} | "
                f"{metadata['language']} | "
                f"{metadata['category']}"
            )
        except Exception as e:
            print(f"[ERROR] {folder.name}: {e}")

    problems.sort(
        key=lambda x: int(x["leetcode_id"])
        if str(x["leetcode_id"]).isdigit() else 999999
    )

    (DATA / "problems-v2.json").write_text(
        json.dumps(problems, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    write_indexes(problems)
    write_dashboard(problems)

    stats = {
        "total": len(problems),
        "difficulty": dict(Counter(p["difficulty"] for p in problems)),
        "language": dict(Counter(p["language"] for p in problems)),
        "category": dict(Counter(p["category"] for p in problems)),
        "topics": dict(
            Counter(
                topic
                for p in problems
                for topic in p.get("topics", [])
            )
        ),
        "patterns": dict(
            Counter(
                pattern
                for p in problems
                for pattern in p.get("patterns", [])
            )
        ),
        "algorithms": dict(
            Counter(p["algorithm"] for p in problems)
        ),
    }

    (DATA / "classification-v2-statistics.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    print()
    print("=" * 70)
    print("CLASSIFICATION V2 COMPLETE")
    print("=" * 70)
    print(f"Problems : {len(problems)}")
    print(f"Unknown difficulty : {stats['difficulty'].get('Unknown', 0)}")
    print(f"Unknown language   : {stats['language'].get('Unknown', 0)}")
    print(f"Topics             : {len(stats['topics'])}")
    print(f"Patterns           : {len(stats['patterns'])}")
    print(f"Algorithms         : {len(stats['algorithms'])}")
    print("=" * 70)

if __name__ == "__main__":
    main()
