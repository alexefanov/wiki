import subprocess
r = subprocess.run(['git', 'rev-list', '--reverse', 'HEAD'], capture_output=True, text=True)
commits = r.stdout.strip().split()
print(f'Total: {len(commits)}')
for idx in [120, 125, 130, 135, 137, 139, 140, 145, 149]:
    c = commits[idx]
    r2 = subprocess.run(['git', 'show', f'{c}:raw/ГОСТ 10180-2012 Бетоны. Методы определения прочности по контрольным образцам.md'], capture_output=True, text=True, encoding='utf-8')
    if r2.returncode == 0:
        has = 'type:' in r2.stdout[:500]
        print(f'Commit {idx}: {c[:8]} has_type={has}')
    else:
        print(f'Commit {idx}: {c[:8]} not found')
