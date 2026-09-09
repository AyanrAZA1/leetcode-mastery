#!/usr/bin/env python3

import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]

extensions = Counter()
problems = []

for p in ROOT.iterdir():
    if not p.is_dir():
        continue

    name = p.name

    if not name[:1].isdigit():
        continue

    files = [x for x in p.iterdir() if x.is_file()]

    if not files:
        continue

    for f in files:
        extensions[f.suffix.lower() or "[no extension]"] += 1

    problems.append({
        "id": name.split("-", 1)[0],
        "slug": name,
        "files": len(files),
        "has_readme": (p / "README.md").exists(),
        "has_metadata": (p / "metadata.json").exists(),
    })

result = {
    "problem_count": len(problems),
    "extensions": dict(extensions),
    "problems": sorted(problems, key=lambda x: int(x["id"]))
}

out = ROOT / "10-Automation" / "data" / "repo-audit.json"
out.parent.mkdir(parents=True, exist_ok=True)

out.write_text(
    json.dumps(result, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8"
)

print("=" * 60)
print("REPOSITORY AUDIT")
print("=" * 60)
print("Problem folders:", len(problems))
print()
print("File types:")
for k, v in extensions.most_common():
    print(f"{k:20} {v}")
print()
print("Audit saved:", out)
