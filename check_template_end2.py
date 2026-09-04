import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find </template>
for i, line in enumerate(lines):
    if '</template>' in line:
        print(f'{i+1}: {line.rstrip()}')
        # show 5 lines around it
        for j in range(max(0, i-5), min(len(lines), i+3)):
            print(f'  {j+1}: {lines[j].rstrip()}')
