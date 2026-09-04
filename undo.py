import re
import os

# 1. Revert style.css
with open(r'e:\NewSystem\frontend-vue\src\style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Restore --app-bg to previous version (the 3-color gradient we had before 23:15)
# Actually, the user's 9:58 PM was right after the "Ambient Aura" was deployed.
# At 9:48 PM, I injected the Ambient Aura CSS block and replaced the global --app-bg.
# Wait, before 23:15, --app-bg was:
original_app_bg = '''  --app-bg: 
    url('data:image/svg+xml;utf8,<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><filter id="noiseFilter"><feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="3" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(%23noiseFilter)" opacity="0.03"/></svg>'),
    radial-gradient(circle at 10% 20%, rgba(148, 163, 184, 0.12), transparent 40%), 
    radial-gradient(circle at 90% 80%, rgba(99, 102, 241, 0.08), transparent 30%), 
    linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);'''

css = re.sub(r'  --app-bg:[\s\S]*?(?=  --surface-glass:)', original_app_bg + '\n', css)

# Restore .app-shell-layout background
if '.app-shell-layout {' in css and 'background:' not in css.split('.app-shell-layout {')[1].split('}')[0]:
    css = css.replace('.app-shell-layout {\n  display: flex;\n  min-height: 100vh;\n}', 
                      '.app-shell-layout {\n  display: flex;\n  min-height: 100vh;\n  background: var(--app-bg);\n}')

# Restore .sidebar-nav background and color
css = re.sub(r'(\.sidebar-nav\s*\{[\s\S]*?)(width: 250px;)', 
             r'\1background: var(--theme-dark-sidebar) !important;\n  color: var(--theme-text-on-dark) !important;\n  \2', css)

# We need to append the removed classes back to style.css:
missing_css = '''
.sidebar-nav .nav-item:hover {
  background: var(--theme-dark-active) !important;
}

.function-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 8px;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid transparent;
}
.function-item:hover {
  background: white;
  border-color: rgba(99, 102, 241, 0.2);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.function-item.active {
  background: white;
  border-color: var(--primary-indigo);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}
'''
css += missing_css

# Restore chat bubble borders
css = css.replace('border-radius: 20px 20px 20px 4px', 'border-radius: 12px 12px 12px 2px')
css = css.replace('border-radius: 20px 20px 4px 20px', 'border-radius: 12px 12px 2px 12px')
css = css.replace('box-shadow: 0 4px 12px rgba(0,0,0,0.03)', 'box-shadow: 0 1px 3px rgba(0,0,0,0.05)')

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("Restored style.css")
