import re
with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace corrupted inputMethods array
new_input_methods = '''const inputMethods = [
  { value: 'text_prompt', label: '1. Text Prompt Only', icon: '✨', hint: 'พิมพ์คำสั่งและอธิบายสิ่งที่คุณต้องการเพื่อสร้างฟอร์ม' },
  { value: 'physical_paper', label: '2. Physical Paper (OCR)', icon: '📄', hint: 'ถ่ายรูปหรืออัปโหลดรูปภาพกระดาษ/แบบฟอร์มที่มีอยู่' },
  { value: 'handwritten_sketch', label: '3. Handwritten Sketch', icon: '✏️', hint: 'อัปโหลดรูปภาพวาดมือหรือสเก็ตช์ที่คุณวาดไว้' },
  { value: 'voice', label: '4. Voice Instruction', icon: '🎙️', hint: 'ใช้เสียงพูดเพื่อสั่งการและอธิบายฟอร์มที่ต้องการ' },
  { value: 'markdown', label: '5. Markdown (.md)', icon: '📝', hint: 'วางข้อความ Markdown เพื่อสร้างฟอร์ม' },
  { value: 'digital_pdf', label: '6. Digital PDF Extractor', icon: '📑', hint: 'อัปโหลดไฟล์ PDF เพื่อดึงโครงสร้างและข้อความ' },
  { value: 'spreadsheet', label: '7. Legacy Spreadsheet', icon: '📊', hint: 'ใช้ข้อมูลจากไฟล์ Excel, Google Sheets หรือ CSV' },
  { value: 'ui_screenshot', label: '8. UI Screenshot', icon: '🖼️', hint: 'อัปโหลดภาพหน้าจอ UI เพื่อแปลงเป็นฟอร์ม' },
  { value: 'json_config', label: '9. JSON Configuration', icon: '⚙️', hint: 'ใช้โครงสร้าง JSON Schema เพื่อสร้างฟอร์ม' },
  { value: 'scanned_image', label: '10. Scanned Image', icon: '🖨️', hint: 'อัปโหลดรูปภาพ PDF/TIFF ที่สแกนเพื่อสร้างฟอร์ม' }
]'''
content = re.sub(r'const inputMethods = \[.*?\]', new_input_methods, content, flags=re.DOTALL)

# Replace corrupted chat messages
content = re.sub(r'chatMessages\.value = \[\s*\{\s*sender:\s*\'ai\',\s*text:.*?\}\s*\]', 
                 "chatMessages.value = [\n  { sender: 'ai', text: 'สวัสดีครับ! กรุณาเลือกฟังก์ชันที่ต้องการจากเมนูด้านซ้าย แนบไฟล์ และพิมพ์คำสั่งตรงกลางนี้ได้เลยครับ ฝั่งขวาจะแสดงผลฟอร์มหลังจากที่ผมประมวลผลเสร็จแล้ว ✨' }\n]", 
                 content, flags=re.DOTALL)

# Replace other corrupted chat pushes
content = re.sub(r'chatMessages\.value\.push\(\{ sender: \'ai\', text: `.*?File attached: \$\{file\.name\}` \}\)',
                 "chatMessages.value.push({ sender: 'ai', text: `✅ File attached: ${file.name}` })",
                 content)

content = re.sub(r'chatMessages\.value\.push\(\{ sender: \'ai\', text: `.*?Upload failed: \$\{err\.message\}` \}\)',
                 "chatMessages.value.push({ sender: 'ai', text: `❌ Upload failed: ${err.message}` })",
                 content)

content = re.sub(r'chatMessages\.value\.push\(\{ sender: \'ai\', text: `.*?Error: \$\{error\.message\}` \}\)',
                 "chatMessages.value.push({ sender: 'ai', text: `❌ Error: ${error.message}` })",
                 content)

content = re.sub(r'chatMessages\.value\.push\(\{ sender: \'ai\', text: `.*?Error connecting: \$\{err\.message\}` \}\)',
                 "chatMessages.value.push({ sender: 'ai', text: `❌ Error connecting: ${err.message}` })",
                 content)

# Fix corrupted form generation messages
content = re.sub(r"text: '.*?'\+ textPrompt\.value",
                 "text: 'ฉันได้สร้างแบบฟอร์มอย่างง่ายตามที่คุณร้องขอแล้วค่ะ...' + textPrompt.value",
                 content)

# Replace nav icons which were corrupted
content = re.sub(r'<span class="nav-icon">.*?</span>\s*Create Form', '<span class="nav-icon">✨</span> Create Form', content)
content = re.sub(r'<span class="nav-icon">.*?</span>\s*Directory', '<span class="nav-icon">📁</span> Directory', content)
content = re.sub(r'<span class="nav-icon">.*?</span>\s*Templates', '<span class="nav-icon">📂</span> Templates', content)
content = re.sub(r'<span class="nav-icon">.*?</span>\s*Dashboard', '<span class="nav-icon">📊</span> Dashboard', content)


with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Replaced corrupted text')
