import re
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# We need to replace the broken :style entirely
pattern = r':style="\{\s*transform:\s*\t*ranslate\(px,\s*px\).*?\}"'
proper_style = ':style="{ transform: \'translate(\' + logoPos.x + \'px, \' + logoPos.y + \'px)\', zIndex: isDraggingLogo ? 50 : 10, transition: isDraggingLogo ? \'none\' : \'transform 0.1s\' }"'

text = re.sub(pattern, proper_style, text)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed broken transform style")
