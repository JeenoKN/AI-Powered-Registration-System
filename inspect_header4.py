import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'              <header class="form-header">.*?</header>', text, re.DOTALL)
if match:
    # write to a file to examine
    with open('current_header.txt', 'w', encoding='utf-8') as out:
        out.write(match.group(0))
    print("Wrote current_header.txt")
