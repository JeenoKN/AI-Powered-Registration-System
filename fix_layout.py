import re
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace <main class="workspace-container"> with <main class="workspace-container"><div class="workspace-inner-card">
text = text.replace('<main class="workspace-container">', '<main class="workspace-container">\n      <div class="workspace-inner-card">')

# Now find the matching </main> and add </div> before it
# Look for </main> at the end of the template block.
# Usually it's right before </div> </template>
text = text.replace('</main>', '  </div>\n    </main>')

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print('Wrapped workspace-container contents into workspace-inner-card.')
