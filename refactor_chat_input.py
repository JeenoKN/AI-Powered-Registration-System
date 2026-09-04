import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace unified-input-cockpit block
cockpit_pattern = r'<div class="unified-input-cockpit">.*?</div>\s*</div>\s*</div>'
# Wait, parsing HTML with regex can be tricky. Let's use string replacement based on exact chunks.

old_cockpit = """          <div class="unified-input-cockpit">
            <div v-if="activeFunction && activeFunction.value !== 'text_prompt'" class="integrated-upload-tray">
              <input type="file" ref="fileInput" @change="handleFileChange" style="display: none;" />
              <div v-if="!selectedFile" class="mini-dropzone" @click=".fileInput.click()">
                <span class="mini-upload-icon">??</span>
                <span class="mini-upload-text">Click to upload {{ activeFunction.hint }}</span>
              </div>
              <div v-else class="attached-file-badge">
                <span class="file-preview-icon">??</span>
                <div class="file-meta-info">
                  <div class="file-name-string">{{ selectedFile.name }}</div>
                  <div class="file-size-string">{{ (selectedFile.size / 1024).toFixed(1) }} KB</div>
                </div>
                <button class="btn-premium-danger" @click="clearFile">×</button>
              </div>
            </div>
            
            <textarea v-model="textPrompt" :disabled="loading" class="embedded-textarea custom-scrollbar" placeholder="Type your instruction here..." @keyup.ctrl.enter="sendCombinedCommand"></textarea>
            
            <div class="cockpit-footer-actions">
              <span class="keyboard-tip">Ctrl + Enter to send</span>
              <div style="display: flex; gap: 8px;">
                <input type="file" ref="chatFileInput" @change="handleChatFile" accept="image/*" hidden />
                <button class="btn-premium-ghost" @click="chatFileInput.click()" :disabled="loading" title="Attach Image">??</button>
                <button class="btn-premium-coral" :disabled="loading" @click="sendCombinedCommand">
                  {{ loading ? 'Generating...' : 'Send' }}
                </button>
              </div>
            </div>
          </div>"""

new_cockpit = """          
          <!-- Floating Input Bar -->
          <div class="absolute bottom-8 left-1/2 -translate-x-1/2 w-[90%] max-w-2xl bg-white/80 backdrop-blur-xl rounded-full shadow-[0_8px_30px_rgb(0,0,0,0.12)] border border-white/60 p-2 flex items-center gap-3 z-50">
            
            <!-- File Upload Tray (Absolute above pill if active) -->
            <div v-if="activeFunction && activeFunction.value !== 'text_prompt'" class="absolute bottom-full mb-4 left-0 w-full">
              <input type="file" ref="fileInput" @change="handleFileChange" style="display: none;" />
              <div v-if="!selectedFile" class="bg-white/90 backdrop-blur-md rounded-2xl p-3 border border-indigo-100 shadow-lg cursor-pointer hover:bg-indigo-50 transition-colors flex items-center justify-center gap-2 text-sm text-indigo-700 font-medium" @click=".fileInput.click()">
                <span>??</span> Click to upload {{ activeFunction.hint }}
              </div>
              <div v-else class="bg-white/90 backdrop-blur-md rounded-2xl p-3 border border-green-100 shadow-lg flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <span>??</span>
                  <div>
                    <div class="text-sm font-semibold text-gray-800">{{ selectedFile.name }}</div>
                    <div class="text-xs text-gray-500">{{ (selectedFile.size / 1024).toFixed(1) }} KB</div>
                  </div>
                </div>
                <button class="bg-red-50 text-red-500 hover:bg-red-100 rounded-full w-8 h-8 flex items-center justify-center transition-colors" @click="clearFile">×</button>
              </div>
            </div>
            
            <!-- Hidden file input for chat image -->
            <input type="file" ref="chatFileInput" @change="handleChatFile" accept="image/*" hidden />
            
            <!-- Attach Button -->
            <button class="w-10 h-10 flex-shrink-0 rounded-full hover:bg-gray-100 text-gray-500 flex items-center justify-center transition-colors ml-1" @click="chatFileInput.click()" :disabled="loading" title="Attach Image">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
            </button>
            
            <!-- Text Input -->
            <textarea v-model="textPrompt" :disabled="loading" class="flex-1 bg-transparent border-none outline-none resize-none py-3 text-gray-700 placeholder-gray-400 font-medium text-[15px]" rows="1" placeholder="Ask AI to design or modify the form..." @keyup.ctrl.enter="sendCombinedCommand"></textarea>
            
            <!-- Send Button -->
            <button class="flex-shrink-0 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full px-6 py-2.5 font-semibold transition-all shadow-md flex items-center gap-2 mr-1" :disabled="loading" @click="sendCombinedCommand">
              <span>{{ loading ? 'Working...' : 'Send' }}</span>
              <svg v-if="!loading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </button>
          </div>"""

if old_cockpit in text:
    text = text.replace(old_cockpit, new_cockpit)
    
    # We must also ensure unified-chat-column has relative positioning
    text = text.replace('<div class="unified-chat-column">', '<div class="unified-chat-column relative">')
    
    with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Cockpit refactored.")
else:
    print("Could not find old cockpit to replace.")

