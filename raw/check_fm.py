import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

root = r'C:\Users\yefan.LAPTOP-T0BIR3IU\Documents\База\raw'
files = sorted([f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f)) and f.endswith('.md')])

for fn in files:
    fp = os.path.join(root, fn)
    with open(fp, 'r', encoding='utf-8') as fh:
        content = fh.read()
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if m:
        fm = m.group(1)
        bits = []
        for k in ['type','number','name','year','actualization_date','tags','source','created']:
            bits.append('1' if k+':' in fm else '0')
        desc_m = re.search(r'description:\s*"([^"]*)"', fm)
        desc_len = len(desc_m.group(1)) if desc_m else 0
        bits.append(str(desc_len))
        print(' '.join(bits) + ' | ' + fn)
    else:
        print('NO_FM 00 000 | ' + fn)
