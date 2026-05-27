import os, re, json

base = r'C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База'
raw_dir = os.path.join(base, 'raw')

def update_frontmatter(filepath, meta):
    """Replace frontmatter in a file safely. Returns True on success."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.startswith('---'):
        print(f'  SKIP: no frontmatter in {os.path.basename(filepath)}')
        return False
    
    # Find closing ---
    end_idx = content.find('---', 3)
    if end_idx == -1:
        print(f'  SKIP: no closing --- in {os.path.basename(filepath)}')
        return False
    end_idx += 3
    
    rest = content[end_idx:]
    
    # Build new frontmatter
    lines = ['---']
    for key, value in meta.items():
        if key == 'tags':
            lines.append('tags:')
            for tag in value:
                lines.append(f'   - {tag}')
        else:
            lines.append(f'{key}: "{value}"')
    lines.append('---')
    new_fm = '\n'.join(lines)
    
    new_content = new_fm + rest
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # Verify
    with open(filepath, 'r', encoding='utf-8') as f:
        v = f.read()
    if len(v) < 100:
        print(f'  ERROR: file too small ({len(v)} bytes) after write!')
        return False
    print(f'  OK: {len(v)} bytes, frontmatter replaced')
    return True

# Each entry: (filename_glob, meta_dict)
# Filenames are used as exact matches (full filenames)
batch = [
    # ГОСТ files
    ('ГОСТ 10060-2012 Бетоны. Методы определения морозостойкости.md', {
        'type': 'ГОСТ', 'number': '10060-2012',
        'name': 'Бетоны. Методы определения морозостойкости',
        'description': 'Устанавливает методы определения морозостойкости бетонов',
        'year': '2012-01-01', 'actualization_date': '2012-01-01',
        'tags': ['бетоны', 'морозостойкость', 'испытания']
    }),
    ('ГОСТ 10180-2012 Бетоны. Методы определения прочности по контрольным образцам.md', {
        'type': 'ГОСТ', 'number': '10180-2012',
        'name': 'Бетоны. Методы определения прочности по контрольным образцам',
        'description': 'Устанавливает методы определения прочности бетона по контрольным образцам',
        'year': '2013-07-01', 'actualization_date': '2013-07-01',
        'tags': ['бетоны', 'прочность', 'испытания', 'образцы']
    }),
    ('ГОСТ 12004-81 Сталь арматурная. Методы испытания на растяжение.md', {
        'type': 'ГОСТ', 'number': '12004-81',
        'name': 'Сталь арматурная. Методы испытания на растяжение',
        'description': 'Устанавливает методы испытания на растяжение арматурной стали',
        'year': '1983-01-01', 'actualization_date': '1983-01-01',
        'tags': ['арматура', 'испытания', 'сталь', 'растяжение']
    }),
    ('ГОСТ 13078-2021 Стекло натриевое жидкое. Технические условия.md', {
        'type': 'ГОСТ', 'number': '13078-2021',
        'name': 'Стекло натриевое жидкое. Технические условия',
        'description': 'Устанавливает технические условия на натриевое жидкое стекло',
        'year': '2021-01-01', 'actualization_date': '2021-01-01',
        'tags': ['стекло', 'технические_условия', 'материалы']
    }),
    ('ГОСТ 14098-2014 Соединения сварные арматуры и закладных изделий железобетонных конструкций. Типы, конструкции и размеры.md', {
        'type': 'ГОСТ', 'number': '14098-2014',
        'name': 'Соединения сварные арматуры и закладных изделий железобетонных конструкций. Типы, конструкции и размеры',
        'description': 'Устанавливает типы, конструкции и размеры сварных соединений арматуры и закладных изделий',
        'year': '2015-01-01', 'actualization_date': '2015-01-01',
        'tags': ['сварка', 'арматура', 'железобетон', 'соединения']
    }),
    ('ГОСТ 1497-2023 Металлы. Методы испытаний на растяжение.md', {
        'type': 'ГОСТ', 'number': '1497-2023',
        'name': 'Металлы. Методы испытаний на растяжение',
        'description': 'Устанавливает методы испытаний на растяжение металлов',
        'year': '2023-01-01', 'actualization_date': '2023-01-01',
        'tags': ['металлы', 'испытания', 'растяжение', 'механические_свойства']
    }),
]

success = 0
for fname, meta in batch:
    filepath = os.path.join(raw_dir, fname)
    if not os.path.exists(filepath):
        print(f'NOT FOUND: {fname[:60]}')
        continue
    print(f'\n{fname[:70]}')
    if update_frontmatter(filepath, meta):
        success += 1

print(f'\nDone: {success}/{len(batch)} files updated')
