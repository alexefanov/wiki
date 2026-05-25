import re
import os
import yaml

FILES = [
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ_27751-2014.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р ИСО 6707-1-2020 Здания и сооружения. Общие термины.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 8.736-2011 Государственная система обеспечения единства измерений. Измерения прямые многократные. Методы обработки результатов измерений. Основные положения.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 7.0.5-2008.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 59529-2021. Национальный стандарт Российской Федерации. Судебная строительно-техническая экспертиза. Термины и определения (утв. и введен в действие Приказом Росстандарта от 25.05.2021 N 449-ст).md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 58945-2020. Национальный стандарт Российской Федерации. Система обеспечения точности геометрических параметров в строительстве. Правила выполнения измерений параметров зданий и сооружений (утв. и введен в действие Приказом Росстандарта от.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 58945-2020 Система обеспечения точности геометрических параметров в строительстве. Правила выполнения измерений параметров зданий и сооружений.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 58938-2020 Система обеспечения точности геометрических параметров в строительстве. Основные положения.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 58527-2019 Материалы стеновые. Методы определения пределов прочности при сжатии и изгибе.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 57997-2017 Арматурные и закладные изделия сварные, соединения сварные арматуры и закладных изделий железобетонных конструкций. Общие технические условия.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 54081-2010 Воздействие природных внешних условий на технические изделия. Общая характеристика. Пожар.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 53965-2010 Контроль неразрушающий. Определение механических напряжений. Общие требования к классификации методов.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 52728-2007 Метод натурной тензотермометрии. Общие требования.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 52544-2006 Прокат арматурный свариваемый периодического профиля классов А500С и В500С для армирования железобетонных конструкций. Технические условия.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р 21.101-2026 Система проектной документации для строительства. Основные требования к проектной и рабочей документации.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р ИСО 24497-1-2009 Контроль неразрушающий. Метод магнитной памяти металла. Часть 1. Термины и определения.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р ИСО 24497-2-2009 Контроль неразрушающий. Метод магнитной памяти металла. Часть 2. Общие требования.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ Р ИСО 24497-3-2009 Контроль неразрушающий. Метод магнитной памяти металла. Часть 3. Контроль сварных соединений.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Здания и сооружения. Правила обследования и мониторинга технического состояния. ГОСТ 31937-2024 — Редакция от 10.04.2024.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Здания и сооружения. Метод тепловизионного контроля качества теплоизоляции ограждающих конструкций. ГОСТ 26629-85 — Редакция от 04.10.1985.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Грунты. Методы измерения деформаций оснований зданий и сооружений. ГОСТ 24846-2019 — Редакция от 28.07.2020.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Бетоны. Определение прочности механическими методами неразрушающего контроля. ГОСТ 22690-2015 — Редакция от 25.09.2015.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\Управление качеством продукции. Основные понятия. Термины и определения. ГОСТ 15467-79 (ст СЭВ 3519-81) — Редакция от 01.01.1985.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 8.050-73 Государственная система обеспечения единства измерений. Нормальные условия выполнения линейных и угловых измерений.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 8.009-84 Государственная система обеспечения единства измерений. Нормируемые метрологические характеристики средств измерений.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 8.051-81 Государственная система обеспечения единства измерений. Погрешности, допускаемые при измерении линейных размеров до 500 мм.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 9.402-2004 Единая система защиты от коррозии и старения. Покрытия лакокрасочные. Подготовка металлических поверхностей к окрашиванию.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 10060-2012 Бетоны. Методы определения морозостойкости.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 10180-2012 Бетоны. Методы определения прочности по контрольным образцам.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 10181-2014. Межгосударственный стандарт. Смеси бетонные. Методы испытаний (введен в действие Приказом Росстандарта от 11.12.2014 N 1972-ст).md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 12004-81 Сталь арматурная. Методы испытания на растяжение.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 13078-2021 Стекло натриевое жидкое. Технические условия.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 14098-2014 Соединения сварные арматуры и закладных изделий железобетонных конструкций. Типы, конструкции и размеры.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 1497-2023 Металлы. Методы испытаний на растяжение.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 15613.2-77 Древесина клееная массивная. Метод определения предела прочности клеевого соединения при раскалывании.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 15613.5-79 Древесина клееная массивная. Метод определения предела прочности зубчатых клеевых соединений при растяжении.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 16483.0-89 Древесина. Общие требования к физико-механическим испытаниям.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 16483.10-73 Древесина. Методы определения предела прочности при сжатии вдоль волокон.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 16483.3-84 Древесина. Метод определения предела прочности при статическом изгибе.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 16483.5-73 Древесина. Методы определения предела прочности при скалывании вдоль волокон.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 17624-2021БЕТОНЫ УЛЬТРАЗВУКОВОЙ МЕТОД ОПРЕДЕЛЕНИЯ ПРОЧНОСТИ Росстандарта от 16.12.2021 Редакция действует с 1 сентября 2022.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 18105-2010 Бетоны. Правила контроля и оценки прочности.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 21616-91 Тензорезисторы. Общие технические условия.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 23858-2019 Соединения сварные стыковые арматуры железобетонных конструкций. Ультразвуковые методы контроля качества. Правила приемки.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 25314-82 Контроль неразрушающий тепловой. Термины и определения.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 25891-83 «Здания и сооружения. Методы определения сопротивления воздухопроницанию ограждающих конструкций».md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 26254-84 «Здания и сооружения. Методы определения сопротивления теплопередаче ограждающих конструкций».md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 26633-2012 Бетоны тяжелые и мелкозернистые. Технические условия.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 28570-2019. Межгосударственный стандарт. Бетоны. Методы определения прочности по образцам, отобранным из конструкций (введен в действие Приказом Росстандарта от 26.04.2019 N 172-ст).md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 30247.0-94 Конструкции строительные. Методы испытаний на огнестойкость. Общие требования.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 30247.1-94 Конструкции строительные. Методы испытаний на огнестойкость. Несущие и ограждающие конструкции.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 30415-96 Сталь. Неразрушающий контроль механических свойств и микроструктуры металлопродукции магнитным методом.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 31108-2020 Цементы общестроительные. Технические условия.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 31384-2017 Защита бетонных и железобетонных конструкций от коррозии. Общие технические требования.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 33120-2014 Конструкции деревянные клееные. Методы определения прочности клеевых соединений.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 34028-2016 Прокат арматурный для железобетонных конструкций. Технические условия.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 5781-82 Сталь горячекатаная для армирования железобетонных конструкций. Технические условия.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 5802-2024. Межгосударственный стандарт. Растворы строительные. Методы испытаний(введен в действие Приказом Росстандарта от 28.12.2024 N 2058-ст).md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 6727-80 Проволока из низкоуглеродистой стали холоднотянутая для армирования железобетонных конструкций. Технические условия.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 7564-97 Прокат. Общие правила отбора проб, заготовок и образцов для механических и технологических испытаний.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 8736-2014 Песок для строительных работ. Технические условия.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 9696-82 Индикаторы многооборотные с ценой деления 0,001 и 0,002 мм. Технические условия.md",
    r"C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw\ГОСТ 10180-2012 Бетоны. Методы определения прочности по контрольным образцам.md",
]

ALLOWED_KEYS = {"source", "created", "title", "description", "tags"}

SEO_PATTERNS = [
    r"— с последними изменениями скачать на сайте Контур\.Норматив",
    r"Скачать бесплатно pdf, word\.",
    r"Скачать бесплатно pdf, word",
    r" — Редакция от \d{2}\.\d{2}\.\d{4}",
    r"Статус: Действует\.\s*",
    r"Статус: Действует",
    r"\.\s*$",  # trailing period after cleanup
]

def strip_markdown(text):
    """Remove **bold**, `code`, [[wikilinks]], [links](url), _italic_ from text."""
    if not isinstance(text, str):
        return text
    # Remove [[wikilinks]] -> text
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    # Remove [links](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove **bold** or __bold__
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    # Remove `code`
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove _italic_ or *italic* (single)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'\1', text)
    return text

