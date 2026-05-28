import os, re, sys

wiki_dir = os.path.join(os.environ['USERPROFILE'], 'Documents', 'База', 'wiki')
visited = set()
ghost_cache = {}
page_order = []

def find_wikilinks(text):
    return re.findall(r'\[\[([^\]]+?)(?:\|[^\]]+)?\]\]', text)

def normalize_link(link):
    """Convert [[link]] to actual filename without .md"""
    link = link.strip()
    # strip anchor
    if '#' in link:
        link = link.split('#')[0]
    # strip leading wiki/ if present
    if link.startswith('wiki/'):
        link = link[5:]
    return link

def filename_for_link(link):
    """Get the actual wiki filename for a wikilink name"""
    # Try exact match: link.md
    fp = os.path.join(wiki_dir, link + '.md')
    if os.path.exists(fp):
        return f'{link}.md'
    # Try case-insensitive search
    for f in os.listdir(wiki_dir):
        if not f.endswith('.md'):
            continue
        name = f[:-3]
        if name.lower() == link.lower():
            return f
    return None

def get_ghost_links(text):
    """Find wikilinks that don't resolve to any wiki file"""
    links = find_wikilinks(text)
    ghosts = []
    for link in links:
        norm = normalize_link(link)
        # skip self-references with anchor
        if norm == '':
            continue
        fname = filename_for_link(norm)
        if fname is None:
            ghosts.append(norm)
    return sorted(set(ghosts))

def get_development_section(filepath):
    """Extract the Развитие section from a wiki file"""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove frontmatter
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            content = content[end+3:]
    # Find ## Развитие or ## Development
    m = re.search(r'^##\s*Развитие\s*$', content, re.MULTILINE)
    if not m:
        return None
    start = m.end()
    # Find next heading of same or higher level
    rest = content[start:]
    next_h = re.search(r'^##\s', rest, re.MULTILINE)
    if next_h:
        section = rest[:next_h.start()]
    else:
        section = rest
    section = section.strip()
    return section if section else None

def process_page(page_name, depth):
    """Process a wiki page and return the tree node data"""
    if depth > 6:
        return None
    key = page_name.lower()
    if key in visited:
        return None
    visited.add(key)
    
    fp = os.path.join(wiki_dir, page_name)
    if not os.path.exists(fp):
        return None
    
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find direct wikilinks (not in frontmatter)
    body = content
    if body.startswith('---'):
        end = body.find('---', 3)
        if end != -1:
            body = body[end+3:]
    
    links = find_wikilinks(body)
    child_names = []
    children = []
    for link in links:
        norm = normalize_link(link)
        if norm == '':
            continue
        fname = filename_for_link(norm)
        if fname and fname != page_name:
            if norm.lower() not in visited:
                child_names.append((fname, norm))
    
    ghost = get_ghost_links(body)
    dev = get_development_section(fp)
    
    result = {
        'page': page_name,
        'name': page_name[:-3],  # without .md
        'depth': depth,
        'ghost': ghost,
        'has_dev': dev is not None,
        'dev_text': dev,
        'children': []
    }
    
    for fname, link_name in child_names:
        child = process_page(fname, depth + 1)
        if child:
            result['children'].append(child)
    
    return result

def render_tree(node, lines, level=1):
    """Render the tree node to markdown"""
    indent = ''
    h_level = min(level + 1, 6)
    heading = '#' * h_level
    
    # Page heading
    name = node['name']
    lines.append(f'{heading} [[{name}]]')
    lines.append('')
    
    # Ghost links
    if node['ghost']:
        lines.append(f'**Призрачные ссылки ({len(node["ghost"])}):**')
        for g in node['ghost']:
            lines.append(f'- `[[{g}]]`')
        lines.append('')
    else:
        lines.append('Призрачных ссылок нет')
        lines.append('')
    
    # Development section
    if node['has_dev']:
        lines.append(f'![[{name}#Развитие]]')
    else:
        lines.append(f'*Раздел «Развитие» отсутствует*')
    lines.append('')
    
    # Separator
    lines.append('---')
    lines.append('')
    
    # Children
    for child in node['children']:
        render_tree(child, lines, level + 1)

# Build tree from index.md
idx = os.path.join(wiki_dir, 'index.md')
tree = process_page('index.md', 0)

if tree is None:
    print("ERROR: cannot read index.md")
    sys.exit(1)

# Render
lines = [
    '---',
    'type: growth',
    'title: Мониторинг развития wiki',
    'description: 'Автоматически сгенерированный сводный файл для отслеживания направлений развития wiki-страниц, призрачных ссылок и разделов «Развитие».',
    'tags:',
    '  - служебная',
    '  - развитие',
    '---',
    '',
    '# Growth Map',
    '',
    'Иерархическая карта развития wiki. Для каждой страницы: призрачные ссылки → раздел «Развитие».',
    '',
    'Легенда:',
    '- `[[ссылка]]` — wikilink на существующую страницу',
    '- `...Призрачные ссылки...` — ссылки на ещё не созданные страницы',
    '- `![[...]]` — встроенный раздел «Развитие» целевой страницы',
    '',
    '---',
    ''
]

render_tree(tree, lines, 0)

output = '\n'.join(lines)

with open(os.path.join(wiki_dir, 'growth.md'), 'w', encoding='utf-8') as f:
    f.write(output)

print(f'Written {len(lines)} lines to wiki/growth.md')

# Stats
total_pages = len(visited)
total_ghosts = sum(len(node['ghost']) for node in [tree] if node)
print(f'Processed {total_pages} pages')
