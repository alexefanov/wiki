#!/usr/bin/env python3
"""Fix frontmatter in raw files according to AGENTS.md section 14.4."""

import re
import os

FILES = [
    # llm/ files
    r"raw\llm\Getting Started with Zettelkasten in Obsidian.md",
    r"raw\llm\Building my Personal LLM Wiki (Part 2) The Technical Implementation.md",
    r"raw\llm\Building my Personal LLM Wiki (Part 1) The Motivation.md",
    r"raw\llm\Build a Second Brain Using Obsidian – A Practical Guide for Engineers.md",
    r"raw\llm\llm-wiki.md",
    r"raw\llm\LLM Wiki v2 — extending Karpathy's LLM Wiki pattern with lessons from building agentmemory.md",
    r"raw\llm\Introduction to Obsidian Web Clipper.md",
    r"raw\llm\Zettelkasten и Obsidian ваш помощник в структурировании знаний.md",
    r"raw\llm\Zettelkasten и Obsidian — лучшие друзья вашей памяти и креативности.md",
    # Codexes
    r"raw\Арбитражный процессуальный кодекс Российской Федерации — Редакция от 15.12.2025.md",
    r"raw\Гражданский процессуальный кодекс Российской Федерации — Редакция от 09.04.2026.md",
    r"raw\Гражданский кодекс Российской Федерации (часть вторая) — Редакция от 24.06.2025.md",
    r"raw\Градостроительный кодекс Российской Федерации — Редакция от 23.03.2026.md",
    r"raw\Кодекс Российской Федерации об административных правонарушениях — Редакция от 07.04.2025.md",
    r"raw\Уголовно-процессуальный кодекс Российской Федерации — Редакция от 09.04.2026.md",
    # ФЗ
    r"raw\Федеральный закон от 31.05.2001 N 73-ФЗ — Редакция от 22.07.2024.md",
    r"raw\Федеральный закон от 30.12.2009 N 384-ФЗ.md",
    r"raw\Федеральный закон от 29.06.2015 N 162-ФЗ — Редакция от 30.12.2020.md",
    r"raw\Федеральный закон от 26.06.2008 N 102-ФЗ — Редакция от 08.08.2024.md",
    r"raw\Федеральный закон от 22.07.2008 N 123-ФЗ — Редакция от 31.07.2025.md",
    r"raw\Федеральный закон от 21.12.94 N 69-ФЗ — Редакция от 25.04.2026.md",
    r"raw\Федеральный закон от 21.07.97 N 116-ФЗ — Редакция от 08.08.2024.md",
    r"raw\Федеральный закон от 10.12.95 N 196-ФЗ — Редакция от 31.07.2025.md",
    # Misc
    r"raw\О техническом регулировании.md",
    r"raw\Иерархия нормативных документов.md",
    r"raw\Обзор норм о судебно-экспертной деятельности.md",
    r"raw\Бутырин. Теория и практика ССТЭ.md",
    r"raw\Об осуществлении замены и (или) восстановления отдельных элементов строительных конструкций зданий, сооружений, элементов систем инженерно-технического обеспечения и сетей инженерно-технического обеспечения при проведении текущего ремонта зданий.md",
]

BASE = r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База"


def strip_markdown(text):
    """Strip all markdown formatting from a string."""
    # Don't strip markdown links inside the main text... actually yes, strip everything
    # Remove bold/italic: **text** or __text__ or *text* or _text_
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    # Remove inline code
    text = re.sub(r'`(.+?)`', r'\1', text)
    # Remove wikilinks
    text = re.sub(r'\[\[(.+?)\]\]', r'\1', text)
    # Remove markdown links [text](url)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    return text


def clean_description(desc):
    """Remove SEO boilerplate from description."""
    # Strip " — с последними изменениями скачать на сайте Контур.Норматив"
    desc = re.sub(r' — с последними изменениями скачать на сайте Контур\.Норматив$', '', desc)
    desc = re.sub(r' — с последними изменениями скачать на сайте «Контур\.Норматив»$', '', desc)
    return desc.strip()


def fix_quotes(text):
    """Fix escaped and smart quotes."""
    # \" → "
    text = text.replace('\\"', '"')
    # Smart/curly quotes → regular
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u00ab', '"').replace('\u00bb', '"')
    return text


def parse_frontmatter(content):
    """Parse YAML frontmatter into a dict of key: value pairs."""
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        return None, content
    
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break
    
    if end_idx == -1:
        return None, content
    
    fm_lines = lines[1:end_idx]
    body = '\n'.join(lines[end_idx+1:])
    
    # Parse simple YAML (no nested structures except list items)
    fm = {}
    current_key = None
    current_list = None
    
    for line in fm_lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # Check for list item
        if stripped.startswith('- '):
            if current_key and current_list is not None:
                current_list.append(stripped[2:].strip().strip('"').strip("'"))
            continue
        
        # Key: value line
        match = re.match(r'^(\w+):\s*(.*)', line)
        if match:
            current_key = match.group(1)
            value = match.group(2).strip()
            
            if value == '' or value == '[]':
                fm[current_key] = [] if value == '[]' else None
                current_list = None
                continue
            
            if value.startswith('[') and value.endswith(']'):
                # Inline list
                items = [x.strip().strip('"').strip("'") for x in value[1:-1].split(',') if x.strip()]
                fm[current_key] = items
                current_list = None
                continue
            
            current_list = None
            
            # Remove quotes if present
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            
            fm[current_key] = value
    
    return fm, body