def fix_escaped_quotes(text):
    """Fix \" to " and \' to '"""
    if not isinstance(text, str):
        return text
    text = text.replace('\\"', '"')
    text = text.replace("\\'", "'")
    return text

def fix_curly_quotes(text):
    """Replace smart/curly quotes with regular ASCII quotes."""
    if not isinstance(text, str):
        return text
    replacements = {
        '\u201c': '"',
        '\u201d': '"',
        '\u2018': "'",
        '\u2019': "'",
        '\u00ab': '"',
        '\u00bb': '"',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def clean_desc(text):
    """Remove SEO junk from descriptions."""
    if not isinstance(text, str):
        return text
    for pat in SEO_PATTERNS:
        text = re.sub(pat, '', text)
    # Strip leading/trailing junk
    text = text.strip()
    text = re.sub(r'^[\s,;\-—.]+', '', text)
    text = re.sub(r'[\s,;\-—.]+$', '', text)
    return text.strip()

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file has frontmatter
    if not content.startswith('---'):
        print(f"  SKIP (no frontmatter): {filepath}")
        return

    # Find closing ---
    end_idx = content.find('---', 3)
    if end_idx == -1:
        print(f"  SKIP (malformed frontmatter): {filepath}")
        return

    fm_text = content[3:end_idx].strip()
    body = content[end_idx+3:]

    # Parse YAML
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        print(f"  YAML ERROR: {filepath}: {e}")
        return

    if not isinstance(fm, dict):
        print(f"  SKIP (not a dict): {filepath}")
        return

    # Keep only allowed keys, strip markdown from string values
    new_fm = {}
    for key in ALLOWED_KEYS:
        if key not in fm:
            continue
        val = fm[key]

        if key == "tags":
            if not val or not isinstance(val, list) or len(val) == 0:
                continue
            # Remove "clippings" (case-insensitive)
            cleaned = [t for t in val if isinstance(t, str) and t.strip().lower() != 'clippings']
            if not cleaned:
                continue
            new_fm[key] = cleaned
            continue

        if isinstance(val, str):
            val = fix_escaped_quotes(val)
            val = fix_curly_quotes(val)
            val = strip_markdown(val)

            if key == "description":
                val = clean_desc(val)
                # Also remove trailing periods
                val = re.sub(r'\.+$', '', val.strip())
                if not val:
                    continue

            if key == "title":
                val = val.strip().strip('"').strip("'").strip()
                if not val:
                    continue

            new_fm[key] = val
        elif val is not None:
            new_fm[key] = val

    # If frontmatter empty after cleanup, remove it entirely
    if not new_fm:
        # No frontmatter, just body
        result = body.lstrip('\n')
    else:
        # Write YAML with explicit UTF-8, no tags, default_flow_style for lists
        fm_lines = ['---']
        for k, v in new_fm.items():
            if k == "tags":
                # Write tags as list
                fm_lines.append('tags:')
                for tag in v:
                    fm_lines.append(f'  - {tag}')
            elif isinstance(v, str):
                # Check if string needs quoting (contains special chars)
                if any(c in v for c in [':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`', '"', "'", '\\']):
                    # Double-quote and escape inner double quotes and backslashes
                    escaped = v.replace('\\', '\\\\').replace('"', '\\"')
                    fm_lines.append(f'{k}: "{escaped}"')
                else:
                    fm_lines.append(f'{k}: {v}')
            else:
                fm_lines.append(f'{k}: {v}')
        fm_lines.append('---')
        result = '\n'.join(fm_lines) + '\n' + body.lstrip('\n')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"  OK: {os.path.basename(filepath)}")
    # Print what was kept
    kept = ', '.join(new_fm.keys()) if new_fm else '(empty)'
    print(f"      fields: {kept}")

def main():
    success = 0
    failed = 0
    for fp in FILES:
        if not os.path.exists(fp):
            print(f"  NOT FOUND: {fp}")
            failed += 1
            continue
        try:
            process_file(fp)
            success += 1
        except Exception as e:
            print(f"  ERROR: {fp}: {e}")
            failed += 1
    print(f"\nDone. {success} OK, {failed} failed.")

if __name__ == '__main__':
    main()
