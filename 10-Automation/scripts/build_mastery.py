import json,re
from pathlib import Path
from collections import Counter,defaultdict

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"10-Automation/data"
INDEX=ROOT/"10-Automation/indexes"
DATA.mkdir(parents=True,exist_ok=True)
INDEX.mkdir(parents=True,exist_ok=True)

EXT={".java":"Java",".cpp":"C++",".py":"Python",".js":"JavaScript",
     ".ts":"TypeScript",".sql":"SQL",".go":"Go",".rs":"Rust"}

DIFF=["Easy","Medium","Hard"]

TOPIC_MAP={
"array":"Array","string":"String","hash-table":"Hash Table",
"linked-list":"Linked List","stack":"Stack","queue":"Queue",
"heap":"Heap","graph":"Graph","binary-tree":"Binary Tree",
"binary-search":"Binary Search","backtracking":"Backtracking",
"dynamic-programming":"Dynamic Programming","greedy":"Greedy",
"divide-and-conquer":"Divide and Conquer","sorting":"Sorting",
"prefix-sum":"Prefix Sum","two-pointers":"Two Pointers",
"sliding-window":"Sliding Window","matrix":"Matrix",
"math":"Math","database":"Database","bit-manipulation":"Bit Manipulation",
"simulation":"Simulation"
}

PATTERNS={
"binary-search":["binary search"],
"sliding-window":["sliding window"],
"two-pointers":["two pointers"],
"prefix-sum":["prefix sum"],
"greedy":["greedy"],
"backtracking":["backtracking"],
"dynamic-programming":["dynamic programming","dp"],
"divide-and-conquer":["divide and conquer"],
"fast-slow-pointers":["fast slow","fast and slow"],
"monotonic-stack":["monotonic stack"],
"merge-intervals":["merge intervals"]
}

def problem_id(name):
    m=re.match(r"^(\d+)-(.+)$",name)
    return int(m.group(1)) if m else None

def title_from_slug(name):
    m=re.match(r"^\d+-(.+)$",name)
    if not m:return name
    return m.group(1).replace("-"," ").title()

def solution_language(folder):
    for f in folder.iterdir():
        if f.is_file() and f.suffix in EXT:
            return EXT[f.suffix]
    return None

def readme(folder):
    f=folder/"README.md"
    try:return f.read_text(encoding="utf-8",errors="ignore")
    except:return ""

def extract_difficulty(text):
    low=text.lower()
    for d in DIFF:
        if re.search(r"\b"+d.lower()+r"\b",low):
            return d
    return None

def extract_topics(text):
    low=text.lower()
    found=[]
    for key,name in TOPIC_MAP.items():
        if key in low:
            found.append(name)
    return sorted(set(found))

def infer_patterns(text):
    low=text.lower()
    found=[]
    for name,terms in PATTERNS.items():
        if any(t in low for t in terms):
            found.append(name.replace("-"," ").title())
    return sorted(set(found))

problems=[]
languages=Counter()
difficulties=Counter()
topics=Counter()
patterns=Counter()
categories=Counter()

for folder in sorted(ROOT.iterdir()):
    if not folder.is_dir() or not re.match(r"^\d+-",folder.name):
        continue

    pid=problem_id(folder.name)
    if pid is None: continue

    text=readme(folder)
    lang=solution_language(folder)
    diff=extract_difficulty(text)
    tops=extract_topics(text)
    pats=infer_patterns(text)

    category="SQL" if lang=="SQL" else "DSA"

    # Prefer explicit topic data when available
    topic_json=[]
    for p in ROOT.glob("Topics/*/problems.json"):
        try:
            data=json.loads(p.read_text(encoding="utf-8"))
            blob=json.dumps(data).lower()
            slug=folder.name.lower()
            if slug in blob:
                topic_json.append(p.parent.name)
        except: pass

    for t in topic_json:
        if t in TOPIC_MAP:
            tops.append(TOPIC_MAP[t])

    tops=sorted(set(tops))

    metadata={
        "leetcode_id":pid,
        "title":title_from_slug(folder.name),
        "slug":folder.name,
        "language":lang,
        "category":category,
        "difficulty":diff,
        "topics":tops,
        "patterns":pats,
        "companies":[],
        "revision":{
            "status":"new",
            "attempts":0,
            "last_reviewed":None,
            "next_review":None
        },
        "complexity":{"time":None,"space":None},
        "notes":""
    }

    (folder/"metadata.json").write_text(
        json.dumps(metadata,indent=2,ensure_ascii=False),
        encoding="utf-8"
    )

    problems.append(metadata)

    if lang: languages[lang]+=1
    if diff: difficulties[diff]+=1
    categories[category]+=1
    for t in tops: topics[t]+=1
    for p in pats: patterns[p]+=1

