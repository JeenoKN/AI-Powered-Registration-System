import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# ----------------------------
# Item 3: Button Consolidation
# ----------------------------
# Replace submit combined button
text = re.sub(
    r'class="submit-combined-btn"',
    r'class="btn-premium-primary"',
    text
)
text = re.sub(
    r'\.submit-combined-btn\s*\{[^}]+\}',
    r'',
    text
)

# Replace attach image button (icon)
text = re.sub(
    r'class="btn-attach"',
    r'class="btn-premium-ghost"',
    text
)
text = re.sub(
    r'\.btn-attach\s*\{[^}]+\}',
    r'',
    text
)

# Replace undo/redo/clear chat styles
text = re.sub(r'style="background: none; border: 1px solid #e2e8f0; color: #64748b; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; cursor: pointer; display: flex; align-items: center; gap: 4px;"', r'class="btn-premium-ghost"', text)

# Export and share buttons
text = re.sub(r'class="btn-export-vue"', r'class="btn-premium-secondary"', text)
text = re.sub(r'class="btn-share"', r'class="btn-premium-secondary"', text)
text = re.sub(r'\.btn-export-vue\s*\{[^}]+\}', r'', text)
text = re.sub(r'\.btn-share\s*\{[^}]+\}', r'', text)

# Delete / Remove buttons
text = re.sub(r'class="dir-btn-delete"', r'class="btn-premium-danger"', text)
text = re.sub(r'class="remove-file-action"', r'class="btn-premium-danger"', text)
text = re.sub(r'\.dir-btn-delete\s*\{[^}]+\}', r'', text)
text = re.sub(r'\.remove-file-action\s*\{[^}]+\}', r'', text)

# Load template/form details button
text = re.sub(r'class="dir-btn-load"', r'class="btn-premium-primary"', text)
text = re.sub(r'\.dir-btn-load\s*\{[^}]+\}', r'', text)

# ----------------------------
# Item 4: AI Chat and Canvas Refactor
# ----------------------------
# AI Bubbles
text = re.sub(
    r'\.chat-message\.ai\s*\{[^}]+\}',
    r'.chat-message.ai {\n  background: rgba(255,255,255,0.88);\n  border: 1px solid rgba(255,255,255,0.6);\n  box-shadow: 0 8px 20px rgba(15,23,42,0.04);\n  backdrop-filter: blur(12px);\n  color: var(--text-main);\n}',
    text
)
# User Bubbles
text = re.sub(
    r'\.chat-message\.user\s*\{[^}]+\}',
    r'.chat-message.user {\n  background: linear-gradient(135deg, #635bff 0%, #4f46e5 55%, #2563eb 100%);\n  color: #ffffff;\n  box-shadow: 0 10px 25px rgba(79,70,229,0.25);\n}',
    text
)
# Input Cockpit
text = re.sub(
    r'\.input-area\s*\{[^}]+\}',
    r'.input-area {\n  background: rgba(255,255,255,0.72);\n  backdrop-filter: blur(18px);\n  border: 1px solid rgba(255,255,255,0.6);\n  border-radius: 20px;\n  padding: 16px;\n  box-shadow: var(--shadow-layered);\n  display: flex;\n  flex-direction: column;\n  gap: 12px;\n  margin-top: 16px;\n}',
    text
)

# Form Cards Canvas
text = re.sub(
    r'\.field-item-box\s*\{[^}]+\}',
    r'.field-item-box {\n  background: rgba(255,255,255,0.92);\n  border: 1px solid rgba(226,232,240,0.9);\n  box-shadow: 0 20px 45px rgba(15,23,42,0.1), inset 0 1px 0 rgba(255,255,255,0.75);\n  border-radius: 16px;\n  padding: 28px;\n  margin-bottom: 12px;\n  transition: all 0.3s ease;\n}\n.field-item-box:hover {\n  box-shadow: 0 32px 70px rgba(15,23,42,0.16), inset 0 1px 0 rgba(255,255,255,0.9);\n  transform: translateY(-2px);\n}',
    text
)

# ----------------------------
# Item 5: Code & Structural Fixes
# ----------------------------
# Fix Draggable item-key title -> _fid or _aid (Actually sections usually have _aid or _fid, let's use '_aid' for sections and '_fid' for fields)
text = text.replace('item-key="title"', 'item-key="_aid"')
text = text.replace('item-key="label"', 'item-key="_fid"')

# Fix incorrect "+ ?????" button text token
# Locate inline action control that adds elements below
text = text.replace('?????', '+ ?????', 1) 

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated Buttons, Chat, Canvas, and structural fixes in AdminView.vue')
