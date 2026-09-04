import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add the state for logo resizing and toolbar
new_state = '''
// Logo Resize & Layout State
const logoSize = computed({
  get: () => {
    if (!generatedForm.value || !generatedForm.value.theme) return 120
    return generatedForm.value.theme.logo_size || 120
  },
  set: (val) => {
    if (!generatedForm.value) return
    if (!generatedForm.value.theme) generatedForm.value.theme = {}
    generatedForm.value.theme.logo_size = val
  }
})

const isResizingLogo = ref(false)
const showLogoToolbar = ref(false)

const startLogoResize = (e) => {
  e.stopPropagation()
  e.preventDefault()
  isResizingLogo.value = true
  
  const startX = e.clientX
  const startSize = logoSize.value
  
  const onMouseMove = (ev) => {
    const diff = ev.clientX - startX
    let newSize = startSize + diff
    if (newSize < 60) newSize = 60
    if (newSize > 350) newSize = 350
    logoSize.value = newSize
  }
  
  const onMouseUp = () => {
    isResizingLogo.value = false
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }
  
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

const removeLogo = () => {
  if (generatedForm.value && generatedForm.value.theme) {
    generatedForm.value.theme.logo_url = null
  }
}

// Ensure old state variables like logoLayout and startLogoDrag are not redefined
'''

# We will just inject these right before startLogoDrag
match = re.search(r'const startLogoDrag =', text)
if match and 'const startLogoResize =' not in text:
    text = text[:match.start()] + new_state + text[match.start():]

# We should also remove the old CSS resize check in startLogoDrag since we have a dedicated handle
# old: if (e.clientX > rect.right - 20 ... ) return
text = re.sub(r'const rect = e.currentTarget.getBoundingClientRect\(\)\s*if \(e.clientX > rect.right - 20 && e.clientY > rect.bottom - 20\) \{\s*return // Let CSS resize handle it\s*\}', '', text)


