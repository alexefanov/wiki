import os
base = 'raw'
# Directly test a file we can see in the directory listing
fname = 'СП 50.13330.2024. Свод правил. Тепловая защита зданий. Актуализированная редакция СНиП 23-02-2003(утв. и введен в действие Приказом Минстроя России от 15.05.2024 N 327пр).md'
path = os.path.join(base, fname)
if not os.path.exists(path):
    print(f'NOT FOUND: {fname}')
    # try first found file
    for f in os.listdir(base):
        if f.endswith('.md') and f.startswith('СП'):
            path = os.path.join(base, f)
            print(f'Using: {f}')
            break
with open(path, 'rb') as f:
    raw = f.read()
print(f'Size: {len(raw)} bytes')
print(f'First 300 raw: {raw[:300]}')
# Try to find --- patterns as bytes
idx = 0
while True:
    idx = raw.find(b'---', idx)
    if idx == -1:
        break
    print(f'--- at byte {idx}')
    idx += 1
