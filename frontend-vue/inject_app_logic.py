import os

filepath = r"e:\NewSystem\frontend-vue\src\App.vue"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Insert script variables and logic right before </script>
js_addition = """
const isFullscreen = ref(false)
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

// ==========================================
// 🛠 Core Logic: Fetch, Load, Delete Forms
// ==========================================
const fetchForms = async () => {
  loadingDirectory.value = true
  try {
    const res = await fetch('http://127.0.0.1:8000/api/v1/forms')
    const data = await res.json()
    if (data.status === 'success') {
      savedForms.value = data.forms
      totalFormsInDb.value = data.forms.length
      mongoDbStatus.value = 'connected'
    } else {
      mongoDbStatus.value = 'error'
    }
  } catch (err) {
    console.error('Fetch Forms Error:', err)
    mongoDbStatus.value = 'error'
  } finally {
    loadingDirectory.value = false
  }
}

const deleteSavedForm = async (id) => {
  if (!confirm('ยืนยันการลบฟอร์มนี้? ข้อมูล Response จะถูกลบไปด้วย')) return
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/v1/forms/${id}`, { method: 'DELETE' })
    if (res.ok) {
      await fetchForms()
      if (generatedForm.value && generatedForm.value.id === id) {
         generatedForm.value = null
      }
    } else {
      alert('ลบฟอร์มไม่สำเร็จ')
    }
  } catch (err) {
    console.error(err)
  }
}

const loadSavedForm = (form) => {
  generatedForm.value = JSON.parse(JSON.stringify(form))
  currentTab.value = 'create'
}

watch(currentTab, (newTab) => {
  if (newTab === 'directory' || newTab === 'dashboard') {
    fetchForms()
  }
})

onMounted(() => {
  fetchForms()
})

// ==========================================
// ✨ AI Quick Tweaker: Edit Form Logic
// ==========================================
const openEditModal = (sIdx, fIdx, field) => {
  editingField.value = { sIdx, fIdx }
  editModalLabel.value = field.label || ''
  editModalPlaceholder.value = field.placeholder || ''
  editModalType.value = field.type || 'text'
  editModalOptionsText.value = (field.options || []).join(', ')
  editModalRequired.value = field.required || false
  editModalWidth.value = field.width || 'full'
  editModalConditionField.value = field.condition_field || ''
  editModalConditionValue.value = field.condition_value || ''
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingField.value = null
}

const saveFieldEdit = () => {
  if (!editingField.value || !generatedForm.value) return
  const { sIdx, fIdx } = editingField.value
  const field = generatedForm.value.sections[sIdx].fields[fIdx]
  
  field.label = editModalLabel.value
  field.placeholder = editModalPlaceholder.value
  field.type = editModalType.value
  field.required = editModalRequired.value
  field.width = editModalWidth.value
  field.condition_field = editModalConditionField.value || null
  field.condition_value = editModalConditionValue.value || null
  
  if (['select', 'radio', 'checkbox'].includes(field.type)) {
    field.options = editModalOptionsText.value.split(',').map(s => s.trim()).filter(s => s)
  }
  closeEditModal()
}

const deleteField = () => {
  if (!editingField.value || !generatedForm.value) return
  if (!confirm('ยืนยันการลบ Field นี้?')) return
  const { sIdx, fIdx } = editingField.value
  generatedForm.value.sections[sIdx].fields.splice(fIdx, 1)
  closeEditModal()
}
"""

content = content.replace("</script>", js_addition + "\n</script>", 1)

# 2. Add Full screen toggle button
fs_btn = """              <div class="canvas-badge">
                <span>🎨</span> AI Canvas
              </div>
              <button class="btn-fullscreen-toggle" @click="toggleFullscreen" :title="isFullscreen ? 'Exit Full Screen' : 'Full Screen'">
                {{ isFullscreen ? '🗗' : '🖵' }}
              </button>"""
content = content.replace("""              <div class="canvas-badge">
                <span>🎨</span> AI Canvas
              </div>""", fs_btn)

# 3. Add fullscreen class binding
content = content.replace('<div class="preview-canvas-column">', '<div class="preview-canvas-column" :class="{ \'fullscreen-mode\': isFullscreen }">')

# 4. Add hover edit overlay
target_field = """<div v-for="(field, fIdx) in section.fields" :key="fIdx" class="field-item-box" :style="field.width === 'half' ? 'grid-column: span 1' : 'grid-column: span 2'">"""
edit_overlay = """<div v-for="(field, fIdx) in section.fields" :key="fIdx" class="field-item-box" :style="field.width === 'half' ? 'grid-column: span 1' : 'grid-column: span 2'">
                      <div class="field-actions-overlay" @click.stop="openEditModal(sIdx, fIdx, field)">
                        <span class="edit-icon">✏️ Edit Field</span>
                      </div>"""
content = content.replace(target_field, edit_overlay)

# 5. Replace directory placeholder
dir_placeholder = """        <div class="directory-empty-state">
           Form directory will be loaded here.
        </div>"""
dir_actual = """        <div v-if="loadingDirectory" class="directory-empty-state">
           Loading forms...
        </div>
        <div v-else-if="savedForms.length === 0" class="directory-empty-state">
           No forms saved yet.
        </div>
        <div v-else class="forms-grid-directory">
          <div v-for="form in savedForms" :key="form.id" class="directory-card animate-fade">
            <div class="directory-card-color-strip" :style="`background: ${form.theme_color || '#4f46e5'}`"></div>
            <div class="directory-card-body">
              <h3 class="directory-card-title">{{ form.title }}</h3>
              <p class="directory-card-desc">{{ form.description || 'No description' }}</p>
              <div class="directory-card-meta">
                <span class="meta-date">📅 {{ new Date(form.created_at).toLocaleDateString() }}</span>
              </div>
              <div class="directory-card-actions">
                <button class="btn-sm btn-load" @click="loadSavedForm(form)">Load & Edit</button>
                <button class="btn-sm btn-delete" @click="deleteSavedForm(form.id)">Delete</button>
              </div>
            </div>
          </div>
        </div>"""
