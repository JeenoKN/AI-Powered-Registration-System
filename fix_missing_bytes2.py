import re

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'r', encoding='utf-8') as f:
    text = f.read()

replacements = {
    '\ufffdท็บที่\ufffdำลังทำงานอยู่\ufffdละราย\ufffdารฟอร์มจา\ufffd': 'แท็บที่กำลังทำงานอยู่และรายการฟอร์มจาก',
    'สถานะ\ufffdาร\ufffd\ufffd้ไขฟิลด์': 'สถานะการแก้ไขฟิลด์',
    'สถานะ\ufffdารลา\ufffdวาง': 'สถานะการลากวาง',
    '!\ufffdรุณาเลือ\ufffdฟัง\ufffd์ชันที่ต้อง\ufffdารจา\ufffdเมนูด้านซ้าย \ufffdนบไฟล์ \ufffdละพิมพ์คำสั่งตรง\ufffdลางนี้ได้เลยครับ \ufffdั่งขวาจะ\ufffdสดงผลฟอร์มหลังจา\ufffdที่ผมประมวลผลเสร็จ\ufffdล้ว': '! กรุณาเลือกฟังก์ชันที่ต้องการจากเมนูด้านซ้าย แนบไฟล์ และพิมพ์คำสั่งตรงกลางนี้ได้เลยครับ ฝั่งขวาจะแสดงผลฟอร์มหลังจากที่ผมประมวลผลเสร็จแล้ว',
    "icon: '\ufffd\ufffd'": "icon: '✨'",
    "icon: '\ufffd'": "icon: '📝'",
    "icon: '🖼\ufffd'": "icon: '🖼️'",
    "icon: '☑\ufffd'": "icon: '☑️'",
    "icon: '🗑\ufffd'": "icon: '🗑️'",
    'ถ้าคลิ\ufffd': 'ถ้าคลิก',
    'เพื่อป้อง\ufffdันไฟล์ผิดประเท\ufffdไปยัง': 'เพื่อป้องกันไฟล์ผิดประเภทไปยัง',
    'ฟัง\ufffd์ชันสำหรับเคลียร์ค่าที่ผู้ใช้\ufffdรอ\ufffdในฟอร์ม': 'ฟังก์ชันสำหรับเคลียร์ค่าที่ผู้ใช้กรอกในฟอร์ม',
    'ฟัง\ufffd์ชันส่งคำสั่งไปหา': 'ฟังก์ชันส่งคำสั่งไปหา',
    '(ส่งไฟล์เพื่อทำ\ufffdารวิเคราะห์รูปาพ)': '(ส่งไฟล์เพื่อทำการวิเคราะห์รูปภาพ)',
    'ฟอร์มของคุณถู\ufffdอัปเดตเรียบร้อย\ufffdล้ว!': 'ฟอร์มของคุณถูกอัปเดตเรียบร้อยแล้ว!',
    'เ\ufffdิดข้อผิดพลาดจา\ufffdเซิร์ฟเวอร์:': 'เกิดข้อผิดพลาดจากเซิร์ฟเวอร์:',
    'ข้อมูลที่ระบบดึงออ\ufffdมาได้': 'ข้อมูลที่ระบบดึงออกมาได้',
    'ขออ\ufffdัยครับ โควตา\ufffdารใช้งาน AI  (Token Exhausted) รบ\ufffdวนรอสั\ufffdครู่\ufffdล้วลองใหม่อี\ufffdครั้งครับ \ufffd': 'ขออภัยครับ โควตาการใช้งาน AI (Token Exhausted) รบกวนรอสักครู่แล้วลองใหม่อีกครั้งครับ 🙏',
    'ไม่สามารถเชื่อมต่อ\ufffdับ Backend   Backend เ\ufffdิด Error ระบบจึงจำลองฟอร์มขึ้นมา\ufffdทนครับ': 'ไม่สามารถเชื่อมต่อกับ Backend ได้ หรือ Backend เกิด Error ระบบจึงจำลองฟอร์มขึ้นมาแทนครับ',
    '⚠\ufffd': '⚠️',
    'วิเคราะห์จา\ufffdไฟล์จำลอง:': 'วิเคราะห์จากไฟล์จำลอง:',
    'ทดสอบ\ufffdล่องข้อความ...': 'ทดสอบกล่องข้อความ...',
    'ฟัง\ufffd์ชันส่งข้อมูลฟอร์มที่ผู้ใช้\ufffdรอ\ufffd': 'ฟังก์ชันส่งข้อมูลฟอร์มที่ผู้ใช้กรอก',
    'เซิร์ฟเวอร์ป\ufffdิเสธ\ufffdารบันทึ\ufffdข้อมูล:': 'เซิร์ฟเวอร์ปฏิเสธการบันทึกข้อมูล:',
    '\ufffdลับเข้าสู่': 'กลับเข้าสู่',
    'บันทึ\ufffdฟอร์มใหม่สำเร็จ!': 'บันทึกฟอร์มใหม่สำเร็จ!',
    'ของคุณเรียบร้อย\ufffdล้วครับ!': 'ของคุณเรียบร้อยแล้วครับ!',
    'เ\ufffdิดข้อผิดพลาดใน\ufffdารบันทึ\ufffd:': 'เกิดข้อผิดพลาดในการบันทึก:',
    'ฟัง\ufffd์ชันสำหรับ\ufffdาร Export โครงสร้างฟอร์มออ\ufffdมาเป็นไฟล์': 'ฟังก์ชันสำหรับการ Export โครงสร้างฟอร์มออกมาเป็นไฟล์',
    '\ufffdรอง PointerEvent  Event ของเบราว์เซอร์ออ\ufffd': 'กรอง PointerEvent หรือ Event ของเบราว์เซอร์ออก',
    'สำหรับ\ufffdต่ละ field เพื่อป้อง\ufffdัน key ชน\ufffdัน (โดยเฉพาะชื่อาษาไทย)': 'สำหรับแต่ละ field เพื่อป้องกัน key ชนกัน (โดยเฉพาะชื่อภาษาไทย)',
    'ป้อง\ufffdัน key ซ้ำ\ufffdัน': 'ป้องกัน key ซ้ำกัน',
    "alert('บันทึ\ufffdข้อมูลสำเร็จ! ')": "alert('บันทึกข้อมูลสำเร็จ! 🚀')",
    'เคลียร์ค่าฟิลด์ที่ถู\ufffdซ่อนโดย': 'เคลียร์ค่าฟิลด์ที่ถูกซ่อนโดย',
    'จา\ufffd allFieldKeys  pre-compute ไว้\ufffdล้ว': 'จาก allFieldKeys ที่ pre-compute ไว้แล้ว',
    'โปรดเลือ\ufffdข้อมูล...': 'โปรดเลือกข้อมูล...',
    '\ufffdำลังบันทึ\ufffd...': 'กำลังบันทึก...',
    '>\ufffd<': '>×<',
    '\ufffd Text (Short)': '📝 Text (Short)',
    '\ufffd Textarea (Long)': '📝 Textarea (Long)',
    '\ufffd File Upload': '📎 File Upload',
    'ยืนยัน\ufffdาร\ufffdฟอร์มนี้?  Response จะถู\ufffd\ufffdไปด้วย': 'ยืนยันการลบฟอร์มนี้? ข้อมูล Response จะถูกลบไปด้วย',
    'ยืนยัน\ufffdาร Field ?': 'ยืนยันการลบ Field นี้?',
    '\ufffdำลังประมวลผล...': 'กำลังประมวลผล...',
    '\ufffd\ufffd้ไข': 'แก้ไข',
    'อัปโหลดรูปถ่ายฟอร์มเอ\ufffdสารใบเสร็จ/': 'อัปโหลดรูปถ่ายฟอร์มเอกสารใบเสร็จ/ใบสมัคร',
    'โครงสร้างเอ\ufffdสาร Text รูป\ufffdบบ': 'โครงสร้างเอกสาร Text รูปแบบ',
    'เอ\ufffdสารประเท PDF': 'เอกสารประเภท PDF',
    'าพ\ufffdคปหน้าจอ UI ของเว็บไซต์เ\ufffd่า': 'ภาพแคปหน้าจอ UI ของเว็บไซต์เก่า',
    'าพส\ufffd\ufffdน PDF/TIFF': 'ภาพสแกน PDF/TIFF ความละเอียดสูง',
    "icon: '\ufffd'": "icon: '📄'", 
    "  \"${generatedForm.value.title}\"  MongoDB ": " 🎉 อัปเดตโครงสร้างฟอร์มดิจิทัล \"${generatedForm.value.title}\" ลงในระบบ MongoDB ",
    "  function เพื่อป้อง\ufffdันไฟล์ผิดประเท\ufffdไปยัง": " // ล้างไฟล์เสมอเมื่อสลับ function เพื่อป้องกันไฟล์ผิดประเภทไปยัง",
    "  [] ฟัง\ufffd์ชันสำหรับเคลียร์ค่าที่ผู้ใช้\ufffdรอ\ufffdในฟอร์ม": " // 👇 [เพิ่มใหม่] ฟังก์ชันสำหรับเคลียร์ค่าที่ผู้ใช้กรอกในฟอร์ม",
    " [] ไม่สามารถเชื่อมต่อ": "🚨 [ข้อผิดพลาด] ไม่สามารถเชื่อมต่อ",
    " !')": " 🚀')",
    " : '\ufffd')": " : 'คำสั่งจำลอง')",
    " : '\ufffd'": " : 'คำสั่งจำลอง'",
    "  ID \ufffdลับเข้าสู่": " ถ้าเป็นฟอร์มใหม่ ให้อัปเดต ID กลับเข้าสู่",
    " Directory Card \ufffd Premium Redesign ": " Directory Card — Premium Redesign "
}

