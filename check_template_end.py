import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the last </div> before </template>
total = len(lines)
print(f"Total lines: {total}")
for i in range(total-1, total-30, -1):
    print(f'{i+1}: {lines[i].rstrip()}')
