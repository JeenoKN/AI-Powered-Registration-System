import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the <template> section only
template_start = content.find('<template>')
template_end = content.rfind('</template>') + len('</template>')
template_content = content[template_start:template_end]

# Count open vs close div tags (rough check)
open_divs = len(re.findall(r'<div[\s>]', template_content))
close_divs = len(re.findall(r'</div>', template_content))
print(f"Open <div>: {open_divs}")
print(f"Close </div>: {close_divs}")
print(f"Difference: {open_divs - close_divs}")

# Check aurora-shell and app-layout
print('\nAurora-shell occurrences:')
for m in re.finditer(r'aurora-shell|app-layout', template_content):
    start = max(0, m.start()-30)
    end = min(len(template_content), m.end()+50)
    print(f'  ...{template_content[start:end].strip()[:80]}...')
