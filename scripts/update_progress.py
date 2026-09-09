#!/usr/bin/env python3

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

difficulty = {"Easy":0,"Medium":0,"Hard":0}
languages = {"Java":0,"C++":0,"SQL":0}
total = 0

for ext in ["*.java","*.cpp","*.sql"]:
    for f in ROOT.rglob(ext):
        if "08-Templates" in str(f):
            continue
        total += 1

        txt = f.read_text(errors="ignore")

        if "Difficulty: Easy" in txt:
            difficulty["Easy"] += 1
        elif "Difficulty: Medium" in txt:
            difficulty["Medium"] += 1
        elif "Difficulty: Hard" in txt:
            difficulty["Hard"] += 1

        if ext=="*.java":
            languages["Java"] += 1
        elif ext=="*.cpp":
            languages["C++"] += 1
        else:
            languages["SQL"] += 1

progress = f"""# 📊 LeetCode Progress

## Overall

| Category | Solved |
|---|---:|
| Total Problems | {total} |

## Difficulty

| Difficulty | Solved |
|---|---:|
| 🟢 Easy | {difficulty["Easy"]} |
| 🟡 Medium | {difficulty["Medium"]} |
| 🔴 Hard | {difficulty["Hard"]} |

## Languages

| Language | Problems |
|---|---:|
| Java | {languages["Java"]} |
| C++ | {languages["C++"]} |
| SQL | {languages["SQL"]} |

_Last Updated Automatically._
"""

(ROOT/"PROGRESS.md").write_text(progress)
print("Updated PROGRESS.md")
