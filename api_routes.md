# API Routes Summary

เอกสารนี้สรุปเส้นทางของ API Endpoints ทั้งหมดที่มีการให้บริการผ่าน FastAPI (`backend-python/main.py`)

## 🌐 System & Health
| Method | URL Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | ตรวจสอบสถานะการทำงานของเซิร์ฟเวอร์, การเชื่อมต่อ MongoDB, และตรวจสอบว่าใส่ API Key ของ Gemini แล้วหรือยัง |

## 📄 Forms Management (การจัดการแบบฟอร์ม)
| Method | URL Path | Description |
|---|---|---|
| `GET` | `/api/v1/forms` | ดึงรายชื่อแบบฟอร์มทั้งหมดในระบบ (เรียงตามวันที่สร้างจากใหม่ไปเก่า) |
| `GET` | `/api/v1/forms/{form_id}` | ดึงข้อมูลโครงสร้างแบบฟอร์มแบบระบุ ID |
| `POST` | `/api/v1/forms` | บันทึกแบบฟอร์มใหม่ลงในฐานข้อมูล (มักใช้สำหรับฟอร์มที่ถูก Duplicate หรือสร้างขึ้นใหม่แบบ Manual) |
| `PUT` | `/api/v1/forms/{form_id}` | อัปเดตโครงสร้างฟอร์ม ข้อมูลทั่วไป และการปรับแต่ง Theme ของฟอร์มที่มีอยู่แล้ว |
| `DELETE`| `/api/v1/forms/{form_id}` | ลบแบบฟอร์มออกจากระบบ (รวมถึงเคลียร์ข้อมูล Responses/Submissions ที่เกี่ยวข้องทิ้งไปด้วย) |

## 🤖 AI Generation (การทำงานกับ Gemini AI)
| Method | URL Path | Description |
|---|---|---|
| `POST` | `/api/v1/forms/generate` | เป็น API หลักในการให้ AI สร้างโครงสร้างฟอร์มแบบไดนามิก รองรับอินพุตหลากหลาย เช่น รูปภาพวาดมือ (Sketch), รูปแบบฟอร์มกระดาษ (Image), เสียง (Voice), Text Prompt และ Markdown |
| `POST` | `/api/v1/ai/theme` | สร้างชุดสี (UI Theme CSS Tokens) แบบอัตโนมัติตาม Prompt ที่ผู้ใช้ขอ (เช่น "Modern Dark", "Ocean Blue") |

## 📝 Form Submissions (การส่งผลลัพธ์)
| Method | URL Path | Description |
|---|---|---|
| `POST` | `/api/v1/submit/{form_id}` | สำหรับให้ผู้ใช้งานทั่วไปส่งข้อมูลหลังจากกรอกแบบฟอร์มเสร็จสิ้น (Public Endpoint) |
| `GET` | `/api/v1/forms/{form_id}/responses`| ดึงข้อมูลผลลัพธ์ (Responses) ทั้งหมดที่ถูกกรอกเข้ามาในฟอร์มที่ระบุ |
| `GET` | `/api/v1/responses/all` | ดึงข้อมูลผลลัพธ์รวมจาก **ทุกฟอร์ม** ทั้งระบบ (ใช้สำหรับแสดงในหน้ารวม All Forms Dashboard) |
