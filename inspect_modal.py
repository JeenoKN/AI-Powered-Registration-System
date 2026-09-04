import re
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('<!-- View Form Modal -->')
if start != -1:
    end = text.find('</Transition>', start)
    print(text[start:end+15])
