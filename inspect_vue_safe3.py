import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "currentTab === 'create'" in line:
        print(f"currentTab === 'create' found at line {i+1}")