# Master database
problems.sort(key=lambda x:x["leetcode_id"])

(DATA/"problems.json").write_text(
    json.dumps(problems,indent=2,ensure_ascii=False),
    encoding="utf-8"
)

# Generic index writer
def write_index(name,items):
    (INDEX/name).write_text(
        json.dumps(items,indent=2,ensure_ascii=False),
        encoding="utf-8"
    )

write_index("by-difficulty.json",{
    d:[p["leetcode_id"] for p in problems if p["difficulty"]==d]
    for d in DIFF
})

write_index("by-language.json",{
    l:[p["leetcode_id"] for p in problems if p["language"]==l]
    for l in sorted(languages)
})

write_index("by-category.json",{
    c:[p["leetcode_id"] for p in problems if p["category"]==c]
    for c in sorted(categories)
})

write_index("by-topic.json",{
    t:[p["leetcode_id"] for p in problems if t in p["topics"]]
    for t in sorted(topics)
})

write_index("by-pattern.json",{
    p:[x["leetcode_id"] for x in problems if p in x["patterns"]]
    for p in sorted(patterns)
})

# Statistics
stats={
    "total_problems":len(problems),
    "categories":dict(categories),
    "languages":dict(languages),
    "difficulty":dict(difficulties),
    "topics":dict(topics),
    "patterns":dict(patterns),
    "missing_difficulty":[p["leetcode_id"] for p in problems if not p["difficulty"]],
    "missing_topics":[p["leetcode_id"] for p in problems if not p["topics"]]
}

(DATA/"statistics.json").write_text(
    json.dumps(stats,indent=2,ensure_ascii=False),
    encoding="utf-8"
)

# Progress
lines=[
"# 📊 LeetCode Progress\n",
"> Automatically generated by the Mastery Engine.\n",
"## Overall\n",
"| Category | Solved |\n|---|---:|"
]

for c in sorted(categories):
    lines.append(f"| {c} | {categories[c]} |")

lines += [
f"| **Total** | **{len(problems)}** |",
"",
"## Difficulty",
"| Difficulty | Solved |",
"|---|---:|"
]

for d in DIFF:
    lines.append(f"| {d} | {difficulties[d]} |")

lines += [
"",
"## Languages",
"| Language | Problems |",
"|---|---:|"
]

for l in sorted(languages):
    lines.append(f"| {l} | {languages[l]} |")

lines += [
"",
"## Topics",
"| Topic | Problems |",
"|---|---:|"
]

for t,n in sorted(topics.items(),key=lambda x:(-x[1],x[0])):
    lines.append(f"| {t} | {n} |")

(ROOT/"PROGRESS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

print("="*60)
print("LEETCODE MASTERY ENGINE COMPLETE")
print("="*60)
print("Problems :",len(problems))
print("Languages:",dict(languages))
print("Category :",dict(categories))
print("Difficulty:",dict(difficulties))
print("Topics   :",len(topics))
print("Patterns :",len(patterns))
print("Missing difficulty:",len(stats["missing_difficulty"]))
print("Missing topics:",len(stats["missing_topics"]))
print()
print("Generated:")
print("  10-Automation/data/problems.json")
print("  10-Automation/data/statistics.json")
print("  10-Automation/indexes/*")
print("  */metadata.json")
print("  PROGRESS.md")
