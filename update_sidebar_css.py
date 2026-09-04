import re

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Remove background and color from .sidebar-nav
css = re.sub(r'(\.sidebar-nav\s*\{[^}]*)background:\s*var\(--theme-dark-sidebar\)\s*!important;', r'\1', css)
css = re.sub(r'(\.sidebar-nav\s*\{[^}]*)color:\s*var\(--theme-text-on-dark\)\s*!important;', r'\1', css)

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'w', encoding='utf-8') as f:
    f.write(css)

# Update AdminView.vue sidebar
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    vue = f.read()

vue = vue.replace(
    '<aside class="sidebar-nav">',
    '<aside class="sidebar-nav bg-gradient-to-b from-[#3a3a3a]/90 to-[#2a2a2a]/95 backdrop-blur-xl border-r border-white/10 text-white/90">'
)

# Refactor nav items hover state
# Old: <a href="#" class="nav-item" :class="{ active: currentTab === 'dashboard' }" @click.prevent="currentTab = 'dashboard'">
# Tailwind: hover:bg-white/10 rounded-xl hover:scale-105 transition-all duration-300
vue = re.sub(r'class="nav-item"', r'class="nav-item hover:bg-white/10 rounded-xl hover:scale-105 transition-all duration-300"', vue)

# Also remove .nav-item hover styles from style.css
css = re.sub(r'\.sidebar-nav \.nav-item:hover\s*\{[^}]*\}', '', css)

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'w', encoding='utf-8') as f:
    f.write(css)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(vue)

print("Updated sidebar to dark glassmorphism.")
