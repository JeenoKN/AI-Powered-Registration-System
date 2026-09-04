import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('<div class="form-logo-widget"')
if start != -1:
    # Find enclosing header
    header_start = text.rfind('<header', 0, start)
    header_end = text.find('</header>', start)
    print(text[header_start:header_end+9])
else:
    print("form-logo-widget not found")
