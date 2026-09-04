import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'unified-chat-column' in line:
        # Search down for something that looks like an input or textarea
        for j in range(i, min(len(lines), i+150)):
            if '<textarea' in lines[j] or '<input' in lines[j]:
                print(f"Found input area around line {j+1}:")
                for k in range(max(0, j-5), min(len(lines), j+10)):
                    print(f'{k+1}: {lines[k].rstrip()}')
                break
        break