def build_frontmatter(fm, body_path):
    """Build new frontmatter string with only allowed fields."""
    allowed = {'source', 'created', 'title', 'description', 'tags'}
    
    result = {}
    
    # Copy allowed fields
    for key in allowed:
        if key in fm:
            if key == 'tags':
                # Filter out "clippings"
                tags = fm['tags']
                if isinstance(tags, list):
                    tags = [t for t in tags if t.lower().strip('"').strip("'").strip() != 'clippings']
                elif isinstance(tags, str):
                    tags_list = [t.strip().strip('"').strip("'") for t in tags.split(',')]
                    tags_list = [t for t in tags_list if t.lower() != 'clippings']
                    tags = tags_list
                else:
                    tags = None
                if tags and len(tags) > 0:
                    result['tags'] = tags
            else:
                result[key] = fm[key]
    
    # Special handling for files missing title
    if 'title' not in fm:
        if body_path and 'Обзор норм' in body_path:
            result['title'] = 'Обзор норм о судебно-экспертной деятельности'
        elif body_path and 'Бутырин' in body_path:
            result['title'] = 'Теория и практика судебной строительно-технической экспертизы'
    
    if 'description' not in fm:
        if body_path and 'Обзор норм' in body_path:
            result['description'] = 'Не нормативный документ. Использовать только как справочную информацию. Проверять на соответствие источникам.'
        elif body_path and 'Бутырин' in body_path:
            result['description'] = 'ОАО Издательский Дом Городец, 2006'
    
    # Build YAML string
    lines = ['---']
    for key in ('source', 'created', 'title', 'description', 'tags'):
        if key in result:
            val = result[key]
            if key == 'tags':
                lines.append('tags:')
                for t in val:
                    lines.append(f'  - "{t}"')
            else:
                # Clean up value
                val = str(val)
                val = fix_quotes(val)
                val = strip_markdown(val)
                
                if key in ('description',):
                    val = clean_description(val)
                
                lines.append(f'{key}: "{val}"')
    
    lines.append('---')
    return '\n'.join(lines)


def process_file(filepath):
    """Process a single file."""
    fullpath = os.path.join(BASE, filepath)
    
    with open(fullpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fm, body = parse_frontmatter(content)
    if fm is None:
        return f"NO FRONTMATTER: {filepath}"
    
    new_fm = build_frontmatter(fm, filepath)
    new_content = new_fm + '\n' + body
    
    # Normalize line endings
    new_content = new_content.replace('\r\n', '\n')
    
    with open(fullpath, 'w', encoding='utf-8', newline='') as f:
        f.write(new_content)
    
    return summarize_changes(filepath, fm, new_fm)


def summarize_changes(filepath, old_fm, new_fm_str):
    """Summarize what changed."""
    parts = []
    
    # Parse new_fm
    lines = new_fm_str.split('\n')
    new_fm = {}
    for line in lines:
        m = re.match(r'^(\w+):\s*(.*)', line)
        if m:
            new_fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
        elif line.strip().startswith('- '):
            if 'tags' not in new_fm:
                new_fm['tags'] = []
            new_fm['tags'].append(line.strip()[2:].strip().strip('"').strip("'"))
    
    removed = []
    for key in old_fm:
        if key not in ('source', 'created', 'title', 'description', 'tags'):
            if key != 'author' or old_fm[key] is not None:
                removed.append(key)
    
    if 'tags' in old_fm and 'tags' not in new_fm:
        parts.append("removed tags (clippings only)")
    
    if 'author' in old_fm:
        parts.append("removed author")
    if 'published' in old_fm:
        parts.append("removed published")
    for r in removed:
        if r not in ('author', 'published'):
            parts.append(f"removed {r}")
    
    if 'title' not in old_fm and 'title' in new_fm:
        parts.append("added title")
    
    if 'description' in old_fm:
        old_desc = str(old_fm.get('description', ''))
        new_desc = new_fm.get('description', '')
        if 'с последними изменениями' in old_desc:
            parts.append("cleaned SEO from description")
        if '"' in old_desc and '"' not in old_desc:
            pass  # check quotes
        old_clean = old_desc.replace('\\"', '').replace('\u201c', '').replace('\u201d', '').replace('\u00ab', '').replace('\u00bb', '')
        new_clean = new_desc.replace('\\"', '').replace('\u201c', '').replace('\u201d', '').replace('\u00ab', '').replace('\u00bb', '')
        if old_clean != new_clean and 'SEO' not in str(parts):
            if 'cleaned' not in str(parts):
                parts.append("cleaned description")
    
    if not parts:
        parts.append("no changes needed")
    
    return f"{os.path.basename(filepath)}: {', '.join(parts)}"


if __name__ == '__main__':
    results = []
    for f in FILES:
        result = process_file(f)
        results.append(result)
        print(result)
    
    print("\nDone! Processed", len(results), "files.")