for bad, good in replacements.items():
    text = text.replace(bad, good)

# Regex for the specific lines that were really broken
text = re.sub(r'\{ value: \'physical_paper\', label: \'2. Physical Paper \(OCR\)\', icon: \'📄\', hint: \'อัปโหลดรูปถ่ายฟอร์มเอกสารใบเสร็จ/.*?\' \},',
              r"{ value: 'physical_paper', label: '2. Physical Paper (OCR)', icon: '📄', hint: 'อัปโหลดรูปถ่ายฟอร์มเอกสารใบเสร็จ/ใบสมัคร' },", text)
text = re.sub(r'\{ value: \'digital_pdf\', label: \'6. Digital PDF Extractor\', icon: \'📄\', hint: \'เอกสารประเภท PDF .*?\' \},',
              r"{ value: 'digital_pdf', label: '6. Digital PDF Extractor', icon: '📄', hint: 'เอกสารประเภท PDF ฟอร์มดิจิทัล' },", text)
text = re.sub(r'\{ value: \'scanned_image\', label: \'10. Scanned Image\', icon: \'📄\', hint: \'ภาพสแกน PDF/TIFF ความละเอียดสูง.*?\' \}',
              r"{ value: 'scanned_image', label: '10. Scanned Image', icon: '🖨️', hint: 'ภาพสแกน PDF/TIFF ความละเอียดสูง' }", text)

with open(r'e:\NewSystem\frontend-vue\src\views\AdminView.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Final replacement of U+FFFD characters complete.")
