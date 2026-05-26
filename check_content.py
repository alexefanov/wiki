import os, re

raw_dir = 'raw'
problems = []
for f in sorted(os.listdir(raw_dir)):
    if not (f.endswith('.md') and os.path.isfile(os.path.join(raw_dir, f))):
        continue
    path = os.path.join(raw_dir, f)
    with open(path, 'r', encoding='utf-8') as fh:
        c = fh.read()
    if not c.startswith('---'):
        problems.append(f'NO FM: {f}')
        continue
    count = c.count('---')
    if count < 2:
        problems.append(f'BROKEN FM (only {count} ---): {f}')
        continue
    try:
        s = c.index('---', 3)
        e = c.index('---', s + 3)
        rest = c[e+3:].strip()
    except ValueError:
        problems.append(f'BROKEN FM (value error): {f}')
        continue
    if len(rest) < 200:
        problems.append(f'SHORT CONTENT ({len(rest)} chars): {f}')

if problems:
    print(f'Problems: {len(problems)}')
    for p in problems:
        print(p)
else:
    print('All files OK')
