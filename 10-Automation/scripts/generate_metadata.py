import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

LANGUAGES = {
    ".java": "Java",
    ".cpp": "C++",
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".sql": "SQL",
}

def detect_language(folder):
    for file in folder.iterdir():
        if file.is_file() and file.suffix in LANGUAGES:
            return LANGUAGES[file.suffix]
    return None


def detect_id(name):
    match = re.match(r"^(\d+)-", name)
    return int(match.group(1)) if match else None


def detect_category(language):
    if language == "SQL":
        return "SQL"
    if language:
        return "DSA"
    return None


count = 0

for folder in ROOT.iterdir():

    if not folder.is_dir():
        continue

    # Only LeetCode-style numbered folders
    if not re.match(r"^\d+-", folder.name):
        continue

    metadata_file = folder / "metadata.json"

    # Never overwrite existing metadata
    if metadata_file.exists():
        continue

    problem_id = detect_id(folder.name)
    language = detect_language(folder)

    metadata = {
        "leetcode_id": problem_id,
        "slug": folder.name,
        "language": language,
        "category": detect_category(language),
        "difficulty": None,
        "topics": [],
        "patterns": [],
        "companies": [],
        "revision": {
            "status": "new",
            "attempts": 0,
            "last_reviewed": None,
            "next_review": None
        },
        "complexity": {
            "time": None,
            "space": None
        },
        "notes": ""
    }

    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    count += 1

print(f"Metadata generated for {count} problems.")
