import re
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix startLogoDrag
old_func_match = re.search(r'const startLogoDrag = \(e\) => \{.*?document\.addEventListener\(\'mouseup\', stopLogoDrag\)\s*(?://[^\n]*\s*)*\}', text, re.DOTALL)

if old_func_match:
    new_func = '''const startLogoDrag = (e) => {
  if (e.target.closest('.form-logo-overlay')) return 
  if (e.target.tagName.toLowerCase() === 'input') return
  
  const rect = e.currentTarget.getBoundingClientRect()
  
  isDraggingLogo.value = true
  dragOffset.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
  ghostPos.value = { x: e.clientX - dragOffset.value.x, y: e.clientY - dragOffset.value.y }
  hoverZone.value = logoLayout.value

  document.addEventListener('mousemove', onLogoDrag)
  document.addEventListener('mouseup', stopLogoDrag)
  e.preventDefault()
}'''
    text = text[:old_func_match.start()] + new_func + text[old_func_match.end():]
else:
    print("Could not find startLogoDrag")

# Fix v-show="!isDraggingLogo" in the template so layout doesn't jump
# Top logo area
text = text.replace('v-show="!isDraggingLogo && logoLayout === \'top\'"', 'v-show="logoLayout === \'top\'" :style="{ opacity: isDraggingLogo ? 0.3 : 1 }"')
# Side logo area
text = text.replace('v-show="!isDraggingLogo && (logoLayout === \'left\' || logoLayout === \'right\')"', 'v-show="logoLayout === \'left\' || logoLayout === \'right\'" :style="{ opacity: isDraggingLogo ? 0.3 : 1 }"')

# Fix ghost logo absolute size to respect the current logoSize
# In the ghost div, we have: width: logoSize + 'px', height: logoSize + 'px'
# But since we use inline style string in python, let's just make sure it's correct.
# Let's check the drop zones visual to make them prettier
text = text.replace('height: 60px; border: 2px dashed #93c5fd;', 'height: 80px; border: 2px dashed #60a5fa; box-shadow: 0 0 10px rgba(96, 165, 250, 0.2);')

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed startLogoDrag and layout jumping")
