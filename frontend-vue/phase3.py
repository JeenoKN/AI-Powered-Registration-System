import os

filepath = r"e:\NewSystem\frontend-vue\src\App.vue"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Inject functions
new_functions = """const formatDate = (dateString) => {
  if (!dateString) return '';
  const d = new Date(dateString);
  const datePart = d.toLocaleDateString('en-US');
  const timePart = d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }).replace(':', '.');
  return `ทำเมื่อวัน ${datePart} เวลา ${timePart}`;
}

const addFieldAfterInline = (sIdx, fIdx) => {
  if (!generatedForm.value) return;
  const newField = {
    name: "new_field_" + Date.now(),
    label: "New Field",
    type: "text",
    placeholder: "Enter value",
    required: false,
    width: "full"
  };
  generatedForm.value.sections[sIdx].fields.splice(fIdx + 1, 0, newField);
}

const deleteFieldInline = (sIdx, fIdx) => {
  if (!generatedForm.value) return;
  if (!confirm('ยืนยันการลบ Field นี้?')) return;
  generatedForm.value.sections[sIdx].fields.splice(fIdx, 1);
}

const deleteField = () => {"""

content = content.replace("const deleteField = () => {", new_functions)

# 2. Update format date in Directory HTML
old_date_html = """<span class="meta-date">📅 {{ new Date(form.created_at).toLocaleDateString() }}</span>"""
new_date_html = """<span class="meta-date">📅 {{ formatDate(form.created_at) }}</span>"""
content = content.replace(old_date_html, new_date_html)

# 3. Update the Field Actions Overlay in the template
old_field_actions = """                      <div class="field-actions-overlay" @click.stop="openEditModal(sIdx, fIdx, field)">
                        <span class="edit-icon">✏️ Edit Field</span>
                      </div>"""

new_field_actions = """                      <div class="field-actions-overlay">
                        <div class="field-toolbar">
                          <button class="toolbar-btn btn-edit" @click.stop="openEditModal(sIdx, fIdx, field)" title="Edit Field">
                            <span class="icon">✏️</span> <span class="lbl">แก้ไข</span>
                          </button>
                          <button class="toolbar-btn btn-add" @click.stop="addFieldAfterInline(sIdx, fIdx)" title="Add Field Below">
                            <span class="icon">➕</span> <span class="lbl">เพิ่มฟิลด์</span>
                          </button>
                          <button class="toolbar-btn btn-delete-inline" @click.stop="deleteFieldInline(sIdx, fIdx)" title="Delete Field">
                            <span class="icon">🗑️</span> <span class="lbl">ลบ</span>
                          </button>
                        </div>
                      </div>"""
content = content.replace(old_field_actions, new_field_actions)

# 4. Add the CSS for the new toolbar
css_addition = """
.field-toolbar {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  gap: 4px;
}
.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  font-family: 'Poppins', 'Plus Jakarta Sans', sans-serif;
  font-weight: 600;
  color: var(--text-color, #475569);
  transition: all 0.2s ease;
}
.toolbar-btn:hover {
  background: #f1f5f9;
}
.toolbar-btn.btn-edit:hover {
  color: #3b82f6;
  background: #eff6ff;
}
.toolbar-btn.btn-add:hover {
  color: #10b981;
  background: #ecfdf5;
}
.toolbar-btn.btn-delete-inline:hover {
  color: #ef4444;
  background: #fef2f2;
}
</style>"""

content = content.replace("</style>", css_addition)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Phase 3 applied successfully.")
