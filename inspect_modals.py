import re
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

print("== useTemplate ==")
match = re.search(r'const useTemplate = \w*\s*\([^)]*\)\s*=>\s*\{.*?\n\}', text, re.DOTALL)
if match:
    print(match.group(0))

print("\n== viewFormModal ==")
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'v-if="viewFormModal"' in line or 'v-if="viewModal"' in line:
        start = max(0, i-5)
        for j in range(start, i+20):
            print(f'{j+1}: {lines[j]}')
        break
