import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

replacements = {
    '// สถานะ\ufffdาร\ufffd\ufffdแก้ไขฟิลด์ (Inline Editor)': '// สถานะการแก้ไขฟิลด์ (Inline Editor)',
    "text: '!\ \ufffdรุณาเลือ\ufffdฟัง\ufffd์ชันที่ต้อง\ufffdารจา\ufffdเมนูด้านซ้าย \ufffdนบไฟล์ \ufffdละพิมพ์คำสั่งตรง\ufffdลางนี้ได้เลยครับ \ufffdั่งขวาจะ\ufffdสดงผลฟอร์มหลังจา\ufffdที่ผมประมวลผลเสร็จ\ufffdล้ว '": "text: 'สวัสดีครับ! กรุณาเลือกฟังก์ชันที่ต้องการจากเมนูด้านซ้าย แนบไฟล์ และพิมพ์คำสั่งตรงกลางนี้ได้เลยครับ ฝั่งขวาจะแสดงผลฟอร์มหลังจากที่ผมประมวลผลเสร็จแล้ว ✨'",
    "if (selectedInputType.value === val) return  // ถ้าคลิก\ufffd function": "if (selectedInputType.value === val) return  // ถ้าคลิก function",
    "//  function เพื่อป้อง\ufffdันไฟล์ผิดประเทไปยัง backend": "// ล้างไฟล์เสมอเมื่อสลับ function เพื่อป้องกันไฟล์ผิดประเภทไปยัง backend",
    "text: 'ขออัยครับ โควตา\ufffdารใช้งาน AI  (Token Exhausted) รบ\ufffdวนรอสั\ufffdครู่\ufffdล้วลองใหม่อี\ufffdครั้งครับ \ufffd'": "text: 'ขออภัยครับ โควตาการใช้งาน AI (Token Exhausted) รบกวนรอสักครู่แล้วลองใหม่อีกครั้งครับ 🙏'",
    "title: `⚠️\ufffd Sandbox Mode (${activeFunction.value.label})`,": "title: `⚠️ Sandbox Mode (${activeFunction.value.label})`,",
    "//   ID \ufffdกลับเข้าสู่ generatedForm": "// ถ้าเป็นฟอร์มใหม่ ให้อัปเดต ID กลับเข้าสู่ generatedForm",
    "// \ufffdกรอง PointerEvent หรือ Event ของเบราว์เซอร์ออก\ufffd เพื่อใช้ค่าจา\ufffd generatedForm.value": "// กรอง PointerEvent หรือ Event ของเบราว์เซอร์ออก เพื่อใช้ค่าจาก generatedForm.value",
    '<option value="text">\ufffd📝 Text (Short)</option>': '<option value="text">📝 Text (Short)</option>',
    '<option value="file">\ufffd📎 File Upload</option>': '<option value="file">📎 File Upload</option>',
    "if (!confirm('ยืนยัน\ufffdารฟอร์มนี้?  Response จะถู\ufffdไปด้วย')) return": "if (!confirm('ยืนยันการลบฟอร์มนี้? ข้อมูล Response จะถูกลบไปด้วย')) return",
    '<div class="message-text-body thinking-state">\ufffdกำลังประมวลผล...</div>': '<div class="message-text-body thinking-state">กำลังประมวลผล...</div>',
    '<span>🖼\ufffd Upload / Replace Logo</span>': '<span>🖼️ Upload / Replace Logo</span>',
    '<span class="icon">\ufffd\ufffd</span> <span class="lbl">\ufffd\ufffdแก้ไข</span>': '<span class="icon">✏️</span> <span class="lbl">แก้ไข</span>',
    '<span class="icon">🗑\ufffd</span> <span class="lbl">×</span>': '<span class="icon">🗑️</span> <span class="lbl">ลบ</span>',
    '<option value="textarea">\ufffd📝 Textarea (Long)</option>': '<option value="textarea">📝 Textarea (Long)</option>',
    '<option value="checkbox">☑\ufffd Checkbox Options</option>': '<option value="checkbox">☑️ Checkbox Options</option>',
    '<div class="empty-icon-box">\ufffd</div>': '<div class="empty-icon-box">📄</div>',
    '>\ufffd</button>': '>×</button>',
    "text: '! \ufffdรุณาเลือ\ufffdฟัง\ufffd์ชันที่ต้อง\ufffdารจา\ufffdเมนูด้านซ้าย \ufffdนบไฟล์ \ufffdละพิมพ์คำสั่งตรง\ufffdลางนี้ได้เลยครับ \ufffdั่งขวาจะ\ufffdสดงผลฟอร์มหลังจา\ufffdที่ผมประมวลผลเสร็จ\ufffdล้ว '": "text: 'สวัสดีครับ! กรุณาเลือกฟังก์ชันที่ต้องการจากเมนูด้านซ้าย แนบไฟล์ และพิมพ์คำสั่งตรงกลางนี้ได้เลยครับ ฝั่งขวาจะแสดงผลฟอร์มหลังจากที่ผมประมวลผลเสร็จแล้ว ✨'",
    "icon: '\ufffd'": "icon: '📄'"
}

for bad, good in replacements.items():
    text = text.replace(bad, good)

# Ensure no `\ufffd` remains
text = text.replace('\ufffd', '')

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Final replacement complete.")
