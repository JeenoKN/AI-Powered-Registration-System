import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find the AI creator view lines
lines = text.split('\n')
start = -1
end = -1
for i, line in enumerate(lines):
    if '<div class="ai-creator-container"' in line:
        start = i
    elif '<div class="directory-view-container"' in line:
        end = i
        break

print(f"AI Creator view is between lines {start+1} and {end+1}")
