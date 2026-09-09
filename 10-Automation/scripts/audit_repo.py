import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]

LANG_EXTENSIONS = {
    ".java": "Java",
    ".cpp": "C++",
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".sql": "SQL",
    ".c": "C",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
}

stats = {
    "total_files": 0,
    "solution_files": 0,
    "readme_files": 0,
    "languages": Counter(),
    "problem_directories": 0,
    "topic_directories": 0,
}

problems = []

for path in ROOT.rglob("*"):

    if not path.is_file():
        continue

    # Ignore Git internals
    if ".git" in path.parts:
        continue

    stats["total_files"] += 1

    if path.name == "README.md":
        stats["readme_files"] += 1

    if path.suffix in LANG_EXTENSIONS:
        language = LANG_EXTENSIONS[path.suffix]
        stats["solution_files"] += 1
        stats["languages"][language] += 1

    # LeetCode problem directories generally start with a number
    if path.parent.name[:1].isdigit():
        problem_dir = path.parent

        if problem_dir not in [p["path"] for p in problems]:
            problems.append({
                "name": problem_dir.name,
                "path": str(problem_dir.relative_to(ROOT)),
                "files": []
            })

for problem in problems:
    problem_path = ROOT / problem["path"]

    for file in problem_path.iterdir():
        if file.is_file():
            problem["files"].append(file.name)

stats["problem_directories"] = len(problems)

# Topic directories
topics_dir = ROOT / "Topics"

if topics_dir.exists():
    stats["topic_directories"] = sum(
        1 for p in topics_dir.iterdir() if p.is_dir()
    )

output = {
    "repository": ROOT.name,
    "stats": {
        "total_files": stats["total_files"],
        "solution_files": stats["solution_files"],
        "readme_files": stats["readme_files"],
        "problem_directories": stats["problem_directories"],
        "topic_directories": stats["topic_directories"],
        "languages": dict(stats["languages"]),
    },
    "problems": problems,
}

output_file = ROOT / "10-Automation/data/repo-audit.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("=" * 50)
print("LEETCODE REPOSITORY AUDIT")
print("=" * 50)
print(f"Repository       : {ROOT.name}")
print(f"Total files      : {stats['total_files']}")
print(f"Solution files   : {stats['solution_files']}")
print(f"README files     : {stats['readme_files']}")
print(f"Problem folders  : {stats['problem_directories']}")
print(f"Topic folders    : {stats['topic_directories']}")
print()
print("Languages:")
for language, count in stats["languages"].most_common():
    print(f"  {language:15} {count}")
print()
print(f"Generated: {output_file}")
