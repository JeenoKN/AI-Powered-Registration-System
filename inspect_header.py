with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('<div class="form-header-container"')
if start != -1:
    end = text.find('</header>', start)
    print(text[start:end+9].encode('ascii', 'ignore').decode('ascii'))
