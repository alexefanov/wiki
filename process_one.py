#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process ONE raw md file: update frontmatter per AGENTS.md 14.1.
Usage: python process_one.py <filename_in_raw>
"""
import os, re, sys, pathlib

RAW_DIR = pathlib.Path(__file__).parent / "raw"

def clean_val(s):
    s = s.strip()
    if s.startswith('"') and s.endswith('"'): s = s[1:-1]
    if s.startswith('"') and s.endswith('"'): s = s[1:-1]
    s = s.replace('\\"', '"').replace("\\'", "'").replace("\r", "")
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
    s = re.sub(r'_(.+?)_', r'\1', s)
    return s.strip()

def dedup(seq):
    seen = set()
    out = []
    for x in seq:
        x = x.strip()
        if x and x not in seen:
            seen.add(x); out.append(x)
    return out

def parse_fm(text):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return "", text, {}
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i; break
    if end is None:
        return "", text, {}
    yaml_block = "\n".join(lines[1:end])
    rest = "\n".join(lines[end+1:])
    result = {}
    for line in yaml_block.split("\n"):
        m = re.match(r'^(\w[\w_-]*)\s*:\s*(.*)', line)
        if m:
            v = m.group(2).strip()
            if v:
                result[m.group(1)] = clean_val(v)
            else:
                result[m.group(1)] = ""
    return yaml_block, rest, result

def first_year(s):
    m = re.search(r'(19\d{2}|20\d{2})', s)
    return m.group(1) if m else None

def extract_oks_udk_bbk(text):
    oks = udk = bbk = ""
    for line in text.split("\n")[:200]:
        m = re.search(r'(?:ОКС|МКС)\s+([\d\.\s]{3,30})(?:\s|$)', line)
        if m and not oks:
            c = m.group(1).strip().replace(" ", ".").split()[0] if m.group(1).strip() else ""
            c = re.sub(r'[^\d\.].*', '', c).rstrip('.')
            if c: oks = c
        m = re.search(r'УДК\s+([\d\.\/\:]{3,40})(?:\s|$)', line)
        if m and not udk:
            c = m.group(1).strip()
            c = re.sub(r'[^\d\.\/\:].*', '', c).rstrip('./:')
            if c: udk = c
        m = re.search(r'ББК\s+([\d\.]{3,20})(?:\s|$)', line)
        if m and not bbk:
            c = m.group(1).strip()
            c = re.sub(r'[^\d\.].*', '', c).rstrip('.')
            if c: bbk = c
    return oks, udk, bbk

TAG_MAP = {
    'бетон':'бетон', 'железобетон':'железобетон', 'арматур':'арматура',
    'сталь':'сталь', 'металл':'металл', 'древесин':'древесина',
    'камен':'камень', 'кирпич':'кирпич', 'раствор':'раствор',
    'цемент':'цемент', 'песок':'песок', 'коррози':'коррозия',
    'огнестойк':'огнестойкость', 'пожар':'пожар',
    'обследовани':'обследование', 'мониторинг':'мониторинг',
    'испытани':'испытания', 'контроль':'контроль',
    'измерени':'измерения', 'прочность':'прочность',
    'нагрузк':'нагрузки', 'фундамент':'фундаменты',
    'сварн':'сварка', 'неразруша':'неразрушающий',
    'ультразвук':'ультразвук', 'тепловизион':'тепловизия',
    'экспертиз':'экспертиза', 'судебн':'судебная',
    'нормировани':'нормирование', 'стандартизаци':'стандартизация',
    'метрологи':'метрология', 'термин':'термины',
    'ремонт':'ремонт', 'усилени':'усиление',
    'дефект':'дефекты', 'аварийн':'аварийное',
    'долговечность':'долговечность', 'качество':'качество',
    'безопасность':'безопасность',
}

def process_file(filepath):
    name = filepath.name
    stem = filepath.stem

    with open(filepath, "r", encoding="utf-8-sig") as f:
        raw = f.read()
    if raw.startswith('\ufeff'):
        raw = raw[1:]

    yaml_block, rest, existing = parse_fm(raw)
    old_title = existing.get("title", "")
    old_desc = existing.get("description", "")

    text_lower = (name + " " + raw[:3000]).lower()
    fname = name
    lower_fname = fname.lower()

    meta = {"type":"","number":"","name":"","title":"","description":"",
            "year":"","actualization_date":"","oks":"","udk":"","bbk":"","tags":[]}

    # --- Dates ---
    act_date = ""
    year_str = ""
    m_act = re.search(r'Редакция\s+от\s+(\d{2})\.(\d{2})\.(\d{4})', fname)
    if m_act:
        act_date = f"{m_act.group(3)}-{m_act.group(2)}-{m_act.group(1)}"
    m_fed = re.search(r'от\s+(\d{2})\.(\d{2})\.(\d{2,4})', fname)
    if m_fed:
        y = m_fed.group(3)
        if len(y) == 2:
            y = "19"+y if int(y) >= 50 else "20"+y
        year_str = f"{y}-{m_fed.group(2)}-{m_fed.group(1)}"
    if not year_str:
        m_dv = re.search(r'Дата\s+введения\s+(\d{4}-\d{2}-\d{2})', raw[:500])
        if m_dv:
            year_str = m_dv.group(1)
    if not year_str:
        y = first_year(fname)
        if y:
            year_str = f"{y}-01-01"
    meta["year"] = year_str
    meta["actualization_date"] = act_date if act_date else year_str

    # --- Type detection ---
    if stem.startswith("Иерархия"):
        meta.update(type="Справочник", name="Иерархия нормативных документов")
        meta["tags"] = ["классификация","аббревиатуры","строительство","нормативные_документы","иерархия"]
    elif stem.startswith("О техническом"):
        meta.update(type="ФЗ", number="184-ФЗ", name="О техническом регулировании", year="2002-12-27")
        meta["tags"] = ["техническое_регулирование","стандартизация","безопасность"]
    elif stem.startswith("Обзор норм"):
        meta.update(type="Обзор", name="Обзор норм о судебно-экспертной деятельности")
        meta["tags"] = ["судебная_экспертиза","обзор","процессуальные_нормы"]
    elif "Бутырин" in stem:
        meta.update(type="Монография", name="Теория и практика судебной строительно-технической экспертизы", year="2006-01-01")
        meta["tags"] = ["судебная_экспертиза","строительно-техническая","монография"]
    elif stem.startswith("Уголовно-процессуальный кодекс"):
        meta.update(type="Кодекс", name="Уголовно-процессуальный кодекс Российской Федерации")
        meta["tags"] = ["уголовный_процесс","судопроизводство","кодекс"]
    elif stem.startswith("Арбитражный процессуальный кодекс"):
        meta.update(type="Кодекс", number="95-ФЗ", name="Арбитражный процессуальный кодекс Российской Федерации")
        meta["tags"] = ["арбитражный_процесс","судопроизводство","кодекс"]
    elif stem.startswith("Градостроительный кодекс"):
        meta.update(type="Кодекс", number="190-ФЗ", name="Градостроительный кодекс Российской Федерации")
        meta["tags"] = ["градостроительство","строительство","кодекс"]
    elif stem.startswith("Гражданский процессуальный кодекс"):
        meta.update(type="Кодекс", name="Гражданский процессуальный кодекс Российской Федерации")
        meta["tags"] = ["гражданский_процесс","судопроизводство","кодекс"]
    elif stem.startswith("Гражданский кодекс"):
        meta.update(type="Кодекс", number="14-ФЗ", name="Гражданский кодекс Российской Федерации (часть вторая)")
        meta["tags"] = ["гражданское_право","кодекс"]
    elif stem.startswith("Кодекс Российской Федерации об административных правонарушениях"):
        meta.update(type="Кодекс", number="195-ФЗ", name="Кодекс Российской Федерации об административных правонарушениях")
        meta["tags"] = ["административные_правонарушения","кодекс"]
    elif "Федеральный закон" in stem:
        meta["type"] = "ФЗ"
        mn = re.search(r'[N№]\s*(\d+[А-Я]*)-ФЗ', fname)
        if mn: meta["number"] = mn.group(1)+"-ФЗ"
        mn2 = re.search(r'"([^"]+)"', raw[:500])
        if mn2: meta["name"] = mn2.group(1)
        else:
            parts = re.split(r'[—–-]', stem, 1)
            if len(parts) > 1: meta["name"] = parts[1].strip()
        meta["tags"] = ["федеральный_закон","нормативный_акт"]
    elif stem.startswith("Постановление Пленума Верховного Суда"):
        meta["type"] = "Постановление"
        mn = re.search(r'N\s*(\d+)', fname)
        if mn: meta["number"] = mn.group(1)
        meta["name"] = stem.split("—")[0].strip() if "—" in stem else stem
        meta["tags"] = ["постановление","верховный_суд","судебная_практика"]
    elif stem.startswith("Постановление Пленума ВАС РФ"):
        meta["type"] = "Постановление"
        mn = re.search(r'N\s*(\d+)', fname)
        if mn: meta["number"] = mn.group(1)
        meta["name"] = stem.split("—")[0].strip()
        meta["tags"] = ["постановление","вас_рф","судебная_практика"]
    elif stem.startswith("Постановление Правительства РФ"):
        meta["type"] = "Постановление"
        mn = re.search(r'N\s*(\d+)', fname)
        if mn: meta["number"] = mn.group(1)
        meta["name"] = stem.split("—")[0].strip()
        meta["tags"] = ["постановление","правительство_рф"]
    elif stem.startswith("Приказ"):
        meta["type"] = "Приказ"
        mn = re.search(r'N\s*(\d+[А-Я]*[пр]*)', fname)
        if mn: meta["number"] = mn.group(1)
        meta["name"] = stem.split("—")[0].strip() if "—" in stem else stem
        meta["tags"] = ["приказ"]
    elif stem.startswith("Письмо"):
        meta.update(type="Письмо", name=stem)
        meta["tags"] = ["письмо","разъяснение"]
    elif stem.startswith("МДС"):
        meta["type"] = "МДС"
        m = re.match(r'МДС\s+([\d\.\-]+(?:-\d{4})?)', stem)
        if m: meta["number"] = m.group(1)
        rest = stem[m.end():].strip().lstrip(" -.—") if m else stem[3:].strip()
        meta["name"] = rest.split("—")[0].split("(приняты")[0].split("(утв")[0].strip()
        meta["tags"] = ["методический_документ"]
    elif stem.startswith("Ведомственные строительные нормы") or stem.startswith("ВСН"):
        meta["type"] = "ВСН"
        m = re.search(r'ВСН\s+([\d\-]+)', fname)
        if m: meta["number"] = m.group(1)
        meta["name"] = stem.split("—")[0].strip()
        meta["tags"] = ["ведомственные_нормы"]
    elif stem.startswith("РД"):
        meta["type"] = "РД"
        m = re.match(r'РД\s+([\d\.\-]+)', stem)
        if m: meta["number"] = m.group(1)
        rest = stem[m.end():].strip().lstrip(" -.—") if m else stem[2:].strip()
        meta["name"] = rest.split("—")[0].split("(утв")[0].split('"')[0].strip()
        meta["tags"] = ["руководящий_документ"]
    elif stem.startswith("ОДМ"):
        meta["type"] = "ОДМ"
        m = re.match(r'ОДМ\s+([\d\.\-]+)', stem)
        if m: meta["number"] = m.group(1)
        rest = stem[m.end():].strip().lstrip(" -.—") if m else stem[3:].strip()
        meta["name"] = rest.split("—")[0].split("(издан")[0].split("(утв")[0].strip()
        meta["tags"] = ["методический_документ","дороги"]
    elif stem.startswith("СТО"):
        meta["type"] = "СТО"
        m = re.match(r'СТО\s+([\w\.\-]+)', stem)
        if m: meta["number"] = m.group(1)
        rest = stem[m.end():].strip().lstrip(" -.—") if m else stem[3:].strip()
        meta["name"] = rest.split("—")[0].split("(утв")[0].strip()
        meta["tags"] = ["стандарт_организации"]
    elif stem.startswith("МРР"):
        meta["type"] = "МРР"
        m = re.match(r'МРР\s+([\d\.\-]+)', stem)
        if m: meta["number"] = m.group(1)
        rest = stem[m.end():].strip().lstrip(" -.—") if m else stem[3:].strip()
        meta["name"] = rest.split("—")[0].strip()
        meta["tags"] = ["методика"]
    elif stem.startswith("Пособие"):
        meta["type"] = "Пособие"
        meta["name"] = stem.split("—")[0].strip()
        meta["tags"] = ["пособие","методика"]
    elif stem.startswith("Рекомендации") or stem.startswith("Руководство"):
        meta["type"] = "Рекомендации" if stem.startswith("Рекомендации") else "Руководство"
        meta["name"] = stem.split("—")[0].split("(утв")[0].strip()
        meta["tags"] = ["методика","рекомендации"]
    elif stem.startswith("Методические рекомендации") or stem.startswith("Методика") or stem.startswith("Определение"):
        meta["type"] = "Методика"
        meta["name"] = stem.split("—")[0].split("(утв")[0].split("- Справочники")[0].strip()
        meta["tags"] = ["методика","экспертиза"]
    elif stem.startswith("Классификатор"):
        meta["type"] = "Классификатор"
        meta["name"] = stem.split("—")[0].strip()
        meta["tags"] = ["классификатор","дефекты","строительство"]
    elif stem.startswith("Каталог"):
        meta["type"] = "Каталог"
        meta["name"] = stem.split("(утв")[0].strip()
        meta["tags"] = ["каталог","усиление","конструкции"]
    elif stem.startswith("СНиП"):
        meta["type"] = "СНиП"
        m = re.match(r'СНиП\s+([\d\.\-]+(?:-\d{2,4})?)', stem)
        if m: meta["number"] = m.group(1)
        rest = stem[m.end():].strip().lstrip(" -.—") if m else stem[4:].strip()
        meta["name"] = rest.split("—")[0].strip()
        meta["tags"] = ["строительные_нормы"]
    elif stem.startswith("СП") or stem.startswith("Свод правил") or stem.startswith("Свод"):
        meta["type"] = "СП"
        m = re.match(r'СП\s+([\d\.\-]+)', stem)
        if m: meta["number"] = m.group(1)
        rest = stem[m.end():].strip().lstrip(" -.—") if m else stem
        meta["name"] = rest.split("—")[0].split("(утв")[0].split("(ред")[0].strip()
        meta["name"] = re.sub(r'\s*\([^)]*$', '', meta["name"])
        meta["tags"] = ["свод_правил"]
    elif "ГОСТ" in stem:
        meta["type"] = "ГОСТ"
        m = re.match(r'ГОСТ\s+Р\s+ИСО\s+(\d[\d\.]*(?:-\d+)?)', stem)
        if m:
            meta["type"] = "ГОСТ Р ИСО"
            meta["number"] = m.group(1)
            rest = stem[m.end():].strip().lstrip(" -—.–")
            meta["name"] = rest
        else:
            m = re.match(r'ГОСТ\s+Р\s+(\d[\d\.]*(?:-\d+)?)', stem)
            if m:
                meta["type"] = "ГОСТ Р"
                meta["number"] = m.group(1)
                rest = stem[m.end():].strip().lstrip(" -—.–«»\"")
                meta["name"] = rest
            else:
                m = re.match(r'ГОСТ\s+(\d[\d\.]*(?:-\d+)?)', stem)
                if m:
                    meta["number"] = m.group(1)
                    rest = stem[m.end():].strip().lstrip(" -—.–«»\"")
                    meta["name"] = rest
                else:
                    meta["name"] = stem
        meta["tags"] = ["стандарт"]
    elif stem.startswith("СанПиН"):
        meta["type"] = "СанПиН"
        meta["name"] = stem.split("—")[0].strip()
        meta["tags"] = ["санитарные_нормы"]
    elif stem.startswith("Об осуществлении"):
        meta.update(type="Постановление", number="2120", name="Об осуществлении замены и (или) восстановления отдельных элементов строительных конструкций зданий, сооружений")
        meta["tags"] = ["постановление","правительство_рф","текущий_ремонт"]
    elif "ГОСТ" in stem:
        m = re.search(r'ГОСТ\s+(\d[\d\.]*(?:-\d{4})?)', stem)
        if m:
            meta["type"] = "ГОСТ"
            meta["number"] = m.group(1)
            meta["name"] = stem[:m.start()].strip().strip(".— ")
            meta["tags"] = ["стандарт"]
    elif "СП" in stem:
        m = re.search(r'(?:СП\s+)?([\d]{2,3}\.13330\.\d{4}|13-\d{3}-\d{4})', stem)
        if m:
            meta["type"] = "СП"
            meta["number"] = m.group(1)
            meta["name"] = stem[:m.start()].strip().strip(".— ")
            meta["tags"] = ["свод_правил"]
    else:
        meta["type"] = "Справочник"
        meta["name"] = stem.split("—")[0].strip()
        meta["tags"] = ["справочник"]

    # --- OKS/UDK/BBK ---
    oks, udk, bbk = extract_oks_udk_bbk(raw)
    if oks: meta["oks"] = oks
    if udk: meta["udk"] = udk
    if bbk: meta["bbk"] = bbk

    # --- Tags: enrich from content ---
    if len(meta["tags"]) <= 2:
        content_tags = []
        for pat, tag in TAG_MAP.items():
            if re.search(pat, text_lower) and tag not in content_tags:
                content_tags.append(tag)
        meta["tags"] = dedup(meta["tags"] + content_tags)
    meta["tags"] = dedup(meta["tags"])[:5]

    # --- Title ---
    if old_title:
        meta["title"] = old_title
    else:
        parts = [p for p in [meta.get("type",""), meta.get("number",""), meta.get("name","")] if p]
        meta["title"] = " ".join(parts) if parts else stem

    # --- Description ---
    if old_desc:
        meta["description"] = old_desc
    else:
        meta["description"] = meta.get("name", stem)

    # --- Actualization default ---
    if not meta["actualization_date"] and meta["year"]:
        meta["actualization_date"] = meta["year"]

    # --- Build frontmatter ---
    keys = ["type","number","name","title","description","year",
            "actualization_date","oks","udk","bbk","tags"]
    lines = ["---"]
    for k in keys:
        v = meta.get(k)
        if v is None or v == "" or (isinstance(v,list) and not v):
            continue
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                if item: lines.append(f"  - {item}")
        else:
            vs = str(v)
            if any(c in vs for c in ": #{}[]&*!|>%@`"):
                vs = vs.replace("\\", "\\\\").replace('"', '\\"')
                vs = f'"{vs}"'
            lines.append(f"{k}: {vs}")
    lines.append("---")

    new_fm = "\n".join(lines)
    rest2 = rest.lstrip("\n")
    new_content = new_fm + "\n" + rest2

    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)

    return meta

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_one.py <filename>")
        sys.exit(1)
    fname = sys.argv[1]
    fp = RAW_DIR / fname
    if not fp.exists():
        print(f"File not found: {fp}")
        sys.exit(1)
    meta = process_file(fp)
    print(f"OK: {fname}")
    print(f"  type={meta.get('type','')} number={meta.get('number','')}")
    print(f"  name={meta.get('name','')[:60]}")
    print(f"  year={meta.get('year','')} actualization={meta.get('actualization_date','')}")
    print(f"  oks={meta.get('oks','')} udk={meta.get('udk','')} bbk={meta.get('bbk','')}")
    print(f"  tags={meta.get('tags','')}")
