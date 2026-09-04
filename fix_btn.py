with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('btn-coral-view', 'btn-premium-coral')
text = text.replace('btn-premium-primary', 'btn-premium-coral')

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)
print('Replaced')
