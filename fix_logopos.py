import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix logoPos computed getter/setter
old_logoPos = '''const logoPos = computed({
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
})'''

new_logoPos = '''const logoPos = computed({
  get: () => {
    if (!generatedForm.value || !generatedForm.value.theme) return { x: 0, y: 0 }
    return { 
      x: generatedForm.value.theme.logo_x || 0, 
      y: generatedForm.value.theme.logo_y || 0 
    }
  },
  set: (val) => {
    if (!generatedForm.value) return
    if (!generatedForm.value.theme) {
      generatedForm.value.theme = {}
    }
    generatedForm.value.theme.logo_x = val.x
    generatedForm.value.theme.logo_y = val.y
  }
})'''

text = text.replace(old_logoPos, new_logoPos)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed logoPos")
