import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'class="ai-creator-container"' in line:
        print(f"ai-creator-container found at line {i+1}")
    if 'id="ai-creator"' in line:
        print(f"id=ai-creator found at line {i+1}")
