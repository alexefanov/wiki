import os, re

wd = os.path.join(os.environ['USERPROFILE'], 'Documents', 'База', 'wiki')

def find_links(text):
    return re.findall(r'\[\[([^\]]+?)(?:\|[^\]]+)?\]\]', text)

def norm_link(link):
    link = link.strip()
    if '#' in link:
        link = link.split('#')[0]
    if link.startswith('wiki/'):
        link = link[5:]
    return link

# Build page index
all_pages = {}
for f in os.listdir(wd):
    if not f.endswith('.md'):
        continue
    all_pages[f[:-3].lower()] = f

print(f'Total wiki pages: {len(all_pages)}')
print()

# 1. Broken wikilinks
broken = []
for f in sorted(os.listdir(wd)):
    if not f.endswith('.md'):
        continue
    fp = os.path.join(wd, f)
    with open(fp, 'r', encoding='utf-8') as h:
        c = h.read()
    body = c
    if body.startswith('---'):
        e = body.find('---', 3)
        if e != -1:
            body = body[e+3:]
    for link in find_links(body):
        n = norm_link(link)
        if n and n.lower() not in all_pages:
            broken.append((f, n))

if broken:
    print(f'=== BROKEN WIKILINKS ({len(broken)}) ===')
    for f, n in sorted(broken):
        print(f'  {f} -> [[{n}]]')
else:
    print('=== BROKEN WIKILINKS: NONE ===')
print()

# 2. Orphan pages (no incoming links)
incoming = {}
for f in os.listdir(wd):
    if not f.endswith('.md'):
        continue
    fp = os.path.join(wd, f)
    with open(fp, 'r', encoding='utf-8') as h:
        c = h.read()
    body = c
    if body.startswith('---'):
        e = body.find('---', 3)
        if e != -1:
            body = body[e+3:]
    for link in find_links(body):
        n = norm_link(link)
        if n:
            n = n.lower()
            incoming.setdefault(n, set()).add(f)

orphans = []
for f in sorted(os.listdir(wd)):
    if not f.endswith('.md'):
        continue
    n = f[:-3].lower()
    if n in ('index', 'growth'):
        continue
    if n not in incoming or not incoming[n]:
        orphans.append(f)

if orphans:
    print(f'=== ORPHAN PAGES ({len(orphans)}) ===')
    for f in orphans:
        print(f'  {f}')
else:
    print('=== ORPHAN PAGES: NONE ===')
print()

# 3. Pages without ## Развитие section
no_dev = []
for f in sorted(os.listdir(wd)):
    if not f.endswith('.md'):
        continue
    if f in ('index.md', 'growth.md'):
        continue
    fp = os.path.join(wd, f)
    with open(fp, 'r', encoding='utf-8') as h:
        c = h.read()
    if c.startswith('---'):
        e = c.find('---', 3)
        if e != -1:
            c = c[e+3:]
    if not re.search(r'^##\s*Развитие', c, re.MULTILINE):
        no_dev.append(f)

if no_dev:
    print(f'=== PAGES WITHOUT Развитие SECTION ({len(no_dev)}) ===')
    for f in no_dev:
        print(f'  {f}')
else:
    print('=== PAGES WITHOUT Развитие SECTION: NONE ===')
print()

# 4. Duplicate H1 titles
h1_titles = {}
for f in os.listdir(wd):
    if not f.endswith('.md'):
        continue
    fp = os.path.join(wd, f)
    with open(fp, 'r', encoding='utf-8') as h:
        c = h.read()
    if c.startswith('---'):
        e = c.find('---', 3)
        if e != -1:
            c = c[e+3:]
    m = re.search(r'^#\s+(.+)$', c, re.MULTILINE)
    if m:
        t = m.group(1).strip().lower()
        if t in h1_titles:
            print(f'  DUPLICATE H1: \"{m.group(1).strip()}\" in {f} and {h1_titles[t]}')
        else:
            h1_titles[t] = f

print()

# 5. Check description property vs H1 (stale description)
print('=== DESCRIPTION VS H1 CHECK ===')
for f in sorted(os.listdir(wd)):
    if not f.endswith('.md'):
        continue
    fp = os.path.join(wd, f)
    with open(fp, 'r', encoding='utf-8') as h:
        c = h.read()
    desc_m = re.search(r'^description:\s*"(.+)"', c, re.MULTILINE)
    h1_m = re.search(r'^#\s+(.+)$', c, re.MULTILINE)
    if desc_m and h1_m:
        desc = desc_m.group(1).strip()
        h1 = h1_m.group(1).strip()
        # Check if description mentions title or is very different
        if h1.lower() not in desc.lower() and desc.lower() not in h1.lower():
            print(f'  {f}: H1=\"{h1}\" DESCR=\"{desc[:80]}...\"')

print()
print('Lint complete.')
