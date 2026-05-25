#!/usr/bin/env python3
"""Fix frontmatter in raw files per AGENTS.md section 14.4 schema."""

import re
import yaml
import os

FILES = [
    r"raw\СП 79.13330.2012. Свод правил. Мосты и трубы. Правила обследований и испытаний. Актуализированная редакция СНиП 3.06.07-86 (утв. Приказом Минрегиона России от 30.06.2012 N 273) (ред. от 22.11.2019).md",
    r"raw\СП 64.13330.2017. Свод правил. Деревянные конструкции. Актуализированная редакция СНиП II-25-80(утв. Приказом Минстроя России от 27.02.2017 N 129пр)(ред. от 28.12.2023).md",
    r"raw\СП 63.13330.2018. Свод правил. Бетонные и железобетонные конструкции. Основные положения. СНиП 52-01-2003 (утв. и введен в действие Приказом Минстрой России от 19.12.2018 N 832пр) (ред. от 20.12.2021).md",
    r"raw\СП 54.13330.2022. Свод правил. Здания жилые многоквартирные. СНиП 31-01-2003(утв. и введен в действие Приказом Минстроя России от 13.05.2022 N 361пр).md",
    r"raw\СП 50.13330.2024. Свод правил. Тепловая защита зданий. Актуализированная редакция СНиП 23-02-2003(утв. и введен в действие Приказом Минстроя России от 15.05.2024 N 327пр).md",
    r"raw\СП 48.13330.2019 Организация строительства.md",
    r"raw\СП 427.1325800.2018. Свод правил. Каменные и армокаменные конструкции. Методы усиления (утв. Приказом Минстроя России от 19.12.2018 N 829пр) (ред. от 09.08.2023).md",
    r"raw\СП 372.1325800.2018. Свод правил. Здания жилые многоквартирные. Правила эксплуатации(утв. и введен в действие Приказом Минстроя России от 18.01.2018 N 27пр)(ред. от 21.12.2022).md",
    r"raw\СП 349.1325800.2017.md",
    r"raw\СП 329.1325800.2017. Свод правил. Здания и сооружения. Правила обследования после пожара (утв. и введен в действие Приказом Минстроя России от 30.10.2017 N 1490пр).md",
    r"raw\СП 305.1325800.2017. Свод правил. Здания и сооружения. Правила проведения геотехнического мониторинга при строительстве (утв. и введен в действие Приказом Минстроя России от 17.10.2017 N 1435пр) (ред. от 17.10.2023).md",
    r"raw\СП 24.13330.2021. Свод правил. Свайные фундаменты. СНиП 2.02.03-85(утв. и введен в действие Приказом Минстроя России от 14.12.2021 N 926пр)(ред. от 13.09.2023).md",
    r"raw\СП 22.13330.2016. Свод правил. Основания зданий и сооружений. Актуализированная редакция СНиП 2.02.01-83 (утв. Приказом Минстроя России от 16.12.2016 N 970пр) (ред. от 07.12.2023).md",
    r"raw\СП 20.13330.2016. Свод правил. Нагрузки и воздействия. Актуализированная редакция СНиП 2.01.07-85 (утв. Приказом Минстроя России от 03.12.2016 N 891пр) (ред. от 05.09.2024).md",
    r"raw\СП 16.13330.2017. Свод правил. Стальные конструкции. Актуализированная редакция СНиП II-23-81(утв. Приказом Минстроя России от 27.02.2017 N 126пр)(ред. от 09.12.2024).md",
    r"raw\СП 15.13330.2020. Свод правил. Каменные и армокаменные конструкции. СНиП II-22-81(утв. Приказом Минстроя России от 30.12.2020 N 902пр)(ред. от 21.12.2023).md",
    r"raw\СП 126.13330.2017. Свод правил. Геодезические работы в строительстве. СНиП 3.01.03-84(утв. и введен в действие Приказом Минстроя России от 24.10.2017 N 1469пр)(ред. от 26.12.2024).md",
    r"raw\Свод правил. Здания и сооружения. Правила эксплуатации. Основные положения. СП 255.1325800.2016 — Редакция от 19.05.2023.md",
    r"raw\Свод правил. Здания жилые. Правила проектирования капитального ремонта. СП 368.1325800.2017 — Редакция от 30.12.2020.md",
    r"raw\СНиП 3.04.03-85 Актуализированная редакция СП 72.13330.2016 Защита строительных конструкций и сооружений от коррозии  3 04 03 85   72 13330 2016.md",
    r"raw\Правила обследования несущих строительных конструкций зданий и сооружений. СП 13-102-2003 — Редакция от 21.08.2003.md",
    r"raw\Защита строительных конструкций от коррозии. Актуализированная редакция СНиП 2.03.11-85. СП 28.13330.2017 — Редакция от 08.05.2024.md",
    r"raw\СТО НОСТРОЙНОП 2.9.142-2014. Стандарт организации. Восстановление и повышение несущей способности кирпичных стен. Проектирование и строительство. Правила, контроль выполнения и требования к результатам работ (утв. и введен в действие Протоколом.md",
]

