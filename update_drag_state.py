import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the state variables to use generatedForm.theme.logo_position if available
state_injection_new = '''
// Logo Dragging State
const isDraggingLogo = ref(false)
const dragOffset = ref({ x: 0, y: 0 })

const logoPos = computed({
  get: () => {
    if (!generatedForm.value.theme) return { x: 0, y: 0 }
    return { 
      x: generatedForm.value.theme.logo_x || 0, 
      y: generatedForm.value.theme.logo_y || 0 
    }
  },
  set: (val) => {
    if (!generatedForm.value.theme) {
      generatedForm.value.theme = {}
    }
    generatedForm.value.theme.logo_x = val.x
    generatedForm.value.theme.logo_y = val.y
  }
})

const startLogoDrag = (e) => {
  if (e.target.closest('.form-logo-overlay')) return // Don't drag when clicking replace overlay
  if (e.target.tagName.toLowerCase() === 'input') return
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

# Find the old state block we just injected and replace it
old_state = '''// Logo Dragging State
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
}'''

text = text.replace(old_state, state_injection_new)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Drag state updated.")
