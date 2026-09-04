with open(r'e:\NewSystem\frontend-vue\src\style.css', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# find the block and replace it correctly
# First, let's restore the broken part if we can, or just append it and remove the broken part.
# The tool might have messed up the CSS.
