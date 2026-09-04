import sys

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'dir-card-actions' in line and i > 2270:
        for j in range(max(0, i-2), min(len(lines), i+15)):
            try:
                print(f'{j+1}: {lines[j].rstrip()}')
            except UnicodeEncodeError:
                print(f'{j+1}: [Unicode Content]')
        break
