import re
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'<div class="form-logo-widget"[^>]*>', text)
if match: print(match.group(0))
