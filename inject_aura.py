# -*- coding: utf-8 -*-
with open(r'e:\NewSystem\frontend-vue\src\style.css', 'r', encoding='utf-8') as f:
    css = f.read()

import re

marker = '/* ==============================================================\n   MESH GRADIENT / AMBIENT AURA BACKGROUND SYSTEM'
idx = css.find(marker)
if idx != -1:
    css = css[:idx]

# Also strip old overhaul comment if present
marker2 = '/* ==============================================================\n   IMAGE 853344.JPG - PREMIUM OVERHAUL TOKENS'
idx2 = css.find(marker2)
if idx2 != -1:
    css = css[:idx2]

with open(r'e:\NewSystem\frontend-vue\src\style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print('Base CSS cleaned, length:', len(css))
