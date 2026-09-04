import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'<div class="chat-input-row"[^>]*>.*?(?=</div>\s*</div>\s*<div class="workspace-side-panel)', text, re.DOTALL)
if match:
    print(match.group(0))
else:
    print("chat-input-row not found")
