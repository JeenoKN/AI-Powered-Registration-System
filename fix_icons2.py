with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# ============================================================
# 1. Fix Undo/Redo/Reset buttons - restore icons
# ============================================================
# Undo button - add ↶ before "Undo"
text = text.replace(
    '                 Undo\r\n              </button>',
    '                ↶ Undo\r\n              </button>'
)
# Also handle without \r
text = text.replace(
    '                 Undo\n              </button>',
    '                ↶ Undo\n              </button>'
)

# Redo button - add ↷ after "Redo"
text = text.replace(
    '                Redo \r\n              </button>',
    '                Redo ↷\r\n              </button>'
)
text = text.replace(
    '                Redo \n              </button>',
    '                Redo ↷\n              </button>'
)

# Reset button - add 🔄 before "Reset"
text = text.replace(
    '                 Reset\r\n              </button>',
    '                🔄 Reset\r\n              </button>'
)
text = text.replace(
    '                 Reset\n              </button>',
    '                🔄 Reset\n              </button>'
)

# ============================================================
# 2. Fix chat sender avatars - were replaced with wrong text
# ============================================================
text = text.replace(
    "{{ msg.sender === 'ai' ? '' : 'คำสั่งจำลอง' }}",
    "{{ msg.sender === 'ai' ? '🤖' : '👤' }}"
)

# ============================================================
# 3. Fix fullscreen toggle button - was replaced with wrong text  
# ============================================================
text = text.replace(
    "{{ isFullscreen ? '' : 'คำสั่งจำลอง' }}",
    "{{ isFullscreen ? '🗗' : '🖵' }}"
)

# ============================================================
# 4. Fix Style button - missing ✨
# ============================================================
text = text.replace(
    "{{ themeLoading ? 'Styling...' : ' Style' }}",
    "{{ themeLoading ? 'Styling...' : '✨ Style' }}"
)

# ============================================================
# 5. Fix canvas wrapper :style fallback - wrong text inserted
# ============================================================
text = text.replace(
    "? `background-color: ${generatedForm.theme.bg_color}` : 'คำสั่งจำลอง'",
    "? `background-color: ${generatedForm.theme.bg_color}` : ''"
)

# ============================================================
# 6. Fix any other places where '' was wrongly replaced with 'คำสั่งจำลอง'
#    Only fix cases that are clearly wrong (in :style or empty fallbacks)
# ============================================================
# The sandbox mode description fallback
# Already handled correctly - leave it

# ============================================================
# 7. Fix input method hints that became empty
# ============================================================
text = text.replace(
    "{ value: 'text_prompt', label: '1. Text Prompt Only', icon: '✏️', hint: '' }",
    "{ value: 'text_prompt', label: '1. Text Prompt Only', icon: '✏️', hint: 'สั่งงานด้วยข้อความภาษาธรรมชาติโดยตรง' }"
)
text = text.replace(
    "{ value: 'handwritten_sketch', label: '3. Handwritten Sketch', icon: '🖊️', hint: '' }",
    "{ value: 'handwritten_sketch', label: '3. Handwritten Sketch', icon: '🖊️', hint: 'รูปภาพฟอร์มที่ร่างด้วยลายมือ' }"
)
text = text.replace(
    "{ value: 'voice', label: '4. Voice Instruction', icon: '🎤', hint: '' }",
    "{ value: 'voice', label: '4. Voice Instruction', icon: '🎤', hint: 'ไฟล์เสียงพูดสั่งงานหรือคำอธิบาย' }"
)
text = text.replace(
    "{ value: 'spreadsheet', label: '7. Legacy Spreadsheet', icon: '📊', hint: ' Excel, Google Sheets  CSV' }",
    "{ value: 'spreadsheet', label: '7. Legacy Spreadsheet', icon: '📊', hint: 'ไฟล์ตาราง Excel, Google Sheets หรือ CSV' }"
)
text = text.replace(
    "{ value: 'json_config', label: '9. JSON Configuration', icon: '⚙️', hint: ' JSON Schema' }",
    "{ value: 'json_config', label: '9. JSON Configuration', icon: '⚙️', hint: 'ไฟล์โครงสร้าง JSON Schema' }"
)

# ============================================================
# 8. Fix the 'ลบฟอร์มไม่สำเร็จ' alert
# ============================================================
text = text.replace("alert('ฟอร์มไม่สำเร็จ')", "alert('ลบฟอร์มไม่สำเร็จ')")

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("All icon and text fixes applied successfully!")
