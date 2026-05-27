import os

base = r'C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База'
raw_dir = os.path.join(base, 'raw')

def update_frontmatter(filepath, meta):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if not content.startswith('---'):
        print(f'  SKIP: no frontmatter')
        return False
    end_idx = content.find('---', 3)
    if end_idx == -1:
        print(f'  SKIP: no closing ---')
        return False
    end_idx += 3
    rest = content[end_idx:]
    lines = ['---']
    for key, value in meta.items():
        if key == 'tags':
            lines.append('tags:')
            for tag in value:
                lines.append(f'   - {tag}')
        else:
            lines.append(f'{key}: "{value}"')
    lines.append('---')
    new_content = '\n'.join(lines) + rest
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    with open(filepath, 'r', encoding='utf-8') as f:
        v = f.read()
    if len(v) < 100:
        print(f'  ERROR: file too small ({len(v)} bytes)!')
        return False
    print(f'  OK: {len(v)} bytes')
    return True

# All remaining files with clippings, discovered by scanning raw dir
import subprocess
result = subprocess.run(['python', '-c', '''
import os
base = r"C:\\\\Users\\\\yefan.LAPTOP-T0BIR3IU\\\\Documents\\\\База\\\\raw"
for f in sorted(os.listdir(base)):
    if not f.endswith(".md"): continue
    with open(os.path.join(base, f), "r", encoding="utf-8") as fh:
        c = fh.read(500)
    if "clippings" in c:
        print(f)
'''], capture_output=True, text=True, cwd=base)
files = [f for f in result.stdout.strip().split('\n') if f]
print(f'Found {len(files)} unprocessed files')
for f in files:
    print(f'  {f}')
print()
