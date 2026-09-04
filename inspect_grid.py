import re
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'<div class="preview-canvas-column"[^>]*>', text)
if match: print(match.group(0))

match2 = re.search(r'<div class="canvas-glass-panel"[^>]*>', text)
if match2: print(match2.group(0))
