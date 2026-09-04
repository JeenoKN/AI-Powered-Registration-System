import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update logo Dragging state to use layout snapping
new_state = '''
// Logo Layout Dragging State
const isDraggingLogo = ref(false)
const ghostPos = ref({ x: 0, y: 0 })
const dragOffset = ref({ x: 0, y: 0 })
const hoverZone = ref(null)

const logoLayout = computed({
  get: () => {
    if (!generatedForm.value || !generatedForm.value.theme) return 'left'
    return generatedForm.value.theme.logo_layout || 'left'
  },
  set: (val) => {
    if (!generatedForm.value) return
    if (!generatedForm.value.theme) generatedForm.value.theme = {}
    generatedForm.value.theme.logo_layout = val
  }
})

const logoAlign = computed({
  get: () => {
    if (!generatedForm.value || !generatedForm.value.theme) return 'left'
    return generatedForm.value.theme.logo_align || 'left'
  },
  set: (val) => {
    if (!generatedForm.value) return
    if (!generatedForm.value.theme) generatedForm.value.theme = {}
    generatedForm.value.theme.logo_align = val
  }
})

const startLogoDrag = (e) => {
  if (e.target.closest('.form-logo-overlay')) return // Don't drag on upload overlay
  if (e.target.tagName.toLowerCase() === 'input') return
  
  // Prevent drag if clicking on the bottom-right resize handle
  const rect = e.currentTarget.getBoundingClientRect()
  if (e.clientX > rect.right - 20 && e.clientY > rect.bottom - 20) {
    return // Let CSS resize handle it
  }

  isDraggingLogo.value = true
  dragOffset.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
  ghostPos.value = { x: e.clientX - dragOffset.value.x, y: e.clientY - dragOffset.value.y }
  hoverZone.value = logoLayout.value

  document.addEventListener('mousemove', onLogoDrag)
  document.addEventListener('mouseup', stopLogoDrag)
  
  // Prevent text selection while dragging
  e.preventDefault()
}

const onLogoDrag = (e) => {
  if (!isDraggingLogo.value) return
  ghostPos.value = {
    x: e.clientX - dragOffset.value.x,
    y: e.clientY - dragOffset.value.y
  }
  
  // Determine drop zone based on mouse position relative to header
  const headerEl = document.querySelector('.form-header-container')
  if (headerEl) {
    const hRect = headerEl.getBoundingClientRect()
    // Relative mouse Y inside header
    const relY = e.clientY - hRect.top
    const relX = e.clientX - hRect.left
    
    if (relY < 60) {
      hoverZone.value = 'top'
      if (relX > hRect.width / 2) {
        logoAlign.value = 'center'
      } else {
        logoAlign.value = 'left'
      }
    } else {
      if (relX < hRect.width / 2) hoverZone.value = 'left'
      else hoverZone.value = 'right'
    }
  }
}

const stopLogoDrag = () => {
  if (isDraggingLogo.value && hoverZone.value) {
    logoLayout.value = hoverZone.value
  }
  isDraggingLogo.value = false
  hoverZone.value = null
  document.removeEventListener('mousemove', onLogoDrag)
  document.removeEventListener('mouseup', stopLogoDrag)
}
'''

# Replace old logo dragging state
old_state_match = re.search(r'// Logo Dragging State.*?const stopLogoDrag = \(\) => \{.*?\n\}', text, re.DOTALL)
if old_state_match:
    text = text[:old_state_match.start()] + new_state + text[old_state_match.end():]

