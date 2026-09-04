with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

fixes = [
    # Templates section - dir-card-accent
    (
        ':style="\\background: "',
        ':style="{ background: template.theme_color || \'#6366f1\' }"'
    ),
    # Templates section - dir-card-icon background
    (
        ':style="\\background: 18"',
        ':style="{ background: (template.theme_color || \'#6366f1\') + \'18\' }"'
    ),
]

for old, new in fixes:
    if old in text:
        text = text.replace(old, new)
        print(f"Fixed: {old[:50]}")
    else:
        print(f"NOT FOUND: {old[:50]}")

# Also fix any template stroke bindings that broke
# Check for :stroke with empty value
import re

# Fix broken :stroke in templates section
text = re.sub(
    r':stroke=""',
    ':stroke="template.theme_color || \'#6366f1\'"',
    text
)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)
print("Done")