content = content.replace(dir_placeholder, dir_actual)

# 6. Replace dashboard placeholder
dash_target = """      <div class="dashboard-view-container" v-show="currentTab === 'dashboard'">
        <div class="view-header">
          <h2 class="view-title">Dashboard</h2>
          <p class="view-sub">Analytics and responses.</p>
        </div>
      </div>"""
dash_actual = """      <div class="dashboard-view-container" v-show="currentTab === 'dashboard'">
        <div class="view-header">
          <h2 class="view-title">Dashboard</h2>
          <p class="view-sub">System Analytics & Overview</p>
        </div>
        <div class="dashboard-stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ totalFormsInDb }}</div>
            <div class="stat-label">Total Forms Generated</div>
          </div>
          <div class="stat-card">
            <div class="stat-value" :class="mongoDbStatus === 'connected' ? 'status-ok' : 'status-err'">
              {{ mongoDbStatus === 'connected' ? 'Connected' : 'Error' }}
            </div>
            <div class="stat-label">MongoDB Status</div>
          </div>
        </div>
      </div>"""
content = content.replace(dash_target, dash_actual)

# 7. Add Edit Modal before </template>
modal_html = """    <!-- AI Quick Tweaker Modal -->
    <div v-if="showEditModal" class="editor-modal-overlay animate-fade">
      <div class="editor-modal-card">
        <div class="modal-header">
          <h3>✨ AI Quick Tweaker</h3>
          <button class="btn-close-modal" @click="closeEditModal">×</button>
        </div>
        <div class="modal-body">
          <div class="modal-input-group">
            <label>Field Label</label>
            <input type="text" v-model="editModalLabel" class="field-input" />
          </div>
          <div class="modal-input-group">
            <label>Placeholder / Hint</label>
            <input type="text" v-model="editModalPlaceholder" class="field-input" />
          </div>
          
          <div class="modal-input-group-row">
            <div class="modal-input-group" style="flex:1">
              <label>Input Type</label>
              <select v-model="editModalType" class="field-input">
                <option value="text">Text (Short)</option>
                <option value="textarea">Textarea (Long)</option>
                <option value="number">Number</option>
                <option value="email">Email</option>
                <option value="date">Date</option>
                <option value="select">Dropdown (Select)</option>
                <option value="radio">Radio Options</option>
                <option value="checkbox">Checkbox Options</option>
                <option value="file">File Upload</option>
              </select>
            </div>
            <div class="modal-input-group" style="flex:1">
              <label>Width</label>
              <select v-model="editModalWidth" class="field-input">
                <option value="full">Full Width (100%)</option>
                <option value="half">Half Width (50%)</option>
              </select>
            </div>
          </div>

          <div v-if="['select', 'radio', 'checkbox'].includes(editModalType)" class="modal-input-group">
            <label>Options (comma separated)</label>
            <input type="text" v-model="editModalOptionsText" class="field-input" placeholder="e.g. Option A, Option B, Option C" />
          </div>

          <div class="modal-input-group-row" style="align-items: center; gap: 12px; margin-top: 12px;">
            <input type="checkbox" id="req-check" v-model="editModalRequired" style="width: 18px; height: 18px; cursor:pointer;" />
            <label for="req-check" style="cursor:pointer; font-weight: 600;">Required Field (*)</label>
          </div>
          
          <div class="modal-conditional-zone" style="margin-top: 16px; padding: 12px; background: #f8fafc; border-radius: 8px;">
            <label style="font-size: 0.85rem; font-weight: 600; color: #64748b; margin-bottom: 8px; display: block;">Conditional Logic (Show if)</label>
            <div class="modal-input-group-row">
              <input type="text" v-model="editModalConditionField" class="field-input" placeholder="Depends on Field Name" style="flex:1" />
              <input type="text" v-model="editModalConditionValue" class="field-input" placeholder="Equals Value" style="flex:1" />
            </div>
          </div>

        </div>
        <div class="modal-footer">
          <button class="btn-sm btn-delete" @click="deleteField">🗑️ Delete</button>
          <div style="flex:1"></div>
          <button class="btn-sm" style="background: var(--border-color); color: var(--text-color);" @click="closeEditModal">Cancel</button>
          <button class="btn-sm btn-load" @click="saveFieldEdit">💾 Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>"""
content = content.replace("  </div>\n</template>", modal_html)

# 8. Add extra CSS for fullscreen and button
css_addition = """
.btn-fullscreen-toggle {
  background: transparent;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 1rem;
  cursor: pointer;
  color: var(--text-color, #475569);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  margin-left: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-fullscreen-toggle:hover {
  background: #f1f5f9;
  transform: translateY(-1px);
}
.fullscreen-mode {
  position: fixed !important;
  inset: 0 !important;
  z-index: 9999 !important;
  width: 100vw !important;
  height: 100vh !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  background: var(--bg-color, #f8fafc);
  display: flex;
  flex-direction: column;
}
.fullscreen-mode .canvas-preview-wrapper {
  flex: 1;
  border-radius: 0;
  max-width: 100%;
}
.fullscreen-mode .form-card {
  max-width: 800px;
  margin: 0 auto;
}
"""

content = content.replace("</style>", css_addition + "\n</style>")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Logic and Full Screen features successfully injected.")