# 2. Update the HTML structure of the header
# We need to wrap the header to support top, left, right zones
old_header_match = re.search(r'<div style="font-size: 13px; color: #64748b; margin-bottom: 12px;.*?</header>', text, re.DOTALL)
if old_header_match:
    new_header = '''              <div style="font-size: 13px; color: #64748b; margin-bottom: 12px; text-align: left; font-style: italic; display: flex; align-items: center; gap: 6px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
                Drag anywhere on the logo to move it. Use bottom-right corner to resize.
              </div>
              
              <div class="form-header-container" style="position: relative; display: flex; flex-direction: column; gap: 16px; min-height: 120px;" :class="{ 'dragging': isDraggingLogo }">
                
                <!-- Drop Zones Indicators (visible when dragging) -->
                <div v-if="isDraggingLogo" class="drop-zone top-zone" :class="{ active: hoverZone === 'top' }" style="position: absolute; top: -10px; left: 0; right: 0; height: 60px; border: 2px dashed #93c5fd; background: rgba(147, 197, 253, 0.1); border-radius: 12px; z-index: 10;"></div>
                <div v-if="isDraggingLogo" class="drop-zone left-zone" :class="{ active: hoverZone === 'left' }" style="position: absolute; top: 60px; left: -10px; width: 140px; bottom: -10px; border: 2px dashed #93c5fd; background: rgba(147, 197, 253, 0.1); border-radius: 12px; z-index: 10;"></div>
                <div v-if="isDraggingLogo" class="drop-zone right-zone" :class="{ active: hoverZone === 'right' }" style="position: absolute; top: 60px; right: -10px; width: 140px; bottom: -10px; border: 2px dashed #93c5fd; background: rgba(147, 197, 253, 0.1); border-radius: 12px; z-index: 10;"></div>

                <!-- Ghost Logo (Follows cursor) -->
                <div v-if="isDraggingLogo" class="form-logo-ghost" :style="{ position: 'fixed', left: ghostPos.x + 'px', top: ghostPos.y + 'px', zIndex: 9999, opacity: 0.8, pointerEvents: 'none', width: '120px', height: '120px', border: '2px dashed #38bdf8', borderRadius: '12px', background: '#f8fafc' }">
                   <div style="display: flex; height: 100%; align-items: center; justify-content: center; color: #38bdf8;">
                     <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg> Moving
                   </div>
                </div>

                <!-- Top Logo Area -->
                <div v-show="!isDraggingLogo && logoLayout === 'top'" class="logo-area-top" :style="{ display: 'flex', justifyContent: logoAlign === 'center' ? 'center' : 'flex-start', width: '100%' }">
                  <div class="form-logo-widget" @mousedown="startLogoDrag" style="position: relative; resize: both; overflow: hidden; width: 120px; height: 120px; min-width: 80px; min-height: 80px; max-width: 300px; max-height: 300px; border: 2px dashed #cbd5e1; border-radius: 12px; box-shadow: 0 0 15px rgba(56, 189, 248, 0.15); background: #f8fafc; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: move; flex-shrink: 0; transition: box-shadow 0.2s;">
                    <!-- Resize Handle Hint -->
                    <div style="position: absolute; bottom: 2px; right: 2px; width: 12px; height: 12px; cursor: nwse-resize; z-index: 20;"></div>
                    <img v-if="generatedForm?.theme?.logo_url" :src="generatedForm.theme.logo_url" class="form-logo-image" style="width: 100%; height: 100%; object-fit: contain; padding: 12px; pointer-events: none;" />
                    <div class="form-logo-placeholder" v-else style="display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 12px; pointer-events: none;">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                      <span style="font-size: 11px; color: #64748b; text-align: center; font-weight: 600; line-height: 1.2;">Upload Logo</span>
                    </div>
                    <div class="form-logo-overlay" @click="logoFileInput.click()" style="position: absolute; inset: 0; background: rgba(0,0,0,0.5); display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; cursor: pointer; color: white; z-index: 15;">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="margin-bottom: 4px;"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                    </div>
                  </div>
                </div>

                <header class="form-header" :style="{ display: 'flex', flexDirection: logoLayout === 'right' ? 'row-reverse' : 'row', alignItems: 'flex-start', gap: '24px', position: 'relative', textAlign: 'left', width: '100%', opacity: isDraggingLogo ? 0.5 : 1 }">
                  <!-- Side Logo Area -->
                  <div v-show="!isDraggingLogo && (logoLayout === 'left' || logoLayout === 'right')" class="logo-area-side">
                    <div class="form-logo-widget" @mousedown="startLogoDrag" style="position: relative; resize: both; overflow: hidden; width: 120px; height: 120px; min-width: 80px; min-height: 80px; max-width: 300px; max-height: 300px; border: 2px dashed #cbd5e1; border-radius: 12px; box-shadow: 0 0 15px rgba(56, 189, 248, 0.15); background: #f8fafc; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: move; flex-shrink: 0; transition: box-shadow 0.2s;">
                      <!-- Resize Handle Hint -->
                      <div style="position: absolute; bottom: 2px; right: 2px; width: 12px; height: 12px; cursor: nwse-resize; z-index: 20;"></div>
                      <img v-if="generatedForm?.theme?.logo_url" :src="generatedForm.theme.logo_url" class="form-logo-image" style="width: 100%; height: 100%; object-fit: contain; padding: 12px; pointer-events: none;" />
                      <div class="form-logo-placeholder" v-else style="display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 12px; pointer-events: none;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                        <span style="font-size: 11px; color: #64748b; text-align: center; font-weight: 600; line-height: 1.2;">Upload Logo</span>
                      </div>
                      <div class="form-logo-overlay" @click="logoFileInput.click()" style="position: absolute; inset: 0; background: rgba(0,0,0,0.5); display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; cursor: pointer; color: white; z-index: 15;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="margin-bottom: 4px;"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                      </div>
                    </div>
                  </div>
                  
                  <input type="file" ref="logoFileInput" @change="handleLogoUpload" accept="image/*" hidden />
                  
                  <div class="form-title-section" style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
                    <input v-model="generatedForm.title" class="form-title-input" placeholder="Form Title" style="text-align: left; font-size: 28px; padding-left: 0; width: 100%; box-sizing: border-box;" />
                    <textarea v-model="generatedForm.description" class="form-description-input" placeholder="Form Description" style="text-align: left; min-height: 60px; padding-left: 0; width: 100%; box-sizing: border-box;"></textarea>
                  </div>
                </header>
              </div>'''
    text = text[:old_header_match.start()] + new_header + text[old_header_match.end():]

# 3. Apply changes
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated dragging to use layout zones")
