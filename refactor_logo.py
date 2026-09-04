import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

old_header = '''              <header class="form-header">
                <div class="form-logo-container">
                  <img v-if="generatedForm?.theme?.logo_url" :src="generatedForm.theme.logo_url" class="form-logo-image" />
                  <div class="form-logo-placeholder" v-else>
                    <span>No Logo</span>
                  </div>
                  <div class="form-logo-overlay" @click="logoFileInput.click()">
                    <span>??? Upload / Replace Logo</span>
                  </div>
                </div>
                <input type="file" ref="logoFileInput" @change="handleLogoUpload" accept="image/*" hidden />
                
                <input v-model="generatedForm.title" class="form-title-input" placeholder="Form Title" />
                <textarea v-model="generatedForm.description" class="form-description-input" placeholder="Form Description"></textarea>
              </header>'''

new_header = '''              <div style="font-size: 13px; color: #64748b; margin-bottom: 12px; text-align: center; font-style: italic;">
                ?? Drag the logo container to reposition it anywhere.
              </div>
              <header class="form-header" style="display: flex; align-items: flex-start; gap: 24px; position: relative; text-align: left;">
                <div class="form-logo-widget" style="position: relative; resize: both; overflow: hidden; width: 120px; height: 120px; min-width: 80px; min-height: 80px; max-width: 300px; max-height: 300px; border: 2px dashed #cbd5e1; border-radius: 12px; box-shadow: 0 0 15px rgba(56, 189, 248, 0.25); background: #f8fafc; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: move; flex-shrink: 0;">
                  <!-- Drag Handle -->
                  <div style="position: absolute; top: 6px; left: 6px; color: #94a3b8; background: rgba(255,255,255,0.7); border-radius: 4px; padding: 2px;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2L12 22M2 12L22 12M12 2L8 6M12 2L16 6M12 22L8 18M12 22L16 18M2 12L6 8M2 12L6 16M22 12L18 8M22 12L18 16"/></svg>
                  </div>
                  
                  <img v-if="generatedForm?.theme?.logo_url" :src="generatedForm.theme.logo_url" class="form-logo-image" style="width: 100%; height: 100%; object-fit: contain; padding: 12px;" />
                  
                  <div class="form-logo-placeholder" v-else style="display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 12px;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                    <span style="font-size: 10px; color: #64748b; text-align: center; font-weight: 600; line-height: 1.2;">Upload / Replace<br/>Logo</span>
                  </div>
                  
                  <div class="form-logo-overlay" @click="logoFileInput.click()" style="position: absolute; inset: 0; background: rgba(0,0,0,0.5); display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; cursor: pointer; color: white;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="margin-bottom: 4px;"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                  </div>
                </div>
                
                <input type="file" ref="logoFileInput" @change="handleLogoUpload" accept="image/*" hidden />
                
                <div class="form-title-section" style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
                  <input v-model="generatedForm.title" class="form-title-input" placeholder="Form Title" style="text-align: left; font-size: 28px; padding-left: 0;" />
                  <textarea v-model="generatedForm.description" class="form-description-input" placeholder="Form Description" style="text-align: left; min-height: 60px; padding-left: 0;"></textarea>
                </div>
              </header>'''

# Also add hover style for the new overlay
# Replace old logo overlay hover rule
new_hover = '''
.form-logo-widget:hover .form-logo-overlay {
  opacity: 1 !important;
}
'''
if '.form-logo-container:hover .form-logo-overlay' in text:
    text = text.replace('.form-logo-container:hover .form-logo-overlay {\n  opacity: 1;\n}', new_hover)

text = text.replace(old_header, new_header)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced form-header block successfully.")
