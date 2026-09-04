import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('<div class="app-layout">', '<div class="app-shell-layout">')

text = re.sub(
    r'\.sidebar-nav\s*\{[^}]+\}',
    r'.sidebar-nav {\n  width: 232px;\n  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);\n  border-right: 1px solid rgba(255,255,255,0.06);\n  padding: 32px 24px;\n  position: fixed;\n  height: 100vh;\n  display: flex;\n  flex-direction: column;\n  z-index: 100;\n}',
    text
)

text = re.sub(
    r'\.workspace-container\s*\{[^}]+\}',
    r'.workspace-container {\n  flex: 1;\n  margin-left: 232px;\n  display: flex;\n  flex-direction: column;\n  background: transparent;\n  min-height: 100vh;\n}',
    text
)

text = re.sub(
    r'\.nav-item\s*\{[^}]+\}',
    r'.nav-item {\n  padding: 12px 16px;\n  color: var(--text-faint, #94a3b8);\n  text-decoration: none;\n  font-size: 13.5px;\n  font-weight: 600;\n  border-radius: 12px;\n  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);\n  display: flex;\n  align-items: center;\n  gap: 10px;\n}',
    text
)

text = re.sub(
    r'\.nav-item\.active\s*\{[^}]+\}',
    r'.nav-item.active {\n  background: rgba(255,255,255,0.08);\n  border: 1px solid rgba(255,255,255,0.1);\n  box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);\n  color: #ffffff;\n}',
    text
)

text = re.sub(
    r'\.global-header\s*\{[^}]+\}',
    r'.global-header {\n  height: 76px;\n  background: rgba(255,255,255,0.72);\n  backdrop-filter: blur(16px);\n  -webkit-backdrop-filter: blur(16px);\n  border-bottom: 1px solid var(--border-subtle);\n  padding: 0 32px;\n  display: flex;\n  align-items: center;\n  position: sticky;\n  top: 0;\n  z-index: 40;\n}',
    text
)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated Sidebar and Header Layout in AdminView.vue')
