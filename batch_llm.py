import os
llm_dir = os.path.join(os.environ['USERPROFILE'], 'Documents', 'База', 'raw', 'llm')

meta = {}

def add(fname, title, description):
    meta[fname] = (title, description)

add('Build a Second Brain Using Obsidian \u2013 A Practical Guide for Engineers.md',
    'Build a Second Brain Using Obsidian. A Practical Guide for Engineers',
    'Практическое руководство для инженеров по созданию второй памяти в Obsidian')

add('Building my Personal LLM Wiki (Part 1) The Motivation.md',
    'Building my Personal LLM Wiki. Part 1. The Motivation',
    'Мотивация и предпосылки создания персональной LLM Wiki')

add('Building my Personal LLM Wiki (Part 2) The Technical Implementation.md',
    'Building my Personal LLM Wiki. Part 2. The Technical Implementation',
    'Техническая реализация персональной LLM Wiki')

add('Getting Started with Zettelkasten in Obsidian.md',
    'Getting Started with Zettelkasten in Obsidian',
    'Введение в метод Zettelkasten в Obsidian')

add('Introduction to Obsidian Web Clipper.md',
    'Introduction to Obsidian Web Clipper',
    'Введение в расширение Obsidian Web Clipper для сохранения веб-контента')

add('LLM Wiki v2 \u2013 extending Karpathy\'s LLM Wiki pattern with lessons from building agentmemory.md',
    'LLM Wiki v2. Extending Karpathy\'s LLM Wiki pattern with lessons from building agentmemory',
    'Развитие паттерна LLM Wiki с опытом создания agentmemory')

add('Zettelkasten \u2013 Obsidian как инструмент для развития мышления.md',
    'Zettelkasten \u2013 Obsidian как инструмент для развития мышления',
    'Использование Obsidian для развития мышления по методу Zettelkasten')

add('Zettelkasten \u2013 Obsidian как научиться думать и писать.md',
    'Zettelkasten \u2013 Obsidian как научиться думать и писать',
    'Обучение мышлению и письму через Obsidian и метод Zettelkasten')

add('llm-wiki.md',
    'LLM Wiki pattern',
    'Паттерн LLM Wiki для создания персональной базы знаний с помощью LLM-агентов')

ok = 0
for fname in os.listdir(llm_dir):
    if not fname.endswith('.md'): continue
    fp = os.path.join(llm_dir, fname)
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'clippings' not in content:
        print(f'  SKIP (already done): {fname}')
        continue
    if fname not in meta:
        print(f'  SKIP (no meta): {fname}')
        continue
    title, desc = meta[fname]
    end_idx = content.find('---', 3)
    if end_idx == -1:
        print(f'  SKIP (bad fm): {fname}')
        continue
    end_idx += 3
    rest = content[end_idx:]
    new_fm = '---\n'
    new_fm += 'type: статья\n'
    new_fm += f'title: "{title}"\n'
    new_fm += f'description: "{desc}"\n'
    new_fm += 'tags:\n'
    new_fm += '  - llm_wiki\n'
    new_fm += '  - obsidian\n'
    new_fm += '  - заметки\n'
    new_fm += '---\n'
    new_content = new_fm + rest
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_content)
    sz = os.path.getsize(fp)
    print(f'  OK: {fname} ({sz} bytes)')
    ok += 1
print(f'\nDone: {ok} files updated')
