import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'aurora-shell' in line or 'app-layout' in line or '<!-- Modals' in line:
        print(f'{i+1}: {line.rstrip()}')
