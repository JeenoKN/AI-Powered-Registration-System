import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add state variables for dragging
state_injection = '''
// Logo Dragging State
const logoPos = ref({ x: 0, y: 0 })
const isDraggingLogo = ref(false)
const dragOffset = ref({ x: 0, y: 0 })

const startLogoDrag = (e) => {
  if (e.target.closest('.form-logo-overlay')) return // Don't drag when clicking replace overlay
  isDraggingLogo.value = true
  dragOffset.value = {
    x: e.clientX - logoPos.value.x,
    y: e.clientY - logoPos.value.y
  }
  document.addEventListener('mousemove', onLogoDrag)
  document.addEventListener('mouseup', stopLogoDrag)
}

const onLogoDrag = (e) => {
  if (!isDraggingLogo.value) return
  logoPos.value = {
    x: e.clientX - dragOffset.value.x,
    y: e.clientY - dragOffset.value.y
  }
}

const stopLogoDrag = () => {
  isDraggingLogo.value = false
  document.removeEventListener('mousemove', onLogoDrag)
  document.removeEventListener('mouseup', stopLogoDrag)
}
'''

# Inject into script setup
if 'const startLogoDrag' not in text:
    script_match = re.search(r'const handleLogoUpload = async \(event\) => \{.*?\n\}', text, re.DOTALL)
    if script_match:
        text = text[:script_match.end()] + '\n' + state_injection + text[script_match.end():]

# 2. Modify the logo widget HTML to use dynamic styles and mouse events
# The current logo widget: <div class="form-logo-widget" style="position: relative; resize: both; ...
# We'll make it absolutely positioned if it has moved, or we just always use transform.
old_widget_match = re.search(r'<div class="form-logo-widget"[^>]+>', text)
if old_widget_match:
    old_widget = old_widget_match.group(0)
    # We will replace position: relative with absolute positioning or transform
    new_widget = old_widget.replace('position: relative;', 'position: relative;') # keep relative for base
    # Add Vue bindings: :style="{ transform: 	ranslate(px, px), zIndex: isDraggingLogo ? 50 : 10 }"
    # Add @mousedown="startLogoDrag"
    new_widget = new_widget.replace('class="form-logo-widget"', 'class="form-logo-widget" :style="{ transform: 	ranslate(px, px), zIndex: isDraggingLogo ? 50 : 10, transition: isDraggingLogo ? \'none\' : \'transform 0.1s\' }" @mousedown="startLogoDrag"')
    
    text = text.replace(old_widget, new_widget)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Drag logic injected successfully.")
