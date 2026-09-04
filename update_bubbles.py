import re

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Soften the chat bubbles
css = css.replace('border-radius: 12px 12px 12px 2px', 'border-radius: 20px 20px 20px 4px')
css = css.replace('border-radius: 12px 12px 2px 12px', 'border-radius: 20px 20px 4px 20px')
css = css.replace('box-shadow: 0 1px 3px rgba(0,0,0,0.05)', 'box-shadow: 0 4px 12px rgba(0,0,0,0.03)')

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("Updated chat bubbles.")
