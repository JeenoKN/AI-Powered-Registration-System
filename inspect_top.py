import re
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'<div[^>]*class="logo-area-top"[^>]*>', text)
if match: print('TOP:', match.group(0))

match2 = re.search(r'<div[^>]*class="logo-area-side"[^>]*>', text)
if match2: print('SIDE:', match2.group(0))
