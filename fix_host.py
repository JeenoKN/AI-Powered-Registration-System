with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

import re
old = r'<div v-show="logoLayout === \'top\'" :style="{ opacity: isDraggingLogo ? 0.3 : 1 }" class="logo-area-top" :style="{ display: \'flex\', justifyContent: logoAlign === \'center\' ? \'center\' : \'flex-start\', width: \'100%\', position: \'relative\' }">'
new = r'<div v-show="logoLayout === \'top\'" class="logo-area-top" :style="{ opacity: isDraggingLogo ? 0.3 : 1, display: \'flex\', justifyContent: logoAlign === \'center\' ? \'center\' : \'flex-start\', width: \'100%\', position: \'relative\' }">'

if old in text:
    text = text.replace(old, new)
    with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Replaced exact string.")
else:
    print("Could not find exact string.")
    match = re.search(r'<div[^>]*class="logo-area-top"[^>]*>', text)
    if match: print('Current HOST TOP:', match.group(0))

