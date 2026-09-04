import re

# Update style.css
with open(r'e:\NewSystem\frontend-vue\src\style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Remove background from app-shell-layout
css = css.replace('  background: var(--app-bg);\n', '')
# Add body background
if 'body {' in css:
    css = re.sub(r'(body\s*\{[^}]*)background:\s*var\(--app-bg\);', r'\1background: var(--app-bg);', css)

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'w', encoding='utf-8') as f:
    f.write(css)

# Update AdminView.vue
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    vue = f.read()

vue = vue.replace(
    '<div class="app-shell-layout">', 
    '<div class="app-shell-layout max-w-screen-2xl mx-auto my-[2vh] h-[96vh] rounded-[32px] shadow-2xl shadow-black/10 overflow-hidden bg-white/40 border border-white/20">'
)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(vue)

print("Updated app-shell-layout to floating window.")
