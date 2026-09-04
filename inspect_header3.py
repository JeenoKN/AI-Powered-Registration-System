import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('<div class="form-logo-container"')
if start != -1:
    header_start = text.rfind('<header', 0, start)
    header_end = text.find('</header>', start)
    print(text[header_start:header_end+9])
else:
    print("form-logo-container not found")
