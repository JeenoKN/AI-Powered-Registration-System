import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    vue = f.read()

# 1. App Shell
vue = vue.replace('<div class="app-shell-layout max-w-screen-2xl mx-auto my-[2vh] h-[96vh] rounded-[32px] shadow-2xl shadow-black/10 overflow-hidden bg-white/40 border border-white/20">', '<div class="app-shell-layout">')

# 2. Sidebar
vue = vue.replace('<aside class="sidebar-nav bg-gradient-to-b from-[#3a3a3a]/90 to-[#2a2a2a]/95 backdrop-blur-xl border-r border-white/10 text-white/90">', '<aside class="sidebar-nav">')

# 3. nav-item
vue = vue.replace('class="nav-item hover:bg-white/10 rounded-xl hover:scale-105 transition-all duration-300"', 'class="nav-item"')

# 4. workspace-grid
vue = vue.replace('<div class="workspace-grid h-full w-full bg-[#F9F8F6] rounded-r-[32px] overflow-hidden" v-show="currentTab === \'create\'">', '<div class="workspace-grid" v-show="currentTab === \'create\'">')

# 5. function-item
vue = vue.replace('<div class="function-item bg-white rounded-2xl shadow-sm border border-gray-100 text-gray-700 hover:-translate-y-1 hover:shadow-md hover:shadow-indigo-500/10 transition-all duration-300 cursor-pointer p-4 flex items-center gap-3"', '<div class="function-item"')

# 6. unified-chat-column
vue = vue.replace('<div class="unified-chat-column relative">', '<div class="unified-chat-column">')

# 7. cockpit (I have to replace the whole block)
floating_bar = '''          <!-- Floating Input Bar -->
          <div class="absolute bottom-8 left-1/2 -translate-x-1/2 w-[90%] max-w-2xl bg-white/80 backdrop-blur-xl rounded-full shadow-[0_8px_30px_rgb(0,0,0,0.12)] border border-white/60 p-2 flex items-center gap-3 z-50">
            
            <!-- File Upload Tray (Absolute above pill if active) -->
            <div v-if="activeFunction && activeFunction.value !== 'text_prompt'" class="absolute bottom-full mb-4 left-0 w-full">
              <input type="file" ref="fileInput" @change="handleFileChange" style="display: none;" />
              <div v-if="!selectedFile" class="bg-white/90 backdrop-blur-md rounded-2xl p-3 border border-indigo-100 shadow-lg cursor-pointer hover:bg-indigo-50 transition-colors flex items-center justify-center gap-2 text-sm text-indigo-700 font-medium" @click=".fileInput.click()">
                <span>&#x1F4E4;</span> Click to upload {{ activeFunction.hint }}
              </div>
              <div v-else class="bg-white/90 backdrop-blur-md rounded-2xl p-3 border border-green-100 shadow-lg flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <span>&#x1F4CE;</span>
                  <div>
                    <div class="text-sm font-semibold text-gray-800">{{ selectedFile.name }}</div>
                    <div class="text-xs text-gray-500">{{ (selectedFile.size / 1024).toFixed(1) }} KB</div>
                  </div>
                </div>
                <button class="bg-red-50 text-red-500 hover:bg-red-100 rounded-full w-8 h-8 flex items-center justify-center transition-colors" @click="clearFile">&times;</button>
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
          </div>'''

old_cockpit = '''          <div class="unified-input-cockpit">
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
          </div>'''

vue = vue.replace(floating_bar, old_cockpit)

# 8. canvas-header-panel
vue = vue.replace('<div class="canvas-header-panel bg-white/60 backdrop-blur-lg rounded-3xl shadow-sm border border-white/80 p-5 mb-4">', '<div class="canvas-header-panel">')

# 9. theme-prompt-box
vue = vue.replace('<div class="theme-prompt-box mt-4 border-t border-gray-100 pt-4">', '<div class="theme-prompt-box">')
vue = vue.replace('<div class="theme-prompt-row flex gap-2">', '<div class="theme-prompt-row">')

# 11, 12. theme input
vue = vue.replace('<input type="text" v-model="themePrompt" class="flex-1 bg-white/50 border border-white/60 rounded-xl px-4 py-2 text-gray-700 outline-none focus:bg-white focus:ring-2 focus:ring-indigo-100 transition-all" placeholder="e.g. Cyberpunk, Minimalist Light, Ocean Blue" @keyup.enter="requestAiTheme" />', '<input type="text" v-model="themePrompt" class="theme-prompt-input" placeholder="e.g. Cyberpunk, Minimalist Light, Ocean Blue" @keyup.enter="requestAiTheme" />')
vue = vue.replace('<button class="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-xl shadow-md font-medium transition-all" :disabled="themeLoading || !generatedForm" @click="requestAiTheme">', '<button class="btn-theme-generate" :disabled="themeLoading || !generatedForm" @click="requestAiTheme">')

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(vue)

print("Restored AdminView.vue")
