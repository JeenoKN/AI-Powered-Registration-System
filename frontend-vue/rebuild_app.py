import os
import re

app_path = "e:/NewSystem/frontend-vue/src/App.vue"
with open(app_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# find where exportVueComponent starts adding templateContent
js_part = "".join(lines[:504])

# Construct the remaining JS
remaining_js = """`
  let styleContent = `<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Plus Jakarta Sans', 'Inter', system-ui, -apple-system, sans-serif;
}
.form-container { padding: 40px 20px; background: var(--bg-color, #f8fafc); min-height: 100vh; display: flex; justify-content: center; }
.form-card { width: 100%; max-width: 680px; background: var(--card-bg, #ffffff); border-radius: var(--border-radius, 20px); padding: 36px; box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.06); border: 1px solid var(--border-color, #e2e8f0); }
.form-header { margin-bottom: 28px; text-align: center; }
.form-title { font-size: 1.75rem; font-weight: 800; color: var(--text-color, #0f172a); margin-bottom: 8px; }
.form-description { font-size: 0.95rem; color: var(--text-color, #64748b); opacity: 0.85; line-height: 1.6; }
.form-element { display: flex; flex-direction: column; gap: 24px; }
.form-section { border: 1px solid var(--border-color, #e2e8f0); border-radius: var(--border-radius, 16px); padding: 24px; background-color: var(--card-bg, #ffffff); margin-bottom: 16px; }
.section-legend { font-weight: 700; color: var(--theme-color, #4f46e5); font-size: 1.15rem; padding: 0 8px; margin-bottom: 8px; }
.section-desc { font-size: 0.9rem; color: var(--text-color, #64748b); opacity: 0.8; margin-bottom: 16px; padding: 0 8px; }
.fields-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.field-group { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 0.9rem; font-weight: 600; color: var(--label-color, #475569); display: flex; align-items: center; }
.required-star { color: #ef4444; margin-left: 2px; }
.field-input { width: 100%; padding: 10px 14px; border: 1.5px solid var(--border-color, #cbd5e1); border-radius: var(--border-radius, 10px); font-size: 0.95rem; color: var(--input-text, #334155); background-color: var(--input-bg, #f8fafc); outline: none; }
.textarea-input { min-height: 100px; resize: vertical; }
.checkbox-group, .radio-group { display: flex; flex-wrap: wrap; gap: 16px; padding: 8px 0; }
.checkbox-option-label, .radio-option-label { display: flex; align-items: center; gap: 8px; font-size: 0.95rem; color: var(--text-color, #475569); cursor: pointer; }
.form-actions { margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border-color, #e2e8f0); text-align: center; }
.submit-btn { padding: 12px 28px; background: var(--theme-color, #4f46e5); color: #ffffff; border: none; border-radius: 12px; font-weight: 700; font-size: 1rem; cursor: pointer; transition: all 0.2s; }
.submit-btn:hover { filter: brightness(1.1); transform: translateY(-2px); }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>`

  const blob = new Blob([scriptContent, '\\n', templateContent, '\\n', styleContent], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `Form_${Date.now()}.vue`
  a.click()
  URL.revokeObjectURL(url)
}

// 🎨 AI Theme Engine Call
const requestAiTheme = async () => {
  if (!themePrompt.value.trim() || !generatedForm.value) return;
  themeLoading.value = true;
  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/ai/theme', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: themePrompt.value })
    });
    
    if (!response.ok) {
      if (response.status === 429) {
        throw new Error("QUOTA_EXCEEDED");
      }
      const errText = await response.text().catch(() => '');
      if (errText.includes("QUOTA_EXCEEDED")) {
        throw new Error("QUOTA_EXCEEDED");
      }
      throw new Error(`Server Error: ${response.status}`);
    }
    const data = await response.json();
    if (data.theme) {
      activeTheme.value = data.theme;
      if (!generatedForm.value.theme) {
        generatedForm.value.theme = {};
      }
      Object.assign(generatedForm.value.theme, data.theme);
      if (data.theme.theme_color) {
        generatedForm.value.theme_color = data.theme.theme_color;
      }
    }
  } catch (error) {
    console.error("Theme Error:", error);
    if (error.message === "QUOTA_EXCEEDED" || error.message.includes("QUOTA_EXCEEDED")) {
      chatMessages.value.push({ 
        sender: 'ai', 
        text: 'ขออภัยครับ โควตาการใช้งาน AI ของระบบเต็มชั่วคราว (Token Exhausted) รบกวนรอสักครู่แล้วลองใหม่อีกครั้งครับ 🙏' 
      });
    } else {
      alert("Error generating theme: " + error.message);
    }
  } finally {
    themeLoading.value = false;
  }
};
</script>
"""

template = """
<template>
  <div class="app-layout">
    <aside class="sidebar-nav">
      <div class="brand-zone">
        <div class="brand-logo ai-glow">✨</div>
        <div>
          <h2 class="brand-title gradient-text">Dynamic Form</h2>
          <div class="brand-sub">AI Generator</div>
        </div>
      </div>
      <div class="menu-label">MENU</div>
      <nav class="nav-links">
        <a href="#" class="nav-item" :class="{ active: currentTab === 'create' }" @click.prevent="currentTab = 'create'">
          <span class="nav-icon">✨</span> Create Form
        </a>
        <a href="#" class="nav-item" :class="{ active: currentTab === 'directory' }" @click.prevent="currentTab = 'directory'">
          <span class="nav-icon">📁</span> Directory
        </a>
        <a href="#" class="nav-item" :class="{ active: currentTab === 'dashboard' }" @click.prevent="currentTab = 'dashboard'">
          <span class="nav-icon">📊</span> Dashboard
        </a>
      </nav>
      <div class="sidebar-footer">
        <div class="user-profile">
          <img class="user-avatar" src="https://ui-avatars.com/api/?name=Admin&background=0D8ABC&color=fff" />
          <div>
            <div class="user-name">Admin User</div>
            <div class="user-email">admin@example.com</div>
          </div>
        </div>
      </div>
    </aside>

    <main class="workspace-container">
      <header class="global-header">
        <div class="breadcrumb">
          <span class="path-parent">Workspace</span> / 
          <span class="path-current">{{ currentTab === 'create' ? 'Create Form' : (currentTab === 'directory' ? 'Form Directory' : 'Dashboard') }}</span>
        </div>
      </header>
      
      <div class="workspace-grid" v-show="currentTab === 'create'">
        <div class="functions-menu-column custom-scrollbar">
          <div class="column-header">
            <div class="column-header-title">Input Methods</div>
            <div class="column-header-sub">Choose how to generate</div>
          </div>
          <div class="functions-list">
            <div class="function-item" v-for="type in inputTypes" :key="type.value" :class="{ active: selectedInputType === type.value }" @click="selectFunction(type.value)">
              <span class="func-icon">{{ type.icon }}</span>
              <span class="func-label">{{ type.label }}</span>
            </div>
          </div>
        </div>

        <div class="unified-chat-column">
          <div class="active-mode-banner">
            <div class="pulse-indicator"></div>
            <div class="mode-text">Active: <b>{{ activeFunction?.label }}</b></div>
          </div>
          
          <div class="chat-display-feed custom-scrollbar">
            <div v-for="(msg, i) in chatMessages" :key="i" class="message-bubble-row" :class="msg.sender">
              <div class="sender-avatar">{{ msg.sender === 'ai' ? '🤖' : '👤' }}</div>
              <div class="message-content-wrapper">
                <div v-if="msg.fileName || msg.functionLabel" class="message-attachment-meta">
                  <span v-if="msg.functionLabel" class="meta-tag function-tag">{{ msg.functionLabel }}</span>
                  <span v-if="msg.fileName" class="meta-tag file-tag">{{ msg.fileName }}</span>
                </div>
                <div class="message-text-body">{{ msg.text }}</div>
              </div>
            </div>
            <div v-if="loading" class="message-bubble-row ai">
              <div class="sender-avatar sparkle-icon">✨</div>
              <div class="message-content-wrapper">
                <div class="message-text-body thinking-state">กำลังประมวลผล...</div>
              </div>
            </div>
          </div>

          <div class="unified-input-cockpit">
            <div v-if="activeFunction && activeFunction.value !== 'text_prompt'" class="integrated-upload-tray">
              <input type="file" ref="fileInput" @change="handleFileChange" style="display: none;" />
              <div v-if="!selectedFile" class="mini-dropzone" @click="$refs.fileInput.click()">
                <span class="mini-upload-icon">📤</span>
                <span class="mini-upload-text">Click to upload {{ activeFunction.hint }}</span>
              </div>
              <div v-else class="attached-file-badge">
                <span class="file-preview-icon">📎</span>
                <div class="file-meta-info">
                  <div class="file-name-string">{{ selectedFile.name }}</div>
                  <div class="file-size-string">{{ (selectedFile.size / 1024).toFixed(1) }} KB</div>
                </div>
                <button class="remove-file-action" @click="clearFile">×</button>
              </div>
            </div>
            
            <textarea v-model="textPrompt" class="embedded-textarea custom-scrollbar" placeholder="Type your instruction here..." @keyup.ctrl.enter="sendCombinedCommand"></textarea>
            
            <div class="cockpit-footer-actions">
              <span class="keyboard-tip">Ctrl + Enter to send</span>
              <button class="submit-combined-btn" :disabled="loading" @click="sendCombinedCommand">
                {{ loading ? 'Generating...' : 'Send' }}
              </button>
            </div>
          </div>
        </div>

        <div class="preview-canvas-column">
          <div class="canvas-header-panel">
            <div class="canvas-badge-row">
              <div class="canvas-badge">
                <span>🎨</span> AI Canvas
              </div>
              <button class="btn-export-vue" :disabled="!generatedForm" @click="exportVueComponent()">Export .vue</button>
            </div>
            <div class="theme-prompt-box">
              <div class="theme-prompt-row">
                <input type="text" v-model="themePrompt" class="theme-prompt-input" placeholder="e.g. Cyberpunk, Minimalist Light, Ocean Blue" @keyup.enter="requestAiTheme" />
                <button class="btn-theme-generate" :disabled="themeLoading || !generatedForm" @click="requestAiTheme">
                  {{ themeLoading ? 'Styling...' : '✨ Style' }}
                </button>
              </div>
            </div>
          </div>

          <div class="canvas-preview-wrapper custom-scrollbar" :style="generatedForm?.theme?.bg_color ? `background-color: ${generatedForm.theme.bg_color}` : ''">
            <div v-if="!generatedForm" class="empty-canvas-state">
              <div class="empty-icon-box">📝</div>
              <h3 class="empty-title">No Form Generated</h3>
              <p class="empty-sub">Send a prompt or upload a file to generate a form schema.</p>
            </div>
            
            <div v-else class="form-card animate-fade" :style="`--bg-color: ${generatedForm?.theme?.bg_color || '#f8fafc'}; --card-bg: ${generatedForm?.theme?.card_bg || '#ffffff'}; --text-color: ${generatedForm?.theme?.text_color || '#0f172a'}; --theme-color: ${generatedForm?.theme_color || '#4f46e5'}; --border-color: ${generatedForm?.theme?.border_color || '#e2e8f0'}; --border-radius: ${generatedForm?.theme?.border_radius || '20px'}; --input-bg: ${generatedForm?.theme?.input_bg || '#f8fafc'}; --input-text: ${generatedForm?.theme?.input_text || '#334155'}; --label-color: ${generatedForm?.theme?.label_color || '#475569'}`">
              <header class="form-header">
                <h1 class="form-title">{{ generatedForm.title }}</h1>
                <p class="form-description">{{ generatedForm.description }}</p>
              </header>
              <div class="form-element">
                <fieldset v-for="(section, sIdx) in generatedForm.sections" :key="sIdx" class="form-section">
                  <legend class="section-legend">{{ section.title }}</legend>
                  <p v-if="section.description" class="section-desc">{{ section.description }}</p>
                  <div class="fields-grid">
                    <div v-for="(field, fIdx) in section.fields" :key="fIdx" class="field-item-box" :style="field.width === 'half' ? 'grid-column: span 1' : 'grid-column: span 2'">
                      <label class="field-label">{{ field.label }}<span v-if="field.required" class="required-star">*</span></label>
                      <input v-if="!['select', 'textarea', 'checkbox', 'radio'].includes(field.type)" :type="field.type || 'text'" class="field-input" :placeholder="field.placeholder" disabled />
                      <textarea v-else-if="field.type === 'textarea'" class="field-input textarea-input" :placeholder="field.placeholder" disabled></textarea>
                      <select v-else-if="field.type === 'select'" class="field-input" disabled>
                        <option>{{ field.placeholder || 'Select...' }}</option>
                      </select>
                      <div v-else-if="['checkbox', 'radio'].includes(field.type)" class="checkbox-group">
                        <label v-for="opt in field.options" :key="opt" class="checkbox-option-label">
                          <input :type="field.type" disabled /> {{ opt }}
                        </label>
                      </div>
                    </div>
                  </div>
                </fieldset>
              </div>
            </div>
          </div>

          <div class="canvas-action-footer">
            <div class="form-action-buttons-row">
              <button class="btn-clear-form" :disabled="!generatedForm" @click="clearFormResponses">Clear Form</button>
              <button class="btn-deploy-form" :disabled="!generatedForm || deploying" @click="deployForm">
                {{ deploying ? 'Deploying...' : 'Deploy to MongoDB' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="directory-view-container" v-show="currentTab === 'directory'">
        <div class="view-header">
          <h2 class="view-title">Form Directory</h2>
          <p class="view-sub">Manage your generated forms.</p>
        </div>
        <div class="directory-empty-state">
           Form directory will be loaded here.
        </div>
      </div>
      
      <div class="dashboard-view-container" v-show="currentTab === 'dashboard'">
        <div class="view-header">
          <h2 class="view-title">Dashboard</h2>
          <p class="view-sub">Analytics and responses.</p>
        </div>
      </div>
    </main>
  </div>
</template>
"""

new_css = "".join(lines[506:])
if not new_css.startswith("<style"):
    new_css = "<style scoped>\\n" + new_css

with open(app_path, "w", encoding="utf-8") as f:
    f.write(js_part)
    f.write(remaining_js)
    f.write(template)
    f.write("\\n")
    f.write(new_css)

print("App.vue rebuilt successfully.")
