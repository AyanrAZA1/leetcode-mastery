#!/usr/bin/env python3

import json
import re
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "10-Automation" / "data"

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

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def is_problem_folder(p):
    if not p.is_dir():
        return False
    if not re.match(r"^\d{1,6}-.+", p.name):
        return False

    return any(
        f.is_file() and f.suffix.lower() in SOLUTION_EXTS
        for f in p.iterdir()
    )

def get_solution_files(folder):
    return [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in SOLUTION_EXTS
    ]

def extract_id(name):
    m = re.match(r"^(\d+)-", name)
    return int(m.group(1)) if m else None

def extract_title(folder):
    readme = folder / "README.md"

    if readme.exists():
        text = readme.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        patterns = [
            r"^#\s+(?:\d+\s*[-—:]\s*)?(.+)$",
            r"^#\s+(.+)$",
        ]

        for pattern in patterns:
            m = re.search(
                pattern,
                text,
                flags=re.MULTILINE
            )

            if m:
                title = m.group(1).strip()
                title = re.sub(r"\s+#.*$", "", title)
                return title

    slug = re.sub(r"^\d+-", "", folder.name)
    return slug.replace("-", " ").title()

def analyze_folder(folder):
    files = get_solution_files(folder)

    languages = sorted({
        SOLUTION_EXTS[f.suffix.lower()]
        for f in files
    })

    return {
        "id": extract_id(folder.name),
        "slug": folder.name,
        "title": extract_title(folder),
        "path": str(folder.relative_to(ROOT)),
        "languages": languages,
        "solution_files": [f.name for f in files],
        "has_readme": (folder / "README.md").exists(),
        "file_count": len(files),
    }

def main():

    folders = sorted(
        p for p in ROOT.iterdir()
        if is_problem_folder(p)
    )

    problems = [
        analyze_folder(folder)
        for folder in folders
    ]

    ids = [
        p["id"]
        for p in problems
        if p["id"] is not None
    ]

    id_counter = Counter(ids)

    duplicates = {
        str(k): v
        for k, v in id_counter.items()
        if v > 1
    }

    missing_readme = [
        p["slug"]
        for p in problems
        if not p["has_readme"]
    ]

    missing_solution = [
        p["slug"]
        for p in problems
        if not p["solution_files"]
    ]

    unknown_id = [
        p["slug"]
        for p in problems
        if p["id"] is None
    ]

    language_counter = Counter()

    for p in problems:
        language_counter.update(p["languages"])

    report = {
        "total_problem_folders": len(problems),
        "unique_problem_ids": len(set(ids)),
        "duplicate_ids": duplicates,
        "missing_readme": missing_readme,
        "missing_solution": missing_solution,
        "unknown_id": unknown_id,
        "languages": dict(language_counter),
        "problems": problems,
    }

    output = DATA / "inventory-v3.json"

    output.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        ) + "\n",
        encoding="utf-8"
    )

    print()
    print("=" * 70)
    print("             PROBLEM INVENTORY V3")
    print("=" * 70)

    print(f"Problem folders : {len(problems)}")
    print(f"Unique IDs      : {len(set(ids))}")
    print(f"Duplicate IDs   : {len(duplicates)}")
    print(f"Missing README  : {len(missing_readme)}")
    print(f"Missing solution: {len(missing_solution)}")
    print(f"Unknown IDs     : {len(unknown_id)}")

    print()
    print("Languages:")
    for lang, count in sorted(language_counter.items()):
        print(f"  {lang:15} {count}")

    print()
    print("Problems discovered:")
    for p in problems:
        langs = ", ".join(p["languages"]) or "UNKNOWN"
        print(
            f"  {p['id']:>4} | "
            f"{langs:<15} | "
            f"{p['slug']}"
        )

    if duplicates:
        print()
        print("DUPLICATE IDS:")
        for k, v in duplicates.items():
            print(f"  {k}: {v}")

    if missing_readme:
        print()
        print("MISSING README:")
        for x in missing_readme:
            print(f"  {x}")

    if missing_solution:
        print()
        print("MISSING SOLUTION:")
        for x in missing_solution:
            print(f"  {x}")

    print()
    print(f"Report written to: {output}")
    print("=" * 70)

if __name__ == "__main__":
    main()
