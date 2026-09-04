# -*- coding: utf-8 -*-
"""Step 3: Main workspace + AI Creator floating input pill"""

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    vue = f.read()

# Main workspace - upgrade with glass
vue = vue.replace('<main class="workspace-container">', '<main class="workspace-container workspace-glass">')

# Chat column: needs relative + padding-bottom for floating pill
vue = vue.replace('<div class="unified-chat-column">', '<div class="unified-chat-column" style="position:relative; padding-bottom: 110px;">')

# chat feed: style softly 
vue = vue.replace('<div class="chat-display-feed custom-scrollbar">', '<div class="chat-display-feed custom-scrollbar glass-chat-feed">')

# Input cockpit: replace with floating pill
old_cockpit = '''          <div class="unified-input-cockpit">
            <div v-if="activeFunction && activeFunction.value !== 'text_prompt'" class="integrated-upload-tray">
              <input type="file" ref="fileInput" @change="handleFileChange" style="display: none;" />
              <div v-if="!selectedFile" class="mini-dropzone" @click=".fileInput.click()">
                <span class="mini-upload-icon">\U0001f4e4</span>
                <span class="mini-upload-text">Click to upload {{ activeFunction.hint }}</span>
              </div>
              <div v-else class="attached-file-badge">
                <span class="file-preview-icon">\U0001f4ce</span>
                <div class="file-meta-info">
                  <div class="file-name-string">{{ selectedFile.name }}</div>
                  <div class="file-size-string">{{ (selectedFile.size / 1024).toFixed(1) }} KB</div>
                </div>
                <button class="remove-file-action" @click="clearFile">\xd7</button>
              </div>
            </div>
            
            <textarea v-model="textPrompt" :disabled="loading" class="embedded-textarea custom-scrollbar" placeholder="Type your instruction here..." @keyup.ctrl.enter="sendCombinedCommand"></textarea>
            
            <div class="cockpit-footer-actions">
              <span class="keyboard-tip">Ctrl + Enter to send</span>
              <div style="display: flex; gap: 8px;">
                <input type="file" ref="chatFileInput" @change="handleChatFile" accept="image/*" hidden />
                <button class="btn-attach" @click="chatFileInput.click()" :disabled="loading" title="Attach Image">\U0001f4ce</button>
                <button class="submit-combined-btn" :disabled="loading" @click="sendCombinedCommand">
                  {{ loading ? 'Generating...' : 'Send' }}
                </button>
              </div>
            </div>
          </div>'''

new_cockpit = '''          <!-- File tray above pill -->
          <div v-if="activeFunction && activeFunction.value !== 'text_prompt'" style="position:absolute; bottom:90px; left:50%; transform:translateX(-50%); width:90%; max-width:720px; z-index:51;">
            <input type="file" ref="fileInput" @change="handleFileChange" style="display: none;" />
            <div v-if="!selectedFile" class="glass-upload-dropzone" @click=".fileInput.click()">
              <span>\U0001f4e4</span> Click to upload {{ activeFunction.hint }}
            </div>
            <div v-else class="glass-file-badge">
              <div style="display:flex;align-items:center;gap:10px;">
                <span>\U0001f4ce</span>
                <div>
                  <div style="font-size:13px;font-weight:600;color:#0f172a;">{{ selectedFile.name }}</div>
                  <div style="font-size:11px;color:#94a3b8;">{{ (selectedFile.size / 1024).toFixed(1) }} KB</div>
                </div>
              </div>
              <button class="remove-file-action" @click="clearFile">&times;</button>
            </div>
          </div>

          <!-- Floating Pill Input -->
          <div class="aurora-input-pill" style="position:absolute; bottom:16px; left:50%; transform:translateX(-50%); width:90%; max-width:720px; z-index:50;">
            <input type="file" ref="chatFileInput" @change="handleChatFile" accept="image/*" hidden />
            <button class="pill-attach-btn" @click="chatFileInput.click()" :disabled="loading" title="Attach Image">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
            </button>
            <textarea v-model="textPrompt" :disabled="loading" class="pill-textarea" rows="1" placeholder="Ask AI to design or modify the form..." @keyup.ctrl.enter="sendCombinedCommand"></textarea>
            <div class="pill-hint">Ctrl+Enter</div>
            <button class="pill-send-btn" :disabled="loading" @click="sendCombinedCommand">
              <span v-if="!loading">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M22 2 11 13M22 2 15 22 11 13 2 9l20-7z"/></svg>
              </span>
              <span v-else style="display:flex;align-items:center;gap:4px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation:spin 1s linear infinite;"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
              </span>
            </button>
          </div>'''

if old_cockpit in vue:
    vue = vue.replace(old_cockpit, new_cockpit)
    print("Cockpit replaced.")
else:
    print("WARNING: Could not find cockpit to replace. Looking for partial match...")
    if 'unified-input-cockpit' in vue:
        print("unified-input-cockpit found but string doesn't match exactly")
    else:
        print("unified-input-cockpit not found at all")

# Update function-items to glass pill style
vue = vue.replace(
    '<div class="function-item" v-for="type in inputTypes" :key="type.value" :class="{ active: selectedInputType === type.value }" @click="selectFunction(type.value)">',
    '<div class="glass-method-item" v-for="type in inputTypes" :key="type.value" :class="{ \'active\': selectedInputType === type.value }" @click="selectFunction(type.value)">'
)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(vue)

print("Step 3 done: Workspace + floating pill + method items.")
