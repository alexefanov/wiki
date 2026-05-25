import re, yaml, os, sys

ALLOWED_KEYS = {'title', 'description', 'source', 'created', 'tags'}
REMOVE_TAGS = {'clippings'}
SEO_JUNK_PATTERNS = [
    r'\s*[—\-]\s*с последними изменениями скачать на сайте Контур\.Норматив',
    r'\s*[—\-]\s*Редакция от \d{2}\.\d{2}\.\d{4}',
    r'\s*\|\s*НАДЗОР-ИНФО:\s*Сообщество экспертов России',
    r'\s*\|\s*НАДЗОР-ИНФО[^|]*$',
]
SMART_QUOTES = {
    '\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'",
    '\u00ab': '"', '\u00bb': '"', '\u201e': '"', '\u201f': '"',
}

def fix_escaped_quotes(s):
    """Fix \"text\" -> "text" and other quote issues"""
    s = s.replace('\\"', '"')
    s = s.replace("\\'", "'")
    for k, v in SMART_QUOTES.items():
        s = s.replace(k, v)
    return s

def strip_markdown(s):
    """Strip markdown from string: **bold**, __bold__, `code`, [[wikilink]], [text](url), _italic_, *italic*"""
    # Remove wikilinks [[text]] -> text
    s = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', s)
    # Remove markdown links [text](url) -> text
    s = re.sub(r'\[([^\]]*)\]\([^)]+\)', r'\1', s)
    # Remove **bold** and __bold__
    s = re.sub(r'\*{2}([^*]+)\*{2}', r'\1', s)
    s = re.sub(r'_{2}([^_]+)_{2}', r'\1', s)
    # Remove `code`
    s = re.sub(r'`([^`]+)`', r'\1', s)
    # Remove _italic_ and *italic* (single, careful not to strip underscores in text)
    # Only remove when there's a word boundary or non-word char
    s = re.sub(r'(?<!\w)_(?!_)([^_]+)_(?!_)(?!\w)', r'\1', s)
    s = re.sub(r'(?<!\w)\*(?!\*)([^*]+)\*(?!\*)(?!\w)', r'\1', s)
    return s

def clean_description(s):
    """Clean SEO junk from description"""
    for pat in SEO_JUNK_PATTERNS:
        s = re.sub(pat, '', s)
    return s.strip()

def clean_yaml_value(v):
    """Clean a YAML value string"""
    v = fix_escaped_quotes(v)
    v = strip_markdown(v)
    v = clean_description(v)
    v = v.strip()
    return v

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file has frontmatter
    if not content.startswith('---'):
        print(f"  SKIP: no frontmatter")
        return False

    # Split frontmatter from body
    # Find second ---
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"  SKIP: malformed frontmatter")
        return False

    fm_text = parts[1].strip()
    body = parts[2]

    # Parse YAML
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        print(f"  YAML ERROR: {e}")
        return False

    if not isinstance(fm, dict):
        print(f"  SKIP: frontmatter is not a dict: {type(fm)}")
        return False

    # Build new frontmatter
    new_fm = {}
    
    # title and description: always include if present
    for key in ('title', 'description'):
        if key in fm and fm[key] is not None:
            val = str(fm[key])
            val = clean_yaml_value(val)
            if val:
                new_fm[key] = val

    # source and created: keep only if exist and non-empty
    for key in ('source', 'created'):
        if key in fm and fm[key] is not None:
            val = str(fm[key]).strip()
            if val:
                new_fm[key] = val

    # tags: keep only if non-empty after removing clippings
    if 'tags' in fm and fm['tags'] is not None:
        tags = fm['tags']
        if isinstance(tags, list):
            cleaned = [str(t).strip() for t in tags if str(t).strip().lower() not in REMOVE_TAGS]
            cleaned = [t for t in cleaned if t]
            if cleaned:
                new_fm['tags'] = cleaned
        elif isinstance(tags, str):
            t = tags.strip()
            if t.lower() not in REMOVE_TAGS and t:
                new_fm['tags'] = [t]

    # Write back
    new_fm_text = yaml.dump(new_fm, allow_unicode=True, default_flow_style=False, sort_keys=False).strip()
    
    # Ensure tags list is formatted properly (yaml.dump uses - item format)
    # Reconstruct
    result = '---\n' + new_fm_text + '\n---\n' + body

    # Preserve original line endings
    if '\r\n' in content:
        result = result.replace('\n', '\r\n')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(result)

    changes = []
    old_keys = set(fm.keys()) if fm else set()
    kept = set(new_fm.keys())
    removed = old_keys - kept - {'title', 'description'}  # don't report title/desc as removed if we kept them
    # Actually let's just report what changed
    added_keys = kept - old_keys
    removed_keys = old_keys - kept
    if removed_keys:
        changes.append(f"removed: {', '.join(sorted(removed_keys))}")
    if added_keys:
        changes.append(f"added: {', '.join(sorted(added_keys))}")
    if 'tags' in old_keys and 'tags' in new_fm:
        old_tags = set(str(t).strip().lower() for t in (fm['tags'] if isinstance(fm['tags'], list) else [fm['tags']]))
        new_tags = set(str(t).strip().lower() for t in new_fm['tags'])
        if old_tags != new_tags:
            removed_t = old_tags - new_tags
            if REMOVE_TAGS & old_tags:
                changes.append("removed clippings from tags")
    if not changes:
        changes.append("cleaned values")
    
    print(f"  OK: {', '.join(changes)}")
    return True


