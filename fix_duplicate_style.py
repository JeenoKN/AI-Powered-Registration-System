import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r':style="\{\s*opacity:\s*isDraggingLogo\s*\?\s*0\.3\s*:\s*1\s*\}"\s*class="logo-area-top"\s*:style="\{\s*display:\s*\'flex\',\s*justifyContent:\s*logoAlign\s*===\s*\'center\'\s*\?\s*\'center\'\s*:\s*\'flex-start\',\s*width:\s*\'100%\',\s*position:\s*\'relative\'\s*\}"'
replacement = 'class="logo-area-top" :style="{ opacity: isDraggingLogo ? 0.3 : 1, display: \'flex\', justifyContent: logoAlign === \'center\' ? \'center\' : \'flex-start\', width: \'100%\', position: \'relative\' }"'

text = re.sub(pattern, replacement, text)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed duplicate attribute with regex")
