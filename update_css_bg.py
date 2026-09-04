import re

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace --app-bg with the new mesh gradient
new_bg = '''  --app-bg: 
    radial-gradient(circle at 15% 50%, rgba(245, 230, 220, 0.4), transparent 50%),
    radial-gradient(circle at 85% 30%, rgba(250, 225, 235, 0.4), transparent 50%),
    radial-gradient(circle at 50% 80%, rgba(230, 225, 240, 0.4), transparent 50%),
    linear-gradient(135deg, #fdfbf7 0%, #f4f3f0 100%);'''

text = re.sub(r'--app-bg:[\s\S]*?(?=--surface-glass:)', new_bg + '\n  ', text)

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated --app-bg in style.css")