files = [
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Ведомственные строительные нормы ВСН 58-88 (р) Положение об организации и проведении реконструкции, ремонта и технического обслуживания зданий, объектов коммунального и социально-культурного назначения — Редакция от 23.11.1988.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Постановление Правительства РФ от 16.02.2008 N 87 — Редакция от 21.10.2025.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Постановление Пленума Верховного Суда РФ от 26.06.2008 N 13 — Редакция от 09.02.2012.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Постановление Пленума ВАС РФ от 04.04.2014 N 23 — Редакция от 04.04.2014.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Пособие по практическому выявлению пригодности к восстановлению поврежденных строительных конструкций зданий и сооружений и способам их оперативного усиления.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Пособие по обследованию строительных конструкций зданий.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Пособие к МГСН 2.07-01 Обследование и мониторинг при строительстве и реконструкции зданий и подземных сооружений.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Письмо Министерства строительства и жилищно-коммунального хозяйства РФ от 4 декабря 2017 г. № 53435-ОГ08 О применении положений СП 112.13330.2011 «СНиП 21-01-97 Пожарная безопасность зданий и сооружений».md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Приказ Минтруда РФ от 11.12.2020 N 883Н — Редакция от 29.04.2025.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Приказ Минстроя России от 19.12.2024 N 883пр.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\РД 22-01-97. Требования к проведению оценки безопасности эксплуатации производственных зданий и сооружений поднадзорных промышленных производств и объектов (обследования строительных конструкций специализированными организациями) (утв. АОЗТ ЦНИИ.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\РД 153-34.1-21.326-2001 «Методические указания по обследованию строительных конструкций производственных зданий и сооружений тепловых электростанций. Часть 1. Железобетонные и бетонные конструкции».md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ОДМ 218.4.002-2008. Руководство по проведению мониторинга состояния эксплуатируемых мостовых сооружений (утв. распоряжением Росавтодора от 24.06.2008 N 261-р).md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ОДМ 218.3.042-2014. Отраслевой дорожный методический документ. Рекомендации по определению параметров и назначению категорий дефектов при оценке технического состояния мостовых сооружений на автомобильных дорогах. Каталог дефектов в мостовых соо.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ОДМ 218.3.014-2011. Отраслевой дорожный методический документ. Методика оценки технического состояния мостовых сооружений на автомобильных дорогах (издан на основании Распоряжения Росавтодора от 17.11.2011 N 883-р).md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ОДМ 218.2.044-2014. Отраслевой дорожный методический документ. Рекомендации по выполнению приборных и инструментальных измерений при оценке технического состояния мостовых сооружений на автомобильных дорогах (издан на основании Распоряжения Роса.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Методические рекомендации. Методика оценки остаточного ресурса несущих конструкций зданий и сооружений.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Методика определения содержания хлоридов в железобетонных конструкциях мостовых сооружений (утв. Распоряжением Минтранса РФ от 09.10.2002 N ОС-857-р).md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\МРР 2.2.07-98 Методика проведения обследований зданий и сооружений при их реконструкции и перепланировке.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\МДС 21-1.98 Предотвращение распространения пожара. Пособие к СНиП 21-01-97 Пожарная безопасность зданий и сооружений  НАДЗОР-ИНФО Сообщество экспертов России.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\МДС 13-20.2004.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\МДС 12-4.2000 Положение о порядке расследования причин аварий зданий и сооружений, их частей и конструктивных элементов на территории Российской Федерации.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\МДС 11-17.2004. Правила обследования зданий, сооружений и комплексов богослужебного и вспомогательного назначения (приняты и рекомендованы к применению Письмом Госстроя РФ от 20.04.2004 N ЛБ-25979).md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Классификатор основных видов дефектов в строительстве и промышленности строительных материалов — Редакция от 17.11.1993.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Каталог конструктивных решений по усилению и восстановлению строительных конструкций зданий и сооружений (утв. ОАО ЦНИИПромзданий 24.12.2008).md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Определение стоимости восстановления зданий и сооружений, поврежденных пожаром - Справочники и нормативы  Недвижимость  Методические рекомендации для экспертов.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Определение причин возникновения и развития дефектов в каменных конструкциях - Справочники и нормативы  Недвижимость  Методические рекомендации для экспертов.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Определение качества работ, выполненных при устройстве гипсокартонных перегородок на металлическом каркасе - Справочники и нормативы  Недвижимость  Методические рекомендации для экспертов.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Определение видов, объемов, качества и стоимости строительно-монтажных и специальных работ по возведению, ремонту (реконструкции) строительных объектов - Справочники и нормативы  Недвижимость  Методические рекомендации для экспертов.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Рекомендации по оценке надежности строительных конструкций зданий и сооружений по внешним признакам.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Рекомендации по определению технического состояния ограждающих конструкций при реконструкции промышленных зданий.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Рекомендации по обследованию стальных конструкций производственных зданий.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Рекомендации по обследованию и оценке технического состояния крупнопанельных и каменных зданий (утв. ЦНИИСК им. В.А. Кучеренко Госстроя СССР 28.07.1987).md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Рекомендации по обследованию зданий и сооружений, поврежденных пожаром.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Руководство по обеспечению долговечности железобетонных конструкций предприятий черной металлургии при их реконструкции и восстановлении.md",
]

print(f"Processing {len(files)} files...")
success = 0
for f in files:
    short = os.path.basename(f)
    print(f"\n{short}")
    if not os.path.exists(f):
        print(f"  NOT FOUND")
        continue
    if process_file(f):
        success += 1

print(f"\nDone: {success}/{len(files)} files updated")
