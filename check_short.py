import os, re

d = 'raw'
problems = []
for f in sorted(os.listdir(d)):
    if not (f.endswith('.md') and os.path.isfile(os.path.join(d, f))):
        continue
    path = os.path.join(d, f)
    c = open(path, 'r', encoding='utf-8').read()
    if not c.startswith('---'):
        continue
    count = c.count('---')
    if count < 2:
        problems.append(f'BROKEN: {f}')
        continue
    try:
        s = c.index('---', 3)
        e = c.index('---', s + 3)
        rest = c[e+3:].strip()
        if len(rest) < 200:
            problems.append(f'SHORT ({len(rest)}): {f}')
    except ValueError:
        problems.append(f'BROKEN2: {f}')

if problems:
    print(f'Problems found: {len(problems)}')
    for p in problems:
        print(p)
else:
    print('All OK')
