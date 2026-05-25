#!/usr/bin/env python3
"""Analyze frontmatter of all raw files to understand scope."""

import os, re
from pathlib import Path

RAW = Path(r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw")
ALLOWED = {"source", "created", "title", "description", "tags"}

def parse_fm(text):
    if not text.startswith("---\n"):
        return None, 0
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, 0
    block = text[4:end]
    fm = {}
    key = None
    for line in block.split("\n"):
        if not line.strip():
            continue
        if line.startswith("- ") and key is not None:
            fm[key].append(line[2:].strip().strip('"'))
        elif ":" in line:
            k, _, v = line.partition(":")
            key = k.strip()
            val = v.strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            fm[key] = val
            if key == "tags":
                fm[key] = []
        else:
            key = None
    return fm, end + 6

files = sorted(RAW.rglob("*.md"))

stats = {
    "total": len(files),
    "has_fm": 0,
    "extra_fields": {},
    "has_clippings": 0,
    "has_escaped_quotes": 0,
    "has_markdown_in_desc": 0,
    "has_h1_question": 0,
    "missing_title": 0,
    "missing_desc": 0,
}

for f in files:
    with open(f, "r", encoding="utf-8") as fh:
        text = fh.read()
    
    fm, _ = parse_fm(text)
    if fm is None:
        continue
    
    stats["has_fm"] += 1
    
    if fm.get("title", "").strip() == "?" or fm.get("title", "").strip() == "":
        stats["missing_title"] += 1
    
    desc = fm.get("description", "")
    if "скачать" in desc.lower() or not desc.strip():
        stats["missing_desc"] += 1
    
    if re.search(r'\\["\']', desc):
        stats["has_escaped_quotes"] += 1
    
    if re.search(r'\[{2}|\[.+?\]\(|[*_]{2}|`', desc):
        stats["has_markdown_in_desc"] += 1
    
    if text.count("# ?") > 0:
        stats["has_h1_question"] += 1
    
    if "tags" in fm and isinstance(fm["tags"], list):
        for t in fm["tags"]:
            if "clippings" in t.lower():
                stats["has_clippings"] += 1
                break
    
    for k in fm:
        if k not in ALLOWED:
            stats["extra_fields"][k] = stats["extra_fields"].get(k, 0) + 1

print(f"Total files: {stats['total']}")
print(f"With frontmatter: {stats['has_fm']}")
print(f"Missing/trivial title: {stats['missing_title']}")
print(f"Missing/SEO description: {stats['missing_desc']}")
print(f"Escaped quotes in desc: {stats['has_escaped_quotes']}")
print(f"Markdown in desc: {stats['has_markdown_in_desc']}")
print(f"Has # ? in body: {stats['has_h1_question']}")
print(f"Has clippings tag: {stats['has_clippings']}")
print(f"Extra fields: {stats['extra_fields']}")
