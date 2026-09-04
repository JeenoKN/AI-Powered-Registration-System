import os

filepath = r"e:\NewSystem\frontend-vue\src\App.vue"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add JS functions
add_field_funcs = """
const addFieldBefore = () => {
  if (!editingField.value || !generatedForm.value) return
  const { sIdx, fIdx } = editingField.value
  const newField = {
    name: "new_field_" + Date.now(),
    label: "New Field",
    type: "text",
    placeholder: "Enter value",
    required: false,
    width: "full"
  }
  generatedForm.value.sections[sIdx].fields.splice(fIdx, 0, newField)
  closeEditModal()
}

const addFieldAfter = () => {
  if (!editingField.value || !generatedForm.value) return
  const { sIdx, fIdx } = editingField.value
  const newField = {
    name: "new_field_" + Date.now(),
    label: "New Field",
    type: "text",
    placeholder: "Enter value",
    required: false,
    width: "full"
  }
  generatedForm.value.sections[sIdx].fields.splice(fIdx + 1, 0, newField)
  closeEditModal()
}

const deleteField = () => {"""

content = content.replace("const deleteField = () => {", add_field_funcs)

# 2. Add emojis to select options
old_options = """                <option value="text">Text (Short)</option>
                <option value="textarea">Textarea (Long)</option>
                <option value="number">Number</option>
                <option value="email">Email</option>
                <option value="date">Date</option>
                <option value="select">Dropdown (Select)</option>
                <option value="radio">Radio Options</option>
                <option value="checkbox">Checkbox Options</option>
                <option value="file">File Upload</option>"""

new_options = """                <option value="text">🔠 Text (Short)</option>
                <option value="textarea">📝 Textarea (Long)</option>
                <option value="number">🔢 Number</option>
                <option value="email">📧 Email</option>
                <option value="date">📅 Date</option>
                <option value="select">🔽 Dropdown (Select)</option>
                <option value="radio">🔘 Radio Options</option>
                <option value="checkbox">☑️ Checkbox Options</option>
                <option value="file">📎 File Upload</option>"""

content = content.replace(old_options, new_options)

# 3. Update Modal Footer
old_footer = """        <div class="modal-footer">
          <button class="btn-sm btn-delete" @click="deleteField">🗑️ Delete</button>
          <div style="flex:1"></div>
          <button class="btn-sm" style="background: var(--border-color); color: var(--text-color);" @click="closeEditModal">Cancel</button>
          <button class="btn-sm btn-load" @click="saveFieldEdit">💾 Save Changes</button>
        </div>"""

new_footer = """        <div class="modal-footer" style="flex-wrap: wrap; gap: 8px;">
          <button class="btn-sm btn-delete-danger" @click="deleteField">🗑️ Delete</button>
          <div style="flex:1"></div>
          <button class="btn-sm btn-insert" @click="addFieldBefore">⬆️ Add Before</button>
          <button class="btn-sm btn-insert" @click="addFieldAfter">⬇️ Add After</button>
          <button class="btn-sm" style="background: var(--border-color, #e2e8f0); color: var(--text-color, #0f172a);" @click="closeEditModal">Cancel</button>
          <button class="btn-sm btn-load" @click="saveFieldEdit">💾 Save Changes</button>
        </div>"""

content = content.replace(old_footer, new_footer)

# 4. Add CSS for Glassmorphism and new buttons
old_css_overlay = ".editor-modal-overlay {\n"
new_css_overlay = """.editor-modal-overlay {
  background: rgba(15, 23, 42, 0.45) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;\n"""
content = content.replace(old_css_overlay, new_css_overlay)

css_additions = """
.btn-delete-danger {
  background: #fef2f2 !important;
  color: #ef4444 !important;
  border: 1px solid #fca5a5 !important;
}
.btn-delete-danger:hover {
  background: #fee2e2 !important;
  transform: translateY(-1px);
}
.btn-insert {
  background: #f0fdf4 !important;
  color: #16a34a !important;
  border: 1px solid #bbf7d0 !important;
}
.btn-insert:hover {
  background: #dcfce7 !important;
  transform: translateY(-1px);
}
.editor-modal-card label {
  font-family: 'Poppins', 'Plus Jakarta Sans', sans-serif;
  font-weight: 600 !important;
  color: #334155;
}
.modal-conditional-zone label {
  font-weight: 500 !important;
  color: #64748b;
}
</style>
"""

content = content.replace("</style>", css_additions)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Phase 1.5 successfully applied.")
