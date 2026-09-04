# MongoDB Database Schema

เอกสารนี้สรุปโครงสร้างของ Database Collections ทั้งหมดที่ถูกใช้งานในโปรเจกต์ปัจจุบัน (อ้างอิงจาก `backend-python/main.py`)

## 1. `forms` Collection
เก็บโครงสร้างของแบบฟอร์มที่สร้างขึ้นในระบบทั้งหมด (รวมถึงฟอร์มที่สร้างจาก AI และสร้างด้วยตัวเอง/Duplicate)

| Field Name | Data Type | Description |
|---|---|---|
| `_id` | ObjectId | รหัสประจำตัวของฟอร์ม (สร้างโดย MongoDB อัตโนมัติ) |
| `title` | String | ชื่อแบบฟอร์ม |
| `description` | String | รายละเอียดหรือคำอธิบายแบบฟอร์ม |
| `theme_color` | String | สีหลักของฟอร์ม (เช่น `#ffffff`) |
| `input_type_used` | String | ที่มาของฟอร์ม (เช่น `text_prompt`, `manual`, `voice`, `scanned_image`) |
| `theme` | Object (Optional)| ออบเจกต์เก็บค่าตัวแปร CSS (Tokens) สำหรับการตกแต่งฟอร์ม เช่น `bg_color`, `card_bg`, `text_color`, `border_radius` เป็นต้น |
| `sections` | Array of Objects | รายการของส่วนต่างๆ (Sections) ภายในฟอร์ม |
| `sections[].title` | String | ชื่อของ Section |
| `sections[].description`| String (Optional)| คำอธิบายเพิ่มเติมสำหรับ Section |
| `sections[].fields` | Array of Objects | รายการของอินพุตใน Section นั้นๆ ประกอบด้วย `name`, `label`, `type` (text, email, select, etc.), `required` (Boolean), `options` (Array), `_fid` (String) |
| `created_at` | Datetime | วันและเวลาที่สร้างฟอร์ม (UTC) (มีการทำ Indexing บนฟิลด์นี้) |

---

## 2. `responses` Collection
เก็บข้อมูลผลลัพธ์ (Submissions) ที่ผู้ใช้งานหรือ User กรอกเข้ามาในแต่ละฟอร์ม

| Field Name | Data Type | Description |
|---|---|---|
| `_id` | ObjectId | รหัสประจำตัวของ Response แต่ละรายการ |
| `form_id` | String | รหัส ID ของฟอร์มที่อ้างอิงถึง `forms._id` (มีการทำ Indexing เพื่อดึงข้อมูลได้เร็วขึ้น) |
| `answers` | Object (Dict) | ออบเจกต์เก็บข้อมูลที่ผู้ใช้กรอก โดยใช้ Key เป็น `field_id` หรือ `field_name` และ Value เป็นข้อมูลที่ผู้ใช้พิมพ์หรือเลือก |
| `respondent_info` | Object / String | ข้อมูลเพิ่มเติมของผู้ตอบ (Metadata) |
| `created_at` | Datetime | วันและเวลาที่ส่งแบบฟอร์ม (UTC) |

---

## 3. `submissions` Collection (Reserved)
ปัจจุบันถูกสร้าง Index เอาไว้และผูกการลบเมื่อผู้ใช้ลบฟอร์ม แต่ฟังก์ชันการเพิ่มข้อมูลจริง (Insert) จะไปลงที่ `responses` แทน (เป็น Legacy/Reserved Collection)

| Field Name | Data Type | Description |
|---|---|---|
| `form_id` | String | รหัสอ้างอิง (มีการทำ Indexing ไว้บนฟิลด์นี้) |
