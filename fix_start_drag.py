with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('const startLogoDrag = (e) => {')
end = text.find('const onLogoDrag = (e) => {', start)

if start != -1 and end != -1:
    old_func = text[start:end]
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
}

'''
    text = text[:start] + new_func + text[end:]
    
    with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
        f.write(text)
    print("startLogoDrag updated successfully")
else:
    print("Could not find startLogoDrag boundaries")
