import re
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('<div class="preview-canvas-column"')
if start != -1:
    print(text[start:start+1000].encode('ascii', 'ignore').decode('ascii'))
