import sys

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'class="dir-search-input"' in line:
        for j in range(max(0, i-4), min(len(lines), i+4)):
            try:
                print(f'{j+1}: {lines[j].rstrip()}')
            except UnicodeEncodeError:
                print(f'{j+1}: [Unicode Content]')
        break
