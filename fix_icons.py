import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# ============================================================
# 1. Fix SVG elements: >×< between SVG child elements should be ><
#    Pattern: closing > followed by × followed by opening < inside SVGs
# ============================================================
# Fix SVG internal >×< (newline chars that got corrupted)
text = re.sub(r'>×<(path|circle|line|polyline|rect|/svg)', r'><\1', text)

# ============================================================
# 2. Fix empty HTML elements: >×</tag> should be ></tag>
#    For textarea, label, td, div (accent bars, spacers), span (badges), iframe
# ============================================================
text = re.sub(r'>×</textarea>', r'></textarea>', text)
text = re.sub(r'>×</iframe>', r'></iframe>', text)
text = re.sub(r'>×</label>', r'></label>', text)

# Fix: <div ...>×</div> for accent bars and spacers (but NOT icon boxes)
# We handle icon boxes separately below
text = text.replace('<div class="dir-card-accent"', '<div class="dir-card-accent" data-accent="1"')
text = re.sub(r'data-accent="1"([^>]*)>×</div>', r'data-accent="1"\1></div>', text)
text = text.replace(' data-accent="1"', '')

# Fix spacer div
text = text.replace('<div style="flex: 1">×</div>', '<div style="flex: 1"></div>')

# Fix view modal accent bar div
text = re.sub(r'(<div :style="`height: 6px[^"]*`">)×(</div>)', r'\1\2', text)

# Fix badge spans in dashboard table
text = re.sub(r'(<td[^>]*>)×(<span class="badge-form">)', r'\1\2', text)
text = re.sub(r'(</span>)×(</span>)×(</td>)', r'\1\2\3', text)

# Fix pulse indicator (should be empty - CSS handles the dot)
text = text.replace('<div class="pulse-indicator">×</div>', '<div class="pulse-indicator"></div>')

# Fix mode-text closing (× before </div> is stray)
text = text.replace('</b>×</div>', '</b></div>')

# Fix db-status-dot (should be empty - CSS handles the dot)
text = text.replace('<span class="db-status-dot">×</span>', '<span class="db-status-dot"></span>')

# ============================================================
# 3. Fix emoji icons in sidebar navigation
# ============================================================
text = text.replace('<div class="brand-logo ai-glow">×</div>', '<div class="brand-logo ai-glow">✨</div>')

# Nav icons - need to match in order: Create Form, Directory, Templates, Dashboard
nav_icons = [
    ("Create Form", "✨"),
    ("Directory", "📁"),
    ("Templates", "📂"),
    ("Dashboard", "📊"),
]
for label, icon in nav_icons:
    text = text.replace(
        f'<span class="nav-icon">×</span> {label}',
        f'<span class="nav-icon">{icon}</span> {label}'
    )

# ============================================================
# 4. Fix emoji icons in chat/upload area
# ============================================================
text = text.replace('<div class="sender-avatar sparkle-icon">×</div>', '<div class="sender-avatar sparkle-icon">✨</div>')
text = text.replace('<span class="mini-upload-icon">×</span>', '<span class="mini-upload-icon">📤</span>')
text = text.replace('<span class="file-preview-icon">×</span>', '<span class="file-preview-icon">📎</span>')

# btn-attach (paperclip icon for attaching files)
text = re.sub(
    r'(<button class="btn-attach"[^>]*>)×(</button>)',
    r'\1📎\2',
    text
)

# ============================================================
# 5. Fix emoji icons in canvas header
# ============================================================
# AI Canvas label
text = re.sub(r'(<span>)×(</span>\s*AI Canvas)', r'\1🎨\2', text)

# Device mode buttons
device_icons = ['🖥️', '📱', '📱']
for i, icon in enumerate(device_icons):
    mode = ['desktop', 'tablet', 'mobile'][i]
    text = re.sub(
        rf'(deviceMode = \'{mode}\'[^>]*>)×(</button>)',
        rf'\g<1>{icon}\2',
        text
    )

# Fullscreen toggle button - find it near isFullscreen
text = re.sub(r"{{ isFullscreen \? '×' : '×' }}", "{{ isFullscreen ? '🗗' : '🖵' }}", text)

# Empty canvas icon
text = text.replace('<div class="empty-icon-box">×</div>', '<div class="empty-icon-box">📄</div>')

# ============================================================
# 6. Fix emoji icons in canvas form editing toolbar
# ============================================================
# Edit button (✏️ แก้ไข)
text = text.replace(
    '<span class="icon">×</span> <span class="lbl">×</span>',
    '<span class="icon">✏️</span> <span class="lbl">แก้ไข</span>'
)

