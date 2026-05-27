import os, re

base = r'C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw'

# Batch 1: ГОСТ files and simple files where info is in the filename
# Format: (filename_pattern, frontmatter_dict or callable)
# We'll just process files by reading first 500 bytes to find key info

def get_type(filename):
    if filename.startswith('ГОСТ Р ИСО'): return 'ГОСТ Р ИСО'
    if filename.startswith('ГОСТ Р'): return 'ГОСТ Р'
    if filename.startswith('ГОСТ'): return 'ГОСТ'
    if filename.startswith('СП'): return 'СП'
    if filename.startswith('ФЗ') or filename.startswith('Федеральный закон'): return 'ФЗ'
    if filename.startswith('Постановление'): return 'Постановление'
    if filename.startswith('Приказ'): return 'Приказ'
    if filename.startswith('МДС'): return 'МДС'
    if filename.startswith('МРР'): return 'МРР'
    if filename.startswith('ОДМ'): return 'ОДМ'
    if filename.startswith('РД'): return 'РД'
    if filename.startswith('Классификатор'): return 'Классификатор'
    if filename.startswith('Каталог'): return 'Каталог'
    if filename.startswith('Пособие'): return 'Пособие'
    return None

def extract_number(name):
    # Extract number from various formats
    m = re.match(r'ГОСТ(?: Р)?(?: ИСО)?\s+([\d.]+-\d+)', name)
    if m: return m.group(1)
    m = re.match(r'СП\s+([\d.]+-\d+)', name)
    if m: return m.group(1)
    m = re.match(r'МДС\s+([\d-]+.\d+)', name)
    if m: return m.group(1)
    m = re.match(r'МРР\s+([\d.]+-\d+)', name)
    if m: return m.group(1)
    m = re.match(r'ОДМ\s+([\d.]+-\d+)', name)
    if m: return m.group(1)
    m = re.match(r'РД\s+([\d-]+.\d+-\d+)', name)
    if m: return m.group(1)
    return ''

def make_name(filename):
    # Remove type prefix and version info for clean name
    name = filename.replace('.md', '')
    # Remove Редакция and year at end
    name = re.sub(r'\s*[—–-]\s*Редакция\s+от\s+[\d.]+', '', name)
    name = re.sub(r'\s*\(ред\.\s+от\s+[\d.]+\)', '', name)
    name = re.sub(r'\s*\(утв[^)]*\)', '', name)
    name = re.sub(r'\s*\(принят[^)]*\)', '', name)
    # For GOST standards, extract the name after the number
    m = re.match(r'ГОСТ(?:\s+Р)?(?:\s+ИСО)?\s+[\d.]+-\d+\s+(.*)', name)
    if m: return m.group(1).strip()
    m = re.match(r'СП\s+[\d.]+-\d+\.?\s*(.*)', name)
    if m: return m.group(1).strip().strip('.')
    return name

def make_title(filename):
    name = filename.replace('.md', '').strip()
    return name

# Files to process
files_to_process = [
    # will be filled
]

i = 0
for f in sorted(os.listdir(base)):
    if not f.endswith('.md'): continue
    filepath = os.path.join(base, f)
    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read(500)
    if 'clippings' not in content: continue
    if i >= 15: break  # process 15 at a time
    i += 1
    print(f'Processing: {f[:70]}')
    files_to_process.append(f)

print(f'\nBatch of {len(files_to_process)} files ready for review')