ALLOWED_KEYS = {'source', 'created', 'title', 'description', 'tags'}
SEO_JUNK = [
    r' — с последними изменениями скачать на сайте Контур\.Норматив',
    r' — Скачать на сайте Контур\.Норматив',
    r' с последними изменениями скачать на сайте Контур\.Норматив',
    r' скачать на сайте Контур\.Норматив',
    r' — с последними изменениями',
]

def strip_markdown(s):
    """Strip all markdown formatting from string."""
    if not isinstance(s, str):
        return s
    # Remove **bold**
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
    # Remove __bold__
    s = re.sub(r'__(.+?)__', r'\1', s)
    # Remove *italic*
    s = re.sub(r'\*(.+?)\*', r'\1', s)
    # Remove _italic_
    s = re.sub(r'(?<!\*)_(.+?)_(?!\*)', r'\1', s)
    # Remove `code`
    s = re.sub(r'`(.+?)`', r'\1', s)
    # Remove [[wikilinks]]
    s = re.sub(r'\[\[(.+?)\]\]', r'\1', s)
    # Remove [links](url) - keep text
    s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)
    return s

def fix_quotes(s):
    """Fix escaped and smart/curly quotes."""
    if not isinstance(s, str):
        return s
    # Fix escaped quotes: \"text\" -> "text"
    s = s.replace('\\"', '"')
    s = s.replace("\\'", "'")
    # Fix smart/curly quotes
    s = s.replace('\u201c', '"').replace('\u201d', '"')
    s = s.replace('\u2018', "'").replace('\u2019', "'")
    s = s.replace('\u00ab', '"').replace('\u00bb', '"')
    return s

def clean_description(s):
    """Remove SEO junk from description."""
    if not isinstance(s, str):
        return s
    for junk in SEO_JUNK:
        s = re.sub(junk, '', s, flags=re.IGNORECASE)
    s = s.strip()
    return s

def process_file(filepath):
    base = os.path.join(r'C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База', filepath)
    if not os.path.exists(base):
        return f"NOT FOUND: {filepath}"

    with open(base, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not fm_match:
        return f"NO FRONTMATTER: {filepath}"

    fm_raw = fm_match.group(1)
    body = content[fm_match.end():]

    # Parse YAML
    try:
        fm = yaml.safe_load(fm_raw)
    except yaml.YAMLError as e:
        return f"YAML ERROR: {filepath}: {e}"

    if not isinstance(fm, dict):
        return f"NOT DICT: {filepath}"

    changes = []

    # Filter allowed keys
    new_fm = {}
    for k in ALLOWED_KEYS:
        if k in fm:
            v = fm[k]
            if k == 'tags':
                # Process tags
                if isinstance(v, list):
                    # Remove 'clippings' and empty strings
                    v = [t for t in v if t and t.lower() != 'clippings']
                    if v:
                        # Clean markdown from each tag
                        v = [strip_markdown(fix_quotes(str(t))) for t in v]
                        new_fm['tags'] = v
                    # else: drop empty tags field
            else:
                # String fields
                if v is not None:
                    v = str(v)
                    v = fix_quotes(v)
                    v = strip_markdown(v)
                    if k == 'description':
                        v = clean_description(v)
                    if k == 'title':
                        # Clean up title too
                        pass
                    new_fm[k] = v

    # Check if there were keys removed
    removed = [k for k in fm if k not in ALLOWED_KEYS]
    if removed:
        changes.append(f"removed keys: {removed}")

    # Check tags changes
    if 'tags' in fm and 'tags' not in new_fm:
        changes.append("removed tags (empty or only 'clippings')")
    elif 'tags' in fm and 'tags' in new_fm:
        old_tags = [t for t in fm['tags'] if t and t.lower() != 'clippings']
        if old_tags != new_fm['tags']:
            changes.append("cleaned tags")

    # Check old vs new value changes
    for k in new_fm:
        old_v = fm.get(k)
        if old_v is not None:
            old_str = str(old_v)
            if old_str != new_fm[k]:
                changes.append(f"changed {k}")

    # Write new frontmatter
    new_yaml = yaml.dump(new_fm, allow_unicode=True, default_flow_style=False, sort_keys=False).strip()

    # YAML dump might add trailing spaces or format inline lists - let's ensure proper formatting
    # Re-dump to ensure clean formatting
    new_content = "---\n" + new_yaml + "\n---\n" + body

    with open(base, 'w', encoding='utf-8') as f:
        f.write(new_content)

    changes_str = ', '.join(changes) if changes else 'no changes'
    return f"OK: {filepath} [{changes_str}]"

def main():
    results = []
    for f in FILES:
        result = process_file(f)
        print(result)
        results.append(result)
    print(f"\n--- Summary: {len([r for r in results if r.startswith('OK')])} OK, {len([r for r in results if 'NOT FOUND' in r])} not found, {len([r for r in results if 'ERROR' in r])} errors out of {len(FILES)} ---")

if __name__ == '__main__':
    main()
