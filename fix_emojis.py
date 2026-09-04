with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

replacements = {
    'âœ¨': '✨',
    'â†©': '↶',
    'â†²': '↷',
    'ðŸ”—': '🔄',
    'ðŸ’¡': '💡',
    'ðŸ“‚': '📁',
    'ðŸ“‘': '📄',
    'ðŸ“Š': '📊',
    'âœ…': '✅',
    'â³': '⏳',
    'ðŸ“ˆ': '📉',
    'ðŸ’»': '💻',
    'ðŸ“±': '📱',
    'ðŸ“²': '📲',
    'ðŸ–¥': '🖥️',
    'âš™ï¸': '⚙️',
    'ðŸ–¨ï¸': '🖨️',
    'ðŸ—‚ï¸': '🗂️'
}

for bad, good in replacements.items():
    text = text.replace(bad, good)

# Also fix the text "Active" and other corrupted Thai strings if they appear
text = text.replace('à¸\xa0', 'ภ') # Just an example, I won't guess Thai mojibake here.
# I already fixed the big chunks of Thai text in my previous script. The remaining ones are mostly emojis.

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print('Emoji replacements done.')
