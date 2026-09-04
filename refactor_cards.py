import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove dir-card-accent
text = re.sub(r'\s*<div class="dir-card-accent" :style="ackground: \$\{[^}]+\}"></div>\n', '\n', text)

# 2. Update dir-meta-pill to date-pill-badge
text = text.replace('<span class="dir-meta-pill">', '<span class="date-pill-badge">')

# 3. Update buttons
text = text.replace('class="btn-premium-coral" @click="openViewModal(form)"', 'class="btn-premium-navy" @click="openViewModal(form)"')
text = text.replace('class="btn-premium-coral" @click="useTemplate(template)"', 'class="btn-premium-navy" @click="useTemplate(template)"')

text = text.replace('class="btn-dir-delete"', 'class="btn-icon-minimal"')
text = text.replace('class="btn-premium-danger" @click="deleteTemplate(template.id)"', 'class="btn-icon-minimal" @click="deleteTemplate(template.id)"')

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print('Card components refactored.')
