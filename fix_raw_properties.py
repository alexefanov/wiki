#!/usr/bin/env python3
"""Clean raw/ frontmatter per AGENTS.md 14.4 schema.

Keeps ONLY: source, created, title, description, tags.
Removes field if value is empty/missing.
Handles indented YAML lists, extra fields, multi-line values, escaped quotes.
"""

import re, sys
from pathlib import Path

RAW = Path(r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw")
ALLOWED = {"source", "created", "title", "description", "tags"}

# Regex to strip markdown: **bold**, `code`, [[wikilinks]], [links](url), _italic_
MD_RE = re.compile(r"\[{2}.+?\]{2}|\[.+?\]\(.+?\)|[*_]{2,}|`{1,3}")

# Curly/smart quotes replacements
SMART_QUOTES = str.maketrans({
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"',
    "\u2018": "'", "\u2019": "'", "\u201a": "'",
    "\u00ab": '"', "\u00bb": '"',
})


def strip_md(s: str) -> str:
    s = MD_RE.sub("", s)
    s = s.translate(SMART_QUOTES)
    s = re.sub(r'\\([\'"])', r'\1', s)
    s = re.sub(r'\\"', '"', s)
    s = re.sub(r"\\'", "'", s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def parse_fm(text: str):
    """Return (fm_dict, body_start) or (None, 0) if no frontmatter.

    Handles list values (indented ``- item``), quoted scalars,
    unquoted scalars, empty keys.
    """
    if not text.startswith("---\n"):
        return None, 0
    end = text.find("\n---\n", 4)
    if end == -1:
        # try end of file
        end = text.find("\n---", 4)
        if end == -1:
            return None, 0
        end = end + 4
    else:
        end = end + 5  # len("\n---\n")

    block = text[4:end-5] if text[end-5:end-4] == "\n" else text[4:end-4]

    fm = {}
    current_key = None
    current_list = None

    for line in block.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Indented list item:  "- value"
        list_match = re.match(r"^\s+-\s+(.+)$", line)
        if list_match and current_key is not None:
            val = list_match.group(1).strip().strip('"').strip("'")
            if current_list is not None:
                current_list.append(val)
            else:
                # Scalar was set, convert to list
                current_list = [fm[current_key], val]
                fm[current_key] = current_list
            continue

        # Non-indented list item
        bare_list_match = re.match(r"^-\s+(.+)$", line)
        if bare_list_match and current_key is not None:
            val = bare_list_match.group(1).strip().strip('"').strip("'")
            if current_list is not None:
                current_list.append(val)
            else:
                current_list = [val]
                fm[current_key] = current_list
            continue

        current_list = None

        # Key: value
        kv_match = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if kv_match:
            current_key = kv_match.group(1)
            val = kv_match.group(2).strip()
            if val == "":
                fm[current_key] = ""
            elif (val.startswith('"') and val.endswith('"')) or \
                 (val.startswith("'") and val.endswith("'")):
                fm[current_key] = val[1:-1]
            else:
                fm[current_key] = val
            continue

        current_key = None

    return fm, end


def write_fm(path: Path, fm: dict, body: str):
    """Write frontmatter preserving order: source, created, title, description, tags."""
    lines = ["---"]
    for k in ("title", "description", "source", "created"):
        if k in fm and fm[k]:
            v = str(fm[k])
            if '"' in v:
                v = v.replace('"', '\\"')
            lines.append(f'{k}: "{v}"')
    if fm.get("tags"):
        lines.append("tags:")
        for t in fm["tags"]:
            t = str(t).strip()
            if '"' in t:
                t = t.replace('"', '\\"')
            lines.append(f'  - "{t}"')
    lines.append("---")

    new_text = "\n".join(lines) + "\n" + body
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)


def clean_val(v):
    if isinstance(v, str):
        return strip_md(v.strip())
    return strip_md(str(v))


def process_file(path: Path) -> str | None:
    """Process a single raw file, return change description or None."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    orig = text

    fm, body_start = parse_fm(text)

    if fm is None:
        name = path.stem
        fm = {"title": name, "description": name}
        body = text
        write_fm(path, fm, body)
        return f"created fm {path.name}"

    body = text[body_start:] if body_start < len(text) else ""

    # Clean title
    raw_title = str(fm.get("title", "")).strip()
    if not raw_title or raw_title == "?":
        raw_title = path.stem

    title = clean_val(raw_title)

    # Clean description
    raw_desc = str(fm.get("description", "")).strip()
    if not raw_desc or raw_desc == path.stem or raw_desc == title:
        # Extract from body
        first_line = body.strip().split("\n")[0] if body.strip() else ""
        first_line = strip_md(first_line).strip().rstrip(".")
        desc = first_line if first_line else title
    else:
        desc = clean_val(raw_desc)

    desc = strip_md(desc)

    # Source
    source = clean_val(fm["source"]) if fm.get("source") else ""

    # Created
    created_val = fm.get("created", "")
    created = clean_val(created_val) if created_val else ""

    # Tags
    raw_tags = fm.get("tags", [])
    if isinstance(raw_tags, str):
        raw_tags = [raw_tags]
    tags = []
    for t in raw_tags:
        t = strip_md(str(t)).strip()
        if t and t.lower() != "clippings":
            tags.append(t)

    # Build clean fm
    clean = {}
    clean["title"] = title
    clean["description"] = desc
    if source:
        clean["source"] = source
    if created:
        clean["created"] = created
    if tags:
        clean["tags"] = tags

    # Check for changes
    changes = []
    for k in ("title", "description", "source", "created"):
        old = str(fm.get(k, ""))
        new = str(clean.get(k, ""))
        if old != new:
            changes.append(k)

    old_tags = [str(t).strip() for t in fm.get("tags", [])]
    new_tags = [str(t).strip() for t in clean.get("tags", [])]
    if old_tags != new_tags:
        changes.append("tags")

    if "author" in fm:
        changes.append("author removed")
    if "published" in fm:
        changes.append("published removed")

    if not changes:
        return None

    write_fm(path, clean, body)
    clean_desc = " ".join(sorted(set(changes)))
    return f"{clean_desc}: {path.name}"


def main():
    files = sorted(RAW.rglob("*.md"))
    processed = []
    unchanged = 0
    for f in files:
        msg = process_file(f)
        if msg:
            processed.append(msg)
        else:
            unchanged += 1

    for p in processed:
        print(p)

    print(f"\n=== Total: {len(files)}, Changed: {len(processed)}, Unchanged: {unchanged} ===")


if __name__ == "__main__":
    main()
