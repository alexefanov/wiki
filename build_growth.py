# -*- coding: utf-8 -*-
import os, re, sys

wiki_dir = os.path.join(os.environ['USERPROFILE'], 'Documents', '\u0411\u0430\u0437\u0430', 'wiki')

visited = set()

def find_wikilinks(text):
    return re.findall(r'\[\[([^\]]+?)(?:\|[^\]]+)?\]\]', text)

def normalize_link(link):
    link = link.strip()
    if '#' in link:
        link = link.split('#')[0]
    if link.startswith('wiki/'):
        link = link[5:]
    return link

def filename_for_link(link):
    fp = os.path.join(wiki_dir, link + '.md')
    if os.path.exists(fp):
        return link + '.md'
    for f in os.listdir(wiki_dir):
        if not f.endswith('.md'):
            continue
        name = f[:-3]
        if name.lower() == link.lower():
            return f
    return None

def get_ghost_links(text):
    links = find_wikilinks(text)
    ghosts = []
    for link in links:
        norm = normalize_link(link)
        if norm == '':
            continue
        fname = filename_for_link(norm)
        if fname is None:
            ghosts.append(norm)
    return sorted(set(ghosts))

def get_development_section(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            content = content[end+3:]
    m = re.search(r'^##\s*[\u0420\u0430\u0437\u0432\u0438\u0442\u0438\u0435]\s*$', content, re.MULTILINE)
    if not m:
        return None
    start = m.end()
    rest = content[start:]
    next_h = re.search(r'^##\s', rest, re.MULTILINE)
    if next_h:
        section = rest[:next_h.start()]
    else:
        section = rest
    section = section.strip()
    return section if section else None

def process_page(page_name, depth):
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
    body = content
    if body.startswith('---'):
        end = body.find('---', 3)
        if end != -1:
            body = body[end+3:]
    links = find_wikilinks(body)
    child_names = []
    for link in links:
        norm = normalize_link(link)
        if norm == '':
            continue
        fname = filename_for_link(norm)
        if fname and fname != page_name:
            if fname.lower() not in visited:
                child_names.append(fname)
    ghost = get_ghost_links(body)
    dev = get_development_section(fp)
    name_for_wiki = page_name[:-3]
    result = {
        'page': page_name,
        'name': name_for_wiki,
        'depth': depth,
        'ghost': ghost,
        'has_dev': dev is not None,
        'children': []
    }
    for fname in child_names:
        child = process_page(fname, depth + 1)
        if child:
            result['children'].append(child)
    return result

def render_tree(node, lines, level=1):
    h_level = min(level + 1, 6)
    heading = '#' * h_level
    name = node['name']
    lines.append(heading + ' [[' + name + ']]')
    lines.append('')
    if node['ghost']:
        lines.append('**Ghost links (' + str(len(node['ghost'])) + '):**')
        for g in node['ghost']:
            lines.append('- `[[' + g + ']]`')
        lines.append('')
    else:
        lines.append('No ghost links')
        lines.append('')
    if node['has_dev']:
        lines.append('![[' + name + '#\u0420\u0430\u0437\u0432\u0438\u0442\u0438\u0435]]')
    else:
        lines.append('*No Development section*')
    lines.append('')
    lines.append('---')
    lines.append('')
    for child in node['children']:
        render_tree(child, lines, level + 1)

idx = os.path.join(wiki_dir, 'index.md')
tree = process_page('index.md', 0)
if tree is None:
    print('ERROR: cannot read index.md')
    sys.exit(1)

lines = ['---',
'type: growth',
'title: '\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433 \u0440\u0430\u0437\u0432\u0438\u0442\u0438\u044f wiki',
'description: "'\u0410\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0441\u0433\u0435\u043d\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0439 \u0441\u0432\u043e\u0434\u043d\u044b\u0439 \u0444\u0430\u0439\u043b \u0434\u043b\u044f \u043e\u0442\u0441\u043b\u0435\u0436\u0438\u0432\u0430\u043d\u0438\u044f \u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0439 \u0440\u0430\u0437\u0432\u0438\u0442\u0438\u044f wiki-\u0441\u0442\u0440\u0430\u043d\u0438\u0446, \u043f\u0440\u0438\u0437\u0440\u0430\u0447\u043d\u044b\u0445 \u0441\u0441\u044b\u043b\u043e\u043a \u0438 \u0440\u0430\u0437\u0434\u0435\u043b\u043e\u0432 \u0420\u0430\u0437\u0432\u0438\u0442\u0438\u0435',
'tags:',
'  - \u0441\u043b\u0443\u0436\u0435\u0431\u043d\u0430\u044f',
'  - \u0440\u0430\u0437\u0432\u0438\u0442\u0438\u0435',
'---',
'',
'# Growth Map',
'',
'\u0418\u0435\u0440\u0430\u0440\u0445\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u043a\u0430\u0440\u0442\u0430 \u0440\u0430\u0437\u0432\u0438\u0442\u0438\u044f wiki. \u0414\u043b\u044f \u043a\u0430\u0436\u0434\u043e\u0439 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b: \u043f\u0440\u0438\u0437\u0440\u0430\u0447\u043d\u044b\u0435 \u0441\u0441\u044b\u043b\u043a\u0438 \u2192 \u0440\u0430\u0437\u0434\u0435\u043b \u0420\u0430\u0437\u0432\u0438\u0442\u0438\u0435',
'',
'\u041b\u0435\u0433\u0435\u043d\u0434\u0430:',
'- `[[\u0441\u0441\u044b\u043b\u043a\u0430]]` \u2014 wikilink \u043d\u0430 \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u044e\u0449\u0443\u044e \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0443',
'- `...Ghost links...` \u2014 \u0441\u0441\u044b\u043b\u043a\u0438 \u043d\u0430 \u0435\u0449\u0451 \u043d\u0435 \u0441\u043e\u0437\u0434\u0430\u043d\u043d\u044b\u0435 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b',
'- `![[...]]` \u2014 \u0432\u0441\u0442\u0440\u043e\u0435\u043d\u043d\u044b\u0439 \u0440\u0430\u0437\u0434\u0435\u043b \u0420\u0430\u0437\u0432\u0438\u0442\u0438\u0435 \u0446\u0435\u043b\u0435\u0432\u043e\u0439 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b',
'',
'---',
'']

render_tree(tree, lines, 0)

output = '\n'.join(lines)
outpath = os.path.join(wiki_dir, 'growth.md')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(output)

print('Written ' + str(len(lines)) + ' lines to wiki/growth.md')
print('Pages processed: ' + str(len(visited)))