# 2. Re-write the form-header-container HTML
new_html = '''              <div class="form-header-container" style="position: relative; display: flex; flex-direction: column; gap: 16px; min-height: 120px;" :class="{ 'dragging': isDraggingLogo }">
                
                <!-- Drop Zones Indicators (visible when dragging) -->
                <div v-if="isDraggingLogo" class="drop-zone top-zone" :class="{ active: hoverZone === 'top' }" style="position: absolute; top: -10px; left: 0; right: 0; height: 60px; border: 2px dashed #93c5fd; background: rgba(147, 197, 253, 0.1); border-radius: 12px; z-index: 10;"></div>
                <div v-if="isDraggingLogo" class="drop-zone left-zone" :class="{ active: hoverZone === 'left' }" style="position: absolute; top: 60px; left: -10px; width: 140px; bottom: -10px; border: 2px dashed #93c5fd; background: rgba(147, 197, 253, 0.1); border-radius: 12px; z-index: 10;"></div>
                <div v-if="isDraggingLogo" class="drop-zone right-zone" :class="{ active: hoverZone === 'right' }" style="position: absolute; top: 60px; right: -10px; width: 140px; bottom: -10px; border: 2px dashed #93c5fd; background: rgba(147, 197, 253, 0.1); border-radius: 12px; z-index: 10;"></div>

                <!-- Ghost Logo (Follows cursor) -->
                <div v-if="isDraggingLogo" class="form-logo-ghost" :style="{ position: 'fixed', left: ghostPos.x + 'px', top: ghostPos.y + 'px', zIndex: 9999, opacity: 0.8, pointerEvents: 'none', width: logoSize + 'px', height: logoSize + 'px', border: '2px dashed #38bdf8', borderRadius: '12px', background: '#f8fafc' }">
                   <div style="display: flex; height: 100%; align-items: center; justify-content: center; color: #38bdf8;">
                     <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg> Moving
                   </div>
                </div>

                <!-- Top Logo Area -->
                <div v-show="!isDraggingLogo && logoLayout === 'top'" class="logo-area-top" :style="{ display: 'flex', justifyContent: logoAlign === 'center' ? 'center' : 'flex-start', width: '100%', position: 'relative' }">
                  <!-- Toolbar -->
                  <div class="logo-toolbar" v-if="generatedForm?.theme?.logo_url" style="position: absolute; top: -45px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); display: flex; gap: 4px; padding: 4px; z-index: 50; transition: opacity 0.2s;" :style="{ opacity: showLogoToolbar ? 1 : 0, pointerEvents: showLogoToolbar ? 'auto' : 'none', left: logoAlign === 'center' ? '50%' : '0', transform: logoAlign === 'center' ? 'translateX(-50%)' : 'none' }">
                    <button @click="logoAlign = 'left'" :style="logoAlign === 'left' ? 'background: #f1f5f9; color: #0f172a;' : 'color: #64748b;'" style="border: none; background: transparent; padding: 6px; border-radius: 4px; cursor: pointer;" title="Align Left"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="21" y1="6" x2="3" y2="6"/><line x1="15" y1="12" x2="3" y2="12"/><line x1="17" y1="18" x2="3" y2="18"/></svg></button>
                    <button @click="logoAlign = 'center'" :style="logoAlign === 'center' ? 'background: #f1f5f9; color: #0f172a;' : 'color: #64748b;'" style="border: none; background: transparent; padding: 6px; border-radius: 4px; cursor: pointer;" title="Align Center"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="21" y1="6" x2="3" y2="6"/><line x1="19" y1="12" x2="5" y2="12"/><line x1="21" y1="18" x2="3" y2="18"/></svg></button>
                    <div style="width: 1px; background: #e2e8f0; margin: 4px;"></div>
                    <button @click="removeLogo" style="border: none; background: transparent; padding: 6px; border-radius: 4px; cursor: pointer; color: #ef4444;" title="Remove Logo"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>
                  </div>
                  
                  <div class="form-logo-widget" @mouseenter="showLogoToolbar = true" @mouseleave="showLogoToolbar = false" @mousedown="startLogoDrag" :style="{ width: logoSize + 'px', height: logoSize + 'px' }" style="position: relative; border: 2px dashed transparent; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: move; flex-shrink: 0; transition: border-color 0.2s;" onmouseover="this.style.borderColor='#cbd5e1'" onmouseout="this.style.borderColor='transparent'">
                    
                    <img v-if="generatedForm?.theme?.logo_url" :src="generatedForm.theme.logo_url" class="form-logo-image" style="width: 100%; height: 100%; object-fit: contain; padding: 12px; pointer-events: none;" />
                    
                    <div class="form-logo-placeholder" v-else style="display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 12px; pointer-events: none; border: 2px dashed #cbd5e1; border-radius: 12px; width: 100%; height: 100%; justify-content: center; background: #f8fafc;">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                      <span style="font-size: 11px; color: #64748b; text-align: center; font-weight: 600; line-height: 1.2;">Upload Logo</span>
                    </div>
                    
                    <!-- Upload overlay triggers on click -->
                    <div v-if="!generatedForm?.theme?.logo_url" class="form-logo-overlay" @click.stop="logoFileInput.click()" style="position: absolute; inset: 0; cursor: pointer; z-index: 15;"></div>
                    <div v-else class="form-logo-overlay" @click.stop="logoFileInput.click()" style="position: absolute; inset: 0; background: rgba(0,0,0,0.4); display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; cursor: pointer; color: white; z-index: 15; border-radius: 12px;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                    </div>

                    <!-- Custom Resize Handle -->
                    <div @mousedown="startLogoResize" style="position: absolute; bottom: 0; right: 0; width: 16px; height: 16px; cursor: nwse-resize; z-index: 20; display: flex; align-items: flex-end; justify-content: flex-end; padding: 4px; background: transparent;" title="Resize logo">
                      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="3" stroke-linecap="round"><polyline points="21 15 21 21 15 21"/><line x1="21" y1="21" x2="15" y2="15"/><polyline points="9 21 3 21 3 15"/><line x1="3" y1="21" x2="9" y2="15"/></svg>
                    </div>
                  </div>
                </div>

                <header class="form-header" :style="{ display: 'flex', flexDirection: logoLayout === 'right' ? 'row-reverse' : 'row', alignItems: 'flex-start', gap: '24px', position: 'relative', textAlign: 'left', width: '100%', opacity: isDraggingLogo ? 0.5 : 1 }">
                  <!-- Side Logo Area -->
                  <div v-show="!isDraggingLogo && (logoLayout === 'left' || logoLayout === 'right')" class="logo-area-side" style="position: relative;">
                    <!-- Toolbar -->
                    <div class="logo-toolbar" v-if="generatedForm?.theme?.logo_url" style="position: absolute; top: -45px; left: 50%; transform: translateX(-50%); background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); display: flex; gap: 4px; padding: 4px; z-index: 50; transition: opacity 0.2s;" :style="{ opacity: showLogoToolbar ? 1 : 0, pointerEvents: showLogoToolbar ? 'auto' : 'none' }">
                      <button @click="removeLogo" style="border: none; background: transparent; padding: 6px; border-radius: 4px; cursor: pointer; color: #ef4444;" title="Remove Logo"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>
                    </div>

                    <div class="form-logo-widget" @mouseenter="showLogoToolbar = true" @mouseleave="showLogoToolbar = false" @mousedown="startLogoDrag" :style="{ width: logoSize + 'px', height: logoSize + 'px' }" style="position: relative; border: 2px dashed transparent; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: move; flex-shrink: 0; transition: border-color 0.2s;" onmouseover="this.style.borderColor='#cbd5e1'" onmouseout="this.style.borderColor='transparent'">
                      
                      <img v-if="generatedForm?.theme?.logo_url" :src="generatedForm.theme.logo_url" class="form-logo-image" style="width: 100%; height: 100%; object-fit: contain; padding: 12px; pointer-events: none;" />
                      
                      <div class="form-logo-placeholder" v-else style="display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 12px; pointer-events: none; border: 2px dashed #cbd5e1; border-radius: 12px; width: 100%; height: 100%; justify-content: center; background: #f8fafc;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                        <span style="font-size: 11px; color: #64748b; text-align: center; font-weight: 600; line-height: 1.2;">Upload Logo</span>
                      </div>
                      
                      <div v-if="!generatedForm?.theme?.logo_url" class="form-logo-overlay" @click.stop="logoFileInput.click()" style="position: absolute; inset: 0; cursor: pointer; z-index: 15;"></div>
                      <div v-else class="form-logo-overlay" @click.stop="logoFileInput.click()" style="position: absolute; inset: 0; background: rgba(0,0,0,0.4); display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; cursor: pointer; color: white; z-index: 15; border-radius: 12px;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                      </div>

                      <!-- Custom Resize Handle -->
                      <div @mousedown="startLogoResize" style="position: absolute; bottom: 0; right: 0; width: 16px; height: 16px; cursor: nwse-resize; z-index: 20; display: flex; align-items: flex-end; justify-content: flex-end; padding: 4px; background: transparent;" title="Resize logo">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="3" stroke-linecap="round"><polyline points="21 15 21 21 15 21"/><line x1="21" y1="21" x2="15" y2="15"/><polyline points="9 21 3 21 3 15"/><line x1="3" y1="21" x2="9" y2="15"/></svg>
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

old_header_match = re.search(r'<div class="form-header-container".*?</header>\s*</div>', text, re.DOTALL)
if old_header_match:
    text = text[:old_header_match.start()] + new_html + text[old_header_match.end():]
else:
    print("Could not find old header match to replace HTML")

# 3. Clean up the placeholder italic text since it's redundant now
# It was added just above the form-header-container
text = re.sub(r'<div style="font-size: 13px; color: #64748b; margin-bottom: 12px;[^>]*>.*?</div>\s*<div class="form-header-container"', '<div class="form-header-container"', text, flags=re.DOTALL)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Injected toolbar and custom resize handler")