# Add field button (➕ เพิ่มฟิลด์)
text = text.replace(
    '<span class="icon">×</span> <span class="lbl">เพิ่มฟิลด์</span>',
    '<span class="icon">➕</span> <span class="lbl">เพิ่มฟิลด์</span>'
)

# Delete button (🗑️ ลบ) 
text = text.replace(
    '<span class="icon">×</span> <span class="lbl">ลบ</span>',
    '<span class="icon">🗑️</span> <span class="lbl">ลบ</span>'
)

# Logo upload span
text = text.replace('<span>× Upload / Replace Logo</span>', '<span>🖼️ Upload / Replace Logo</span>')

# ============================================================
# 7. Fix KPI dashboard icons
# ============================================================
kpi_icons = ['📄', '✅', '⏳']
kpi_count = 0
def replace_kpi(match):
    global kpi_count
    icon = kpi_icons[kpi_count] if kpi_count < len(kpi_icons) else '📊'
    kpi_count += 1
    return f'<div class="kpi-icon">{icon}</div>'

text = re.sub(r'<div class="kpi-icon">×</div>', replace_kpi, text)

# Panel icon for responses
text = text.replace('<span class="panel-icon">×</span>', '<span class="panel-icon">📋</span>')

# ============================================================
# 8. Fix input method icons that were lost
# ============================================================
input_icon_fixes = {
    "{ value: 'text_prompt', label: '1. Text Prompt Only', icon: '✨'": "{ value: 'text_prompt', label: '1. Text Prompt Only', icon: '✏️'",
    "{ value: 'physical_paper', label: '2. Physical Paper (OCR)', icon: '📄'": "{ value: 'physical_paper', label: '2. Physical Paper (OCR)', icon: '📄'",
    "{ value: 'handwritten_sketch', label: '3. Handwritten Sketch', icon: '✨'": "{ value: 'handwritten_sketch', label: '3. Handwritten Sketch', icon: '🖊️'",
    "{ value: 'voice', label: '4. Voice Instruction', icon: '📄'": "{ value: 'voice', label: '4. Voice Instruction', icon: '🎤'",
    "{ value: 'markdown', label: '5. Markdown (.md)', icon: '📄'": "{ value: 'markdown', label: '5. Markdown (.md)', icon: '📝'",
    "{ value: 'digital_pdf', label: '6. Digital PDF Extractor', icon: '📄'": "{ value: 'digital_pdf', label: '6. Digital PDF Extractor', icon: '📄'",
    "{ value: 'spreadsheet', label: '7. Legacy Spreadsheet', icon: '📄'": "{ value: 'spreadsheet', label: '7. Legacy Spreadsheet', icon: '📊'",
    "{ value: 'json_config', label: '9. JSON Configuration', icon: '📄'": "{ value: 'json_config', label: '9. JSON Configuration', icon: '⚙️'",
}
for bad, good in input_icon_fixes.items():
    text = text.replace(bad, good)

# ============================================================
# 9. Fix toolbar buttons (Undo, Redo, Reset) - check current state
# ============================================================
# These might have lost emojis too
text = re.sub(r'×( Undo)', r'↶\1', text)
text = re.sub(r'(Redo )×', r'\1↷', text)
text = re.sub(r'× Reset', r'🔄 Reset', text)

# Style button
text = re.sub(r'× Style', r'✨ Style', text)

# ============================================================
# 10. Fix close buttons (× is CORRECT here - keep them)
#     These are already correct, just making sure
# ============================================================
# btn-close-modal buttons are correct with × (close icon)
# remove-file-action button is correct with × (close icon)

# ============================================================
# 11. Fix the chat sender avatars
# ============================================================
text = re.sub(
    r"{{ msg\.sender === 'ai' \? '×' : '×' }}",
    "{{ msg.sender === 'ai' ? '🤖' : '👤' }}",
    text
)

# ============================================================
# 12. Fix Export .vue button text
# ============================================================
text = re.sub(r'×(Export \.vue)', r'\1', text)

# ============================================================
# 13. Fix the theme styling button
# ============================================================
text = re.sub(r"{{ themeLoading \? 'Styling\.\.\.' : '× Style' }}", "{{ themeLoading ? 'Styling...' : '✨ Style' }}", text)

# ============================================================
# 14. Fix remaining stray × that should be empty in SVG contexts
# ============================================================
# Any remaining >×< that we missed
text = re.sub(r'>×<(svg|/svg|g|/g|defs|use)', r'><\1', text)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

# Verify
remaining = text.count('×')
print(f"Done! Remaining × characters: {remaining}")
# Print contexts of remaining ×
lines = text.split('\n')
for i, line in enumerate(lines):
    if '×' in line:
        snippet = line.strip()[:120]
        print(f"  Line {i+1}: {snippet}")
