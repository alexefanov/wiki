#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update frontmatter (YAML properties) in raw/*.md files (except raw/llm/).

Reads existing title/description, derives type/number/name/year/... from
filename and content, preserves existing content, writes back UTF-8 no BOM.
"""

import os
import re
import pathlib

RAW_DIR = pathlib.Path(r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw")
LLM_DIR = RAW_DIR / "llm"

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _clean_yaml_value(s: str) -> str:
    """Strip outer whitespace, unescape common issues, remove markdown."""
    s = s.strip()
    # strip surrounding double quotes if any
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    # strip escaped quotes
    s = s.replace('\\"', '"').replace("\\'", "'")
    # remove leftover \r
    s = s.replace("\r", "")
    # remove markdown **bold**
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
    # remove markdown _italic_
    s = re.sub(r'_(.+?)_', r'\1', s)
    return s.strip()

def _dedup_tags(tags):
    seen = set()
    out = []
    for t in tags:
        t = t.strip()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out

def _make_date(year_str: str, month: int = 1, day: int = 1) -> str:
    """Normalise to YYYY-MM-DD."""
    year_str = year_str.strip()
    if not year_str:
        return ""
    # if already full date
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', year_str)
    if m:
        return year_str
    # YYYY only
    m = re.match(r'(\d{4})$', year_str)
    if m:
        # sanity check: year roughly 1900-2030
        y = int(m.group(1))
        if 1900 <= y <= 2030:
            return f"{y:04d}-{month:02d}-{day:02d}"
    return ""

# ---------------------------------------------------------------------------
# existing frontmatter parser (no pyyaml)
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str):
    """Return (yaml_block, rest_of_text, frontmatter_dict)."""
    lines = text.split("\n")
    # must start with ---
    if not lines or lines[0].strip() != "---":
        return "", text, {}

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return "", text, {}

    yaml_block = "\n".join(lines[1:end_idx])
    rest = "\n".join(lines[end_idx + 1:])

    # crude YAML key: value parser
    result = {}
    current_key = None
    current_list = []
    in_list = False
    for line in yaml_block.split("\n"):
        # list item
        list_match = re.match(r'^\s*-\s+(.+)$', line)
        if list_match:
            in_list = True
            current_list.append(_clean_yaml_value(list_match.group(1)))
            continue
        # key: value
        kv_match = re.match(r'^(\w[\w_]*)\s*:\s*(.*)$', line)
        if kv_match:
            if in_list and current_key:
                result[current_key] = current_list
                current_list = []
                in_list = False
            current_key = kv_match.group(1)
            val = kv_match.group(2).strip()
            if val:
                # unquote
                val = _clean_yaml_value(val)
                result[current_key] = val
                current_key = None
            else:
                # key with no value yet (possible list following)
                result[current_key] = ""
            continue
        # continuation line (indented)
        cont_match = re.match(r'^\s+(.+)$', line)
        if cont_match and current_key and not in_list and result.get(current_key) == "":
            result[current_key] = _clean_yaml_value(cont_match.group(1))
        if cont_match and current_key and in_list and result.get(current_key) == "":
            result[current_key] = _clean_yaml_value(cont_match.group(1))

    if in_list and current_key:
        result[current_key] = current_list

    return yaml_block, rest, result

# ---------------------------------------------------------------------------
# OKS / UDK / BBK extraction from content
# ---------------------------------------------------------------------------

def _extract_oks_udk_bbk(text: str):
    """Scan first 300 lines for OKS/UDK/BBK codes."""
    oks, udk, bbk = "", "", ""
    lines = text.split("\n")[:300]
    for line in lines:
        # OKS: e.g. "ОКС 91.080.40" or "ОКС 93 010 00"
        m = re.search(r'ОКС\s+([\d\.\s]{2,30}?)(?:\s|$)', line)
        if m and not oks:
            code = m.group(1).strip().replace(" ", ".")
            # clean trailing non-digit/non-dot
            code = re.sub(r'[^\d\.].*$', '', code)
            code = re.sub(r'\.+$', '', code)
            if code:
                oks = code
        # UDK: e.g. "УДК 624.04:624.012.3/.4" or "УДК 69.059"
        m = re.search(r'УДК\s+([\d\.\/\:]{2,40}?)(?:\s|$)', line)
        if m and not udk:
            code = m.group(1).strip()
            code = re.sub(r'[^\d\.\/\:].*$', '', code)
            code = re.sub(r'[\.\:\/]+$', '', code)
            if code:
                udk = code
        # BBK: e.g. "ББК 38.4"
        m = re.search(r'ББК\s+([\d\.]{2,20}?)(?:\s|$)', line)
        if m and not bbk:
            code = m.group(1).strip()
            code = re.sub(r'[^\d\.].*$', '', code)
            code = re.sub(r'\.+$', '', code)
            if code:
                bbk = code
        # also МКС (similar to OKS)
        if not oks:
            m = re.search(r'МКС\s+([\d\.]{2,20}?)(?:\s|$)', line)
            if m:
                code = m.group(1).strip()
                code = re.sub(r'[^\d\.].*$', '', code)
                code = re.sub(r'\.+$', '', code)
                if code:
                    oks = code
    return oks, udk, bbk

# ---------------------------------------------------------------------------
# tag generation
# ---------------------------------------------------------------------------

# Content-area keyword → tag mapping (priority: specific first)
KEYWORD_TAGS = {
    # materials
    r'бетон': 'бетон',
    r'железобетон': 'железобетон',
    r'арматур': 'арматура',
    r'сталь': 'сталь',
    r'металл': 'металл',
    r'древесин': 'древесина',
    r'камен': 'камень',
    r'кирпич': 'кирпич',
    r'раствор': 'раствор',
    r'цемент': 'цемент',
    r'песок': 'песок',
    r'стекло': 'стекло',
    r'коррози': 'коррозия',
    r'теплоизоляци': 'теплоизоляция',
    r'пожар': 'пожар',
    r'огнестойк': 'огнестойкость',
    # techniques
    r'обследовани': 'обследование',
    r'мониторинг': 'мониторинг',
    r'испытани': 'испытания',
    r'контроль': 'контроль',
    r'измерени': 'измерения',
    r'деформаци': 'деформации',
    r'прочность': 'прочность',
    r'нагрузк': 'нагрузки',
    r'фундамент': 'фундаменты',
    r'свайн': 'сваи',
    r'грунт': 'грунты',
    r'восстановлени': 'восстановление',
    r'усилени': 'усиление',
    r'ремонт': 'ремонт',
    r'реконструкци': 'реконструкция',
    r'эксплуатаци': 'эксплуатация',
    r'восстановление': 'восстановление',
    r'дефект': 'дефекты',
    r'экспертиз': 'экспертиза',
    r'судебн': 'судебная',
    r'нормировани': 'нормирование',
    r'стандартизаци': 'стандартизация',
    r'метрологи': 'метрология',
    r'термин': 'термины',
    r'сварн': 'сварка',
    r'тензорезистор': 'тензорезисторы',
    r'неразруша': 'неразрушающий',
    r'ультразвук': 'ультразвук',
    r'тепловизион': 'тепловизия',
    r'геодезическ': 'геодезия',
    r'геотехническ': 'геотехника',
    r'проектировани': 'проектирование',
    r'строительство': 'строительство',
    r'безопасность': 'безопасность',
    r'охрана труда': 'охрана_труда',
    r'мост': 'мосты',
    r'фундамент': 'фундаменты',
    r'долговечность': 'долговечность',
    r'качество': 'качество',
    r'аварийн': 'аварийное',
    r'пожарная безопасность': 'пожарная_безопасность',
}

def _generate_tags(fname: str, text: str, doc_type: str, name: str) -> list:
    """Generate 3-5 single-word tags based on content keywords."""
    lower_text = (fname + " " + text[:5000]).lower()

    # domain-specific tags based on document type
    domain_tags = []
    if doc_type in ("ГОСТ", "ГОСТ Р", "ГОСТ Р ИСО"):
        domain_tags.append("стандарт")
    elif doc_type == "СП":
        domain_tags.append("свод_правил")
    elif doc_type == "СНиП":
        domain_tags.append("строительные_нормы")
    elif doc_type in ("ФЗ", "Кодекс", "Постановление", "ПП", "Приказ"):
        domain_tags.append("нормативный_акт")
    elif doc_type == "МДС":
        domain_tags.append("методический_документ")
    elif doc_type in ("РД", "ОДМ"):
        domain_tags.append("руководящий_документ")
    elif doc_type == "ВСН":
        domain_tags.append("ведомственные_нормы")
    elif doc_type == "МРР":
        domain_tags.append("методика")
    elif doc_type == "СТО":
        domain_tags.append("стандарт_организации")

    # content-area tags
    content_tags = []
    for pattern, tag in KEYWORD_TAGS.items():
        if re.search(pattern, lower_text):
            if tag not in content_tags:
                content_tags.append(tag)

    # combine, dedup, limit to 5
    combined = _dedup_tags(domain_tags + content_tags)

    # ensure no duplicates with type abbreviation
    type_lower = doc_type.lower().replace(" ", "_")
    combined = [t for t in combined if t != type_lower]

    # if too few, add general construction tags
    if len(combined) < 3:
        general_tags = ["строительство", "конструкции", "нормативный"]
        for g in general_tags:
            if g not in combined:
                combined.append(g)
            if len(combined) >= 5:
                break

    return combined[:5]

# ---------------------------------------------------------------------------
# main metadata derivation logic
# ---------------------------------------------------------------------------

def _first_year_in(s: str):
    """Return first 4-digit year 19xx or 20xx found, or None."""
    m = re.search(r'(19\d{2}|20\d{2})', s)
    return m.group(1) if m else None

def derive_metadata(fname_stem: str, text: str):
    """
    Derive type, number, name, year, actualization_date, title from filename + content.
    Returns dict with keys matching frontmatter schema.
    """
    meta = {
        "type": "",
        "number": "",
        "name": "",
        "title": "",
        "year": "",
        "actualization_date": "",
        "oks": "",
        "udk": "",
        "bbk": "",
        "tags": [],
    }

    fname = fname_stem + ".md"
    lower_fname = fname.lower()

    # Special cases first ---------------------------------------------------
    if fname_stem == "Иерархия нормативных документов":
        meta.update(type="Справочник", number="", name="Иерархия нормативных документов")
        meta["tags"] = ["классификация", "аббревиатуры", "строительство", "нормативные_документы", "иерархия"]
        return _finalize_meta(meta, fname_stem, text)

    if fname_stem == "О техническом регулировании":
        meta.update(type="ФЗ", number="184-ФЗ", name="О техническом регулировании",
                    year="2002-12-27")
        meta["tags"] = ["техническое_регулирование", "стандартизация", "безопасность"]
        return _finalize_meta(meta, fname_stem, text)

    if fname_stem == "Обзор норм о судебно-экспертной деятельности":
        meta.update(type="Обзор", number="", name="Обзор норм о судебно-экспертной деятельности")
        meta["tags"] = ["судебная_экспертиза", "обзор", "процессуальные_нормы"]
        return _finalize_meta(meta, fname_stem, text)

    if fname_stem.startswith("Бутырин"):
        meta.update(type="Монография", number="", name="Теория и практика судебной строительно-технической экспертизы",
                    year="2006-01-01")
        meta["tags"] = ["судебная_экспертиза", "строительно-техническая", "монография"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # Extract dates from filename
    # ------------------------------------------------------------------------
    act_date = ""
    year_str = ""

    # "Редакция от DD.MM.YYYY" → actualization_date
    m_act = re.search(r'Редакция\s+от\s+(\d{2})\.(\d{2})\.(\d{4})', fname)
    if m_act:
        act_date = f"{m_act.group(3)}-{m_act.group(2)}-{m_act.group(1)}"

    # "от DD.MM.YYYY" or "от DD.MM.YY" (first occurrence before Редакция) → year
    m_fed = re.search(r'от\s+(\d{2})\.(\d{2})\.(\d{2,4})', fname)
    if m_fed:
        y = m_fed.group(3)
        if len(y) == 2:
            y = "19" + y if int(y) >= 50 else "20" + y
        year_str = f"{y}-{m_fed.group(2)}-{m_fed.group(1)}"

    # "Дата введения YYYY-MM-DD" in content
    if not year_str:
        m_dv = re.search(r'Дата\s+введения\s+(\d{4}-\d{2}-\d{2})', text[:500])
        if m_dv:
            year_str = m_dv.group(1)

    # "введен в действие Приказом ... от DD.MM.YYYY" in content
    if not year_str and not m_fed:
        m_prikaz = re.search(r'(?:введен|утв).*?Приказ.*?от\s+(\d{2})\.(\d{2})\.(\d{4})', text[:1000], re.DOTALL)
        if m_prikaz:
            year_str = f"{m_prikaz.group(3)}-{m_prikaz.group(2)}-{m_prikaz.group(1)}"

    # fallback to first year in filename
    if not year_str:
        y = _first_year_in(fname)
        if y:
            year_str = f"{y}-01-01"

    # also check "Действует с DD.MM.YYYY" or similar for year
    if not year_str:
        m_ds = re.search(r'Действует\s+с\s+(\d{2})\.(\d{2})\.(\d{4})', text[:500])
        if m_ds:
            year_str = f"{m_ds.group(3)}-{m_ds.group(2)}-{m_ds.group(1)}"

    meta["year"] = year_str
    meta["actualization_date"] = act_date

    # ------------------------------------------------------------------------
    # Document type detection patterns
    # ------------------------------------------------------------------------

    # Уголовно-процессуальный кодекс
    if fname_stem.startswith("Уголовно-процессуальный кодекс"):
        meta["type"] = "Кодекс"
        meta["number"] = ""
        meta["name"] = "Уголовно-процессуальный кодекс Российской Федерации"
        meta["tags"] = ["уголовный_процесс", "судопроизводство", "кодекс"]
        return _finalize_meta(meta, fname_stem, text)

    # Арбитражный процессуальный кодекс
    if fname_stem.startswith("Арбитражный процессуальный кодекс"):
        meta["type"] = "Кодекс"
        meta["number"] = "95-ФЗ"
        meta["name"] = "Арбитражный процессуальный кодекс Российской Федерации"
        meta["tags"] = ["арбитражный_процесс", "судопроизводство", "кодекс"]
        return _finalize_meta(meta, fname_stem, text)

    # Градостроительный кодекс
    if fname_stem.startswith("Градостроительный кодекс"):
        meta["type"] = "Кодекс"
        meta["number"] = "190-ФЗ"
        meta["name"] = "Градостроительный кодекс Российской Федерации"
        meta["tags"] = ["градостроительство", "строительство", "кодекс"]
        return _finalize_meta(meta, fname_stem, text)

    # Гражданский процессуальный кодекс
    if fname_stem.startswith("Гражданский процессуальный кодекс"):
        meta["type"] = "Кодекс"
        meta["number"] = ""
        meta["name"] = "Гражданский процессуальный кодекс Российской Федерации"
        meta["tags"] = ["гражданский_процесс", "судопроизводство", "кодекс"]
        return _finalize_meta(meta, fname_stem, text)

    # Гражданский кодекс (часть вторая)
    if fname_stem.startswith("Гражданский кодекс"):
        meta["type"] = "Кодекс"
        meta["number"] = "14-ФЗ"
        meta["name"] = "Гражданский кодекс Российской Федерации (часть вторая)"
        meta["tags"] = ["гражданское_право", "кодекс"]
        return _finalize_meta(meta, fname_stem, text)

    # Кодекс об административных правонарушениях
    if fname_stem.startswith("Кодекс Российской Федерации об административных правонарушениях"):
        meta["type"] = "Кодекс"
        meta["number"] = "195-ФЗ"
        meta["name"] = "Кодекс Российской Федерации об административных правонарушениях"
        meta["tags"] = ["административные_правонарушения", "кодекс"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # Федеральные законы
    # ------------------------------------------------------------------------
    if fname.startswith("Федеральный закон"):
        meta["type"] = "ФЗ"
        # extract number: N NNN-ФЗ or № NNN-ФЗ
        m_n = re.search(r'[N№]\s*(\d+[А-Я]*)-ФЗ', fname)
        if m_n:
            meta["number"] = m_n.group(1) + "-ФЗ"
        # extract name from content: in quotes after title
        m_name = re.search(r'"([^"]+)"', text[:500])
        if m_name:
            meta["name"] = m_name.group(1)
        else:
            # fallback: filename after the date/number part
            # "Федеральный закон от DD.MM.YYYY N NNN-ФЗ — ..." → "..."
            parts = re.split(r'[—–-]', fname_stem, maxsplit=1)
            if len(parts) > 1:
                meta["name"] = parts[1].strip()
        meta["tags"] = ["федеральный_закон", "нормативный_акт"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # Постановления
    # ------------------------------------------------------------------------
    if fname_stem.startswith("Постановление Пленума Верховного Суда"):
        meta["type"] = "Постановление"
        m_n = re.search(r'N\s*(\d+)', fname)
        if m_n:
            meta["number"] = m_n.group(1)
        meta["name"] = fname_stem.split("—")[0].strip() if "—" in fname_stem else fname_stem
        meta["tags"] = ["постановление", "верховный_суд", "судебная_практика"]
        return _finalize_meta(meta, fname_stem, text)

    if fname_stem.startswith("Постановление Пленума ВАС РФ"):
        meta["type"] = "Постановление"
        m_n = re.search(r'N\s*(\d+)', fname)
        if m_n:
            meta["number"] = m_n.group(1)
        meta["name"] = fname_stem.split("—")[0].strip()
        meta["tags"] = ["постановление", "вас_рф", "судебная_практика"]
        return _finalize_meta(meta, fname_stem, text)

    if fname_stem.startswith("Постановление Правительства РФ"):
        meta["type"] = "Постановление"
        m_n = re.search(r'N\s*(\d+)', fname)
        if m_n:
            meta["number"] = m_n.group(1)
        meta["name"] = fname_stem.split("—")[0].strip()
        meta["tags"] = ["постановление", "правительство_рф"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # Приказы
    # ------------------------------------------------------------------------
    if fname_stem.startswith("Приказ Минтруда") or fname_stem.startswith("Приказ Минстроя"):
        meta["type"] = "Приказ"
        m_n = re.search(r'N\s*(\d+[А-Я]*[пр]*)', fname)
        if m_n:
            meta["number"] = m_n.group(1)
        meta["name"] = fname_stem.split("—")[0].strip() if "—" in fname_stem else fname_stem
        meta["tags"] = ["приказ", "минстрой"]
        if "труда" in lower_fname:
            meta["tags"] = ["приказ", "минтруд", "охрана_труда"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # Письмо
    # ------------------------------------------------------------------------
    if fname_stem.startswith("Письмо"):
        meta["type"] = "Письмо"
        meta["number"] = ""
        meta["name"] = fname_stem
        meta["tags"] = ["письмо", "разъяснение"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # Классификатор
    # ------------------------------------------------------------------------
    if fname_stem.startswith("Классификатор"):
        meta["type"] = "Классификатор"
        meta["number"] = ""
        meta["name"] = fname_stem.split("—")[0].strip()
        meta["tags"] = ["классификатор", "дефекты", "строительство"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # Каталог
    # ------------------------------------------------------------------------
    if fname_stem.startswith("Каталог"):
        meta["type"] = "Каталог"
        meta["number"] = ""
        meta["name"] = fname_stem.split("(утв")[0].strip()
        meta["tags"] = ["каталог", "усиление", "конструкции"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # ГОСТ patterns (most numerous)
    # ------------------------------------------------------------------------
    # Try "ГОСТ Р ИСО NNNN-NNN" → type=ГОСТ Р ИСО
    m_gost_riso = re.match(r'ГОСТ\s+Р\s+ИСО\s+(\d[\d\.]*(?:-\d+)?)', fname_stem)
    if m_gost_riso:
        meta["type"] = "ГОСТ Р ИСО"
        meta["number"] = m_gost_riso.group(1)
        rest = fname_stem[m_gost_riso.end():].strip().lstrip(" -—.–")
        # "Контроль неразрушающий. Метод магнитной памяти металла. Часть 1. Термины и определения"
        meta["name"] = rest
        meta["tags"] = ["стандарт", "неразрушающий_контроль"]
        if "термин" in rest.lower():
            meta["tags"].append("термины")
        return _finalize_meta(meta, fname_stem, text)

    # Try "ГОСТ Р NNNN-NNN" → type=ГОСТ Р
    m_gost_r = re.match(r'ГОСТ\s+Р\s+(\d[\d]*(?:\.[\d]+)*(?:-\d+)?)', fname_stem)
    if m_gost_r:
        meta["type"] = "ГОСТ Р"
        meta["number"] = m_gost_r.group(1)
        rest = fname_stem[m_gost_r.end():].strip().lstrip(" -—.–«»\"")
        meta["name"] = rest
        meta["tags"] = ["стандарт"]
        return _finalize_meta(meta, fname_stem, text)

    # Try "ГОСТ NNNN-NNN" (with space after ГОСТ)
    m_gost = re.match(r'ГОСТ\s+(\d[\d]*(?:\.[\d]+)*(?:-\d+)?)', fname_stem)
    if m_gost:
        meta["type"] = "ГОСТ"
        meta["number"] = m_gost.group(1)
        rest = fname_stem[m_gost.end():].strip().lstrip(" -—.–«»\"")
        meta["name"] = rest
        meta["tags"] = ["стандарт"]
        return _finalize_meta(meta, fname_stem, text)

    # Try "ГОСТ_NNNN-NNN" (with underscore)
    m_gost_u = re.match(r'ГОСТ_(\d[\d]*(?:\.[\d]+)*(?:-\d+)?)', fname_stem)
    if m_gost_u:
        meta["type"] = "ГОСТ"
        meta["number"] = m_gost_u.group(1)
        rest = fname_stem[m_gost_u.end():].strip().lstrip(" -—.–«»\"")
        meta["name"] = rest
        meta["tags"] = ["стандарт"]
        return _finalize_meta(meta, fname_stem, text)

    # "ГОСТ NNNN-NNN" pattern with no space after number
    m_gost_near = re.match(r'ГОСТ\s+(\d[\d]*(?:\.[\d]+)*(?:-\d+)?)(?!\d)', fname_stem)
    if m_gost_near:
        meta["type"] = "ГОСТ"
        meta["number"] = m_gost_near.group(1)
        rest = fname_stem[m_gost_near.end():].strip().lstrip(" -—.–«»\"")
        meta["name"] = rest
        meta["tags"] = ["стандарт"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # СП (Своды Правил) - complex patterns
    # ------------------------------------------------------------------------
    # СП NNN.NNNNNNN.YYYY or СП NNN.NNNNNNNN-YYYY
    m_sp = re.match(r'СП\s+(\d+[\d\.]*(?:-\d{4})?)', fname_stem)
    if m_sp:
        meta["type"] = "СП"
        num = m_sp.group(1)
        # ensure it contains year at end
        meta["number"] = num
        rest = fname_stem[m_sp.end():].strip().lstrip(" -—.–«»\"")
        # strip leading ". Свод правил." or ". Свод правил."
        rest = re.sub(r'^\.?\s*Свод\s+правил[а]?[\.\s]*', '', rest)
        # but also may have "Свод правил." after the number in the name itself
        meta["name"] = rest.split("(утв")[0].split("(ред")[0].split("—")[0].strip()
        # clean trailing parens
        meta["name"] = re.sub(r'\s*\([^)]*$', '', meta["name"])
        meta["tags"] = ["свод_правил"]
        return _finalize_meta(meta, fname_stem, text)

    # "Свод правил. ... СП NNN.NNNNNNN.NNNN" pattern (name first)
    m_sp_namefirst = re.match(r'Свод\s+правил[а]?[\.\s]+(.+?)СП\s+(\d+[\d\.]*(?:-\d{4})?)', fname_stem)
    if m_sp_namefirst:
        meta["type"] = "СП"
        meta["number"] = m_sp_namefirst.group(2)
        meta["name"] = m_sp_namefirst.group(1).strip().rstrip(".— ")
        meta["tags"] = ["свод_правил"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # СНиП
    # ------------------------------------------------------------------------
    if fname_stem.startswith("СНиП"):
        meta["type"] = "СНиП"
        m_snip = re.match(r'СНиП\s+([\d\.\-]+(?:-\d{2,4})?)', fname_stem)
        if m_snip:
            meta["number"] = m_snip.group(1)
        rest = fname_stem[m_snip.end():].strip() if m_snip else fname_stem[4:].strip()
        meta["name"] = rest.split("—")[0].strip()
        meta["tags"] = ["строительные_нормы"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # МДС
    # ------------------------------------------------------------------------
    if fname_stem.startswith("МДС"):
        meta["type"] = "МДС"
        m_mds = re.match(r'МДС\s+([\d\.\-]+(?:-\d{4})?)', fname_stem)
        if m_mds:
            meta["number"] = m_mds.group(1)
        rest = fname_stem[m_mds.end():].strip().lstrip(" -.—") if m_mds else fname_stem[3:].strip()
        meta["name"] = rest.split("—")[0].split("(приняты")[0].split("(утв")[0].strip()
        meta["tags"] = ["методический_документ"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # ВСН
    # ------------------------------------------------------------------------
    if fname_stem.startswith("Ведомственные строительные нормы"):
        meta["type"] = "ВСН"
        m_vsn = re.search(r'ВСН\s+([\d\-]+(?:\([^)]*\))?)', fname_stem)
        if m_vsn:
            meta["number"] = m_vsn.group(1)
        meta["name"] = fname_stem.split("—")[0].strip()
        meta["tags"] = ["ведомственные_нормы"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # РД
    # ------------------------------------------------------------------------
    if fname_stem.startswith("РД"):
        meta["type"] = "РД"
        m_rd = re.match(r'РД\s+([\d\.\-]+)', fname_stem)
        if m_rd:
            meta["number"] = m_rd.group(1)
        rest = fname_stem[m_rd.end():].strip().lstrip(" -.—«»\"") if m_rd else fname_stem[2:].strip()
        meta["name"] = rest.split("—")[0].split("(утв")[0].split('"')[0].strip()
        meta["tags"] = ["руководящий_документ"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # ОДМ
    # ------------------------------------------------------------------------
    if fname_stem.startswith("ОДМ"):
        meta["type"] = "ОДМ"
        m_odm = re.match(r'ОДМ\s+([\d\.\-]+)', fname_stem)
        if m_odm:
            meta["number"] = m_odm.group(1)
        rest = fname_stem[m_odm.end():].strip().lstrip(" -.—«»\"") if m_odm else fname_stem[3:].strip()
        meta["name"] = rest.split("—")[0].split("(издан")[0].split("(утв")[0].strip()
        meta["tags"] = ["методический_документ", "дороги"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # СТО
    # ------------------------------------------------------------------------
    if fname_stem.startswith("СТО"):
        meta["type"] = "СТО"
        m_sto = re.match(r'СТО\s+([\w\.\-]+)', fname_stem)
        if m_sto:
            meta["number"] = m_sto.group(1)
        rest = fname_stem[m_sto.end():].strip().lstrip(" -.—«»\"") if m_sto else fname_stem[3:].strip()
        meta["name"] = rest.split("—")[0].split("(утв")[0].strip()
        meta["tags"] = ["стандарт_организации"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # МРР
    # ------------------------------------------------------------------------
    if fname_stem.startswith("МРР"):
        meta["type"] = "МРР"
        m_mrr = re.match(r'МРР\s+([\d\.\-]+)', fname_stem)
        if m_mrr:
            meta["number"] = m_mrr.group(1)
        rest = fname_stem[m_mrr.end():].strip().lstrip(" -.—") if m_mrr else fname_stem[3:].strip()
        meta["name"] = rest.split("—")[0].strip()
        meta["tags"] = ["методика"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # Пособия, Руководства, Рекомендации, Методические рекомендации
    # ------------------------------------------------------------------------
    if fname_stem.startswith("Пособие"):
        meta["type"] = "Пособие"
        meta["number"] = ""
        meta["name"] = fname_stem.split("—")[0].strip()
        meta["tags"] = ["пособие", "методика"]
        return _finalize_meta(meta, fname_stem, text)

    if fname_stem.startswith("Рекомендации"):
        meta["type"] = "Рекомендации"
        meta["number"] = ""
        meta["name"] = fname_stem.split("—")[0].split("(утв")[0].strip()
        meta["tags"] = ["рекомендации", "методика"]
        return _finalize_meta(meta, fname_stem, text)

    if fname_stem.startswith("Руководство"):
        meta["type"] = "Руководство"
        meta["number"] = ""
        meta["name"] = fname_stem.split("—")[0].strip()
        meta["tags"] = ["руководство", "методика"]
        return _finalize_meta(meta, fname_stem, text)

    if fname_stem.startswith("Методические рекомендации") or fname_stem.startswith("Методика"):
        meta["type"] = "Методика"
        meta["number"] = ""
        meta["name"] = fname_stem.split("—")[0].split("(утв")[0].strip()
        meta["tags"] = ["методика"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # "Об осуществлении..." - Постановление Правительства
    # ------------------------------------------------------------------------
    if fname_stem.startswith("Об осуществлении"):
        meta["type"] = "Постановление"
        meta["number"] = "2120"
        meta["name"] = "Об осуществлении замены и (или) восстановления отдельных элементов строительных конструкций зданий, сооружений"
        meta["tags"] = ["постановление", "правительство_рф", "текущий_ремонт"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # Embedded GOST / СП in filename (e.g. "Бетоны... ГОСТ 22690-2015")
    # ------------------------------------------------------------------------
    m_egost = re.search(r'ГОСТ\s+(\d[\d]*(?:\.[\d]+)*(?:-\d{4})?)', fname_stem)
    if m_egost:
        meta["type"] = "ГОСТ"
        meta["number"] = m_egost.group(1)
        meta["name"] = fname_stem[:m_egost.start()].strip().strip(".— ")
        meta["tags"] = ["стандарт"]
        return _finalize_meta(meta, fname_stem, text)

    # Embedded СП in filename (e.g. "Защита... СП 28.13330.2017" or "Правила... СП 13-102-2003")
    m_esp_dot = re.search(r'СП\s+(\d+[\d\.]*(?:-\d{4})?)', fname_stem)
    if m_esp_dot:
        meta["type"] = "СП"
        meta["number"] = m_esp_dot.group(1)
        meta["name"] = fname_stem[:m_esp_dot.start()].strip().strip(".— ")
        meta["tags"] = ["свод_правил"]
        return _finalize_meta(meta, fname_stem, text)
    m_esp_dash = re.search(r'СП\s+([\d\-]{5,})', fname_stem)
    if m_esp_dash:
        meta["type"] = "СП"
        meta["number"] = m_esp_dash.group(1)
        meta["name"] = fname_stem[:m_esp_dash.start()].strip().strip(".— ")
        meta["tags"] = ["свод_правил"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # Fallback: "Определение ..." files
    # ------------------------------------------------------------------------
    if fname_stem.startswith("Определение"):
        meta["type"] = "Методика"
        meta["number"] = ""
        meta["name"] = fname_stem.split("- Справочники")[0].strip()
        meta["tags"] = ["методика", "экспертиза"]
        return _finalize_meta(meta, fname_stem, text)

    # ------------------------------------------------------------------------
    # Absolute fallback
    # ------------------------------------------------------------------------
    meta["type"] = "Справочник"
    meta["number"] = ""
    meta["name"] = fname_stem
    meta["tags"] = ["справочник"]

    return _finalize_meta(meta, fname_stem, text)


def _finalize_meta(meta, fname_stem, text):
    """Post-process: add OKS/UDK/BBK, tags, cleanup."""
    oks, udk, bbk = _extract_oks_udk_bbk(text)
    if oks:
        meta["oks"] = oks
    if udk:
        meta["udk"] = udk
    if bbk:
        meta["bbk"] = bbk

    # actualization_date defaults to year if not specified (AGENTS.md 14.5(7))
    if not meta.get("actualization_date") and meta.get("year"):
        meta["actualization_date"] = meta["year"]

    # regenerate tags if empty or we only have default
    if not meta.get("tags") or (len(meta["tags"]) <= 1 and meta["tags"][0] in ("стандарт", "свод_правил")):
        meta["tags"] = _generate_tags(fname_stem, text, meta.get("type", ""), meta.get("name", ""))

    meta["tags"] = _dedup_tags(meta["tags"])

    # clean name: remove everything after (утв, (ред, — if present
    # but only if it looks like boilerplate tail
    name = meta.get("name", "")
    name = re.split(r'\s*\(утв', name)[0]
    name = re.split(r'\s*\(ред', name)[0]
    name = name.strip().rstrip(".—, ")
    meta["name"] = name

    return meta


# ---------------------------------------------------------------------------
# YAML writer (no pyyaml, manual)
# ---------------------------------------------------------------------------

def _write_yaml_value(key: str, value) -> str:
    """Return a single YAML line for a key-value pair."""
    if value is None or value == "" or (isinstance(value, list) and not value):
        return ""  # skip empty
    if isinstance(value, list):
        lines = [f"tags:"] if key == "tags" else []
        for v in value:
            if v:
                lines.append(f"  - {v}")
        return "\n".join(lines)
    # string
    val_str = str(value)
    # if contains special chars, wrap in quotes
    if any(c in val_str for c in ": #{}[]&*!|>%@`"):
        val_str = val_str.replace("\\", "\\\\").replace('"', '\\"')
        val_str = f'"{val_str}"'
    return f"{key}: {val_str}"


def build_frontmatter(meta: dict) -> str:
    """Build YAML frontmatter string from meta dict."""
    lines = ["---"]
    ordered_keys = ["type", "number", "name", "title", "description",
                    "year", "actualization_date", "oks", "udk", "bbk",
                    "tags"]
    for key in ordered_keys:
        if key in meta:
            val = meta[key]
            line = _write_yaml_value(key, val)
            if line:
                if isinstance(val, list) and key == "tags":
                    lines.append(line)
                else:
                    lines.append(line)
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def process_file(filepath: pathlib.Path) -> dict:
    """Process a single file. Returns status dict."""
    result = {"file": filepath.name, "status": "ok", "message": ""}

    with open(filepath, "r", encoding="utf-8-sig") as f:
        raw = f.read()

    # try to strip BOM
    if raw.startswith('\ufeff'):
        raw = raw[1:]

    yaml_block, rest, existing_fm = _parse_frontmatter(raw)

    old_title = existing_fm.get("title", "")
    old_description = existing_fm.get("description", "")

    # derive metadata
    fname_stem = filepath.stem
    meta = derive_metadata(fname_stem, raw)

    # preserve existing title/description if they exist and are meaningful
    if old_title:
        meta["title"] = old_title
    else:
        # build title from type + number + name
        parts = []
        if meta.get("type"):
            parts.append(meta["type"])
        if meta.get("number"):
            parts.append(meta["number"])
        if meta.get("name"):
            parts.append(meta["name"])
        meta["title"] = " ".join(parts) if parts else fname_stem

    if old_description:
        meta["description"] = old_description
    else:
        meta["description"] = meta.get("name", fname_stem)

    # raw_source not added — per AGENTS.md 14.5(11): "Для файлов в raw/ не заполняется"

    # build new frontmatter
    new_fm = build_frontmatter(meta)

    # ensure content after frontmatter starts with a blank line for readability
    rest = rest.lstrip("\n")
    new_content = new_fm + "\n" + rest

    # write back
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)

    result["type"] = meta.get("type", "")
    result["title"] = meta.get("title", "")
    return result


def main():
    md_files = sorted(RAW_DIR.glob("*.md"))
    # exclude llm/ content (files in raw/llm/ not in raw/)
    # but we're only globbing raw/*.md so this is fine

    total = len(md_files)
    ok = 0
    errors = []

    print(f"Found {total} .md files in raw/")
    print("-" * 60)

    for fp in md_files:
        try:
            res = process_file(fp)
            ok += 1
            print(f"  OK  {fp.name[:65]:65s} → {res.get('type',''):15s} | {res.get('title','')[:50]}")
        except Exception as e:
            errors.append((fp.name, str(e)))
            print(f"  ERR {fp.name}: {e}")

    print("-" * 60)
    print(f"Processed: {ok}/{total}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for name, msg in errors:
            print(f"  - {name}: {msg}")
    print("Done.")


if __name__ == "__main__":
    main()
