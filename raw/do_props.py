import os, re, sys

root = r'C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw'

# Collect all .md files (exclude scripts)
files = sorted([f for f in os.listdir(root) 
                if os.path.isfile(os.path.join(root, f)) 
                and f.endswith('.md')
                and not f.startswith('fix_')
                and not f.startswith('check_')
                and not f.startswith('do_')])

outlines = []
for fn in files:
    fp = os.path.join(root, fn)
    with open(fp, 'r', encoding='utf-8') as fh:
        content = fh.read(1000)
    
    # Extract current frontmatter description
    m = re.search(r'description:\s*"([^"]*)"', content)
    if m:
        cur_desc = m.group(1)[:80].replace('\n', ' ')
    else:
        # Try single-line description without quotes
        m2 = re.search(r'description:\s*([^\n]+)', content)
        cur_desc = m2.group(1)[:80] if m2 else '(no description field)'
    
    outlines.append(f"{cur_desc} | {fn}")

report = '\n'.join(outlines)
report_path = r'C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\fm_report.txt'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)
print(f'Report written to {report_path}')
