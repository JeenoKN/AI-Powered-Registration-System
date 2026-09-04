import re

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'\.app-shell-layout\s*\{[^}]*\}', text)
if match:
    print(match.group(0))
else:
    print("app-shell-layout not found in style.css")
