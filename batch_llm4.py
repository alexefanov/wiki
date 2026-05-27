import os
d = os.path.join(os.environ['USERPROFILE'], 'Documents', 'База', 'raw', 'llm')
c = 0
for f in os.listdir(d):
    if not f.endswith('.md'):
        continue
    fp = os.path.join(d, f)
    with open(fp, 'r', encoding='utf-8') as h:
        x = h.read()
    if 'clippings' not in x:
        continue
    e = x.find('---', 3)
    if e == -1:
        continue
    r = x[e+3:]
    title = f.replace('.md', '')
    n = '---\ntype: статья\ntitle: "' + title + '"\ndescription: "Статья"\ntags:\n  - llm_wiki\n  - obsidian\n  - заметки\n---\n'
    with open(fp, 'w', encoding='utf-8') as h:
        h.write(n + r)
    c += 1
    print(f'OK: {f}')
print(f'Done: {c}')
