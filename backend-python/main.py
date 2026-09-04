import datetime
import io
import json
import os
import traceback  # 🚨 เพิ่มสำหรับดักจับ Log Error
from typing import Any

from bson import ObjectId
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
from google import genai
from google.genai import types
import shutil
import uuid
import pandas as pd
import io
from pymongo import MongoClient
from pydantic import BaseModel, Field

app = FastAPI(title="AI Dynamic Chat & Form Backend (Strict Multi-Modal Edition)")

# Mount static files for uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/api/v1/uploads", StaticFiles(directory="uploads"), name="uploads")

# เปิดการเชื่อมต่อ CORS สำหรับ Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://newsystem-mongodb:27017/NewSystem")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


# โหลดไฟล์ .env 
def _load_dotenv_if_exists(path: str | None = None) -> None:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), ".env")
    try:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and os.getenv(key) is None:
                    os.environ[key] = val
    except Exception:
        pass

_load_dotenv_if_exists()

# เชื่อมต่อ Gemini API
_gemini_api_key = os.getenv("GEMINI_API_KEY")
if _gemini_api_key:
    client = genai.Client(api_key=_gemini_api_key)
else:
    client = genai.Client()

# เชื่อมต่อฐานข้อมูล MongoDB
mongo_client = MongoClient(MONGO_URI)
try:
    db = mongo_client.get_default_database()
    if db.name in {"admin", "", None}:
        db = mongo_client["NewSystem"]
except Exception:
    db = mongo_client["NewSystem"]

forms_collection = db["forms"]
submissions_collection = db["submissions"]
responses_collection = db["responses"]

forms_collection.create_index("created_at")
submissions_collection.create_index("form_id")
responses_collection.create_index("form_id")

# --- Phase 3: Templates Collection ---
templates_collection = db["templates"]
templates_collection.create_index("created_at")

class ResponseSubmission(BaseModel):
    form_id: str
    answers: dict
    respondent_info: dict | str = {}
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

def normalize_doc(document: dict[str, Any] | None) -> dict[str, Any] | None:
    if document is None:
        return None
    result: dict[str, Any] = {}
    for key, value in document.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime.datetime):
            if value.tzinfo is None:
                result[key] = value.replace(tzinfo=datetime.timezone.utc).isoformat()
            else:
                result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = normalize_doc(value)
        elif isinstance(value, list):
            result[key] = [normalize_doc(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    if "_id" in result:
        result["id"] = result.pop("_id")
    return result

def parse_json_value(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    return value

async def parse_request_body(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        return await request.json()
    if "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        data: dict[str, Any] = {}
        for key, value in form.items():
            if isinstance(value, UploadFile):
                data[key] = value
            else:
                data[key] = parse_json_value(value)
        return data
    return await request.json()

# ==========================================
# 🛠️ 1. แก้ไขกฎให้เข้มงวดและบังคับใช้โครงสร้าง sections
# ==========================================
def build_system_instruction() -> str:
    return (
        "You are an Expert UI/UX Form Architect AI.\n"
        "CRITICAL RULE 1: If the user uploads an image, photo, or screenshot, you MUST perfectly REPLICATE EXACTLY what is written and shown. DO NOT invent, hallucinate, or add extra fields. Extract every single visible input field strictly.\n"
        "CRITICAL RULE 2: If the user provides a text prompt, strictly follow their exact requirements without adding unnecessary fluff.\n\n"
        "You must ALWAYS reply with a single valid JSON object containing exactly two keys:\n"
        "1. 'reply': (string) Your friendly conversational response IN THAI explaining what you extracted.\n"
        "2. 'form': (object or null) The form schema.\n\n"
        "When generating the 'form' object, use this exact strict structure (Notice the 'sections' array):\n"
        "{\n"
        "  \"title\": \"Exact Form Title from Image or Request\",\n"
        "  \"description\": \"Form Description\",\n"
        "  \"theme_color\": \"#0e7090\",\n"
        "  \"theme\": {\n"
        "    \"logo_url\": \"\"\n"
        "  },\n"
        "  \"sections\": [\n"
        "    {\n"
        "      \"title\": \"Section Name (Group related fields logically)\",\n"
        "      \"description\": \"Brief section description\",\n"
        "      \"fields\": [\n"
        "        {\n"
        "          \"name\": \"db_field_name\", // English, lowercase, no spaces\n"
        "          \"label\": \"Exact field name as seen in image/prompt\",\n"
        "          \"placeholder\": \"Placeholder text\",\n"
        "          \"db_note\": \"Description of data\",\n"
        "          \"type\": \"text|number|email|date|textarea|select|radio|checkbox|file|master_data\",\n"
        "          \"master_data_category\": \"provinces|faculties|title_names (only if type is master_data)\",\n"
        "          \"required\": true,\n"
        "          \"options\": [\"Option 1\", \"Option 2\"] // Only for select/radio/checkbox\n"
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "CRITICAL RULE 3 (MASTER DATA): Whenever the user requests common data fields (like Provinces, Faculties, or Title Names), you MUST change the field type to 'master_data' and set a 'master_data_category' property to the corresponding value (e.g., 'provinces', 'faculties', 'title_names'). Do not default to text input for these fields.\n"
        "CRITICAL RULE 4 (LOGO): If the user provides an image URL in their instruction and asks for it to be a logo, set the theme.logo_url to that URL exactly. If they do NOT ask for a logo, strictly preserve the existing theme.logo_url and do NOT inject an empty placeholder or nullify it.\n"
        "Do not include markdown block ticks like ```json."
    )

def build_ai_prompt(input_type: str, prompt: str | None = None, extracted_data: str | None = None) -> str:
    base_msg = "Please generate a dynamic form schema based on the details below:\n"
    if input_type == "text_prompt":
        return f"{base_msg}Input Type: 1. Text Prompt (Natural Language Description)\nDescription: {prompt}"
    elif input_type in ["physical_paper", "scanned_image"]:
        return (
            "CRITICAL INSTRUCTION: Look closely at the attached image. It contains a real physical application form.\n"
            "Your ONLY task is to read the text INSIDE the image, extract all fields (e.g., Name, Email, Date, Phone), "
            "and convert those exact fields into the digital JSON form schema.\n"
            "DO NOT create a form about 'image analysis' or 'photo processing'. Create a digital clone of the form visible in the image.\n"
            f"Additional user request: {prompt or 'None'}"
        )
    elif input_type == "handwritten_sketch":
        return (
            "CRITICAL INSTRUCTION: Look closely at the attached handwritten sketch.\n"
            "Identify the form layout drawn by the user inside the image and convert it into the digital JSON form schema.\n"
            f"Additional user request: {prompt or 'None'}"
        )
    elif input_type == "voice":
        return f"{base_msg}Input Type: 4. Voice Instruction (Speech-to-Text Transcription)\nTranscribed Content: {extracted_data}\nUser Request Context: {prompt or 'None'}"
    elif input_type == "markdown":
        return f"{base_msg}Input Type: 5. Markdown Document (.md File)\nRaw Markdown Structure:\n{extracted_data or prompt}"
    elif input_type == "digital_pdf":
        return f"{base_msg}Input Type: 6. Digital Electronic PDF (Extracted Core Text)\nExtracted Document Text:\n{extracted_data}"
    elif input_type == "spreadsheet":
        return f"{base_msg}Input Type: 7. Legacy Spreadsheet Headers (CSV/Excel Column Names)\nDetected Table Headers: {extracted_data}\nMap these header categories perfectly into input fields."
    elif input_type == "ui_screenshot":
        return (
            "CRITICAL INSTRUCTION: Look closely at the attached user interface screenshot.\n"
            "Replicate all visible input boxes, checkboxes, radio buttons, and dropdowns from the screenshot into the JSON form schema.\n"
            f"Additional user request: {prompt or 'None'}"
        )
    elif input_type == "json_config":
        return f"{base_msg}Input Type: 9. JSON Configuration Schema (Raw Data Review)\nProvided Configuration to analyze:\n{extracted_data or prompt}"
    
    return f"Process this input:\n{prompt or ''}"

# ==========================================
# 🛠️ 2. แก้ไขให้รองรับระบบ Sections และป้องกัน API ล่ม
# ==========================================
def validate_form_schema(schema: Any) -> dict[str, Any]:
    if not isinstance(schema, dict):
        raise ValueError("โครงสร้างฟอร์มต้องเป็น JSON Object")
    
    # ดักเผื่อ AI ดื้อ ส่งมาเป็น fields ธรรมดา (แปลงให้อยู่ใน section อัตโนมัติ หน้าเว็บจะได้ไม่พัง)
    if "fields" in schema and "sections" not in schema:
        schema["sections"] = [
            {
                "title": "General Information",
                "description": "ข้อมูลทั่วไป",
                "fields": schema.pop("fields")
            }
        ]

    if "sections" not in schema or not isinstance(schema["sections"], list):
        raise ValueError("โครงสร้างฟอร์มต้องมีอาเรย์ของ sections")
    
    if "theme_color" not in schema or not schema["theme_color"]:
        schema["theme_color"] = "#ffffff"

    master_data_cache = None
    for section in schema["sections"]:
        if "fields" not in section:
            section["fields"] = []
        for field in section["fields"]:
            if "name" not in field or "type" not in field or "label" not in field:
                raise ValueError("ทุกๆ ฟิลด์จำเป็นต้องระบุ name, type และ label เสมอ")
            
            if field.get("type") == "master_data":
                field["type"] = "select"
                category = field.get("master_data_category")
                if category:
                    try:
                        if master_data_cache is None:
                            import json
                            with open("master_data.json", "r", encoding="utf-8") as f:
                                master_data_cache = json.load(f)
                        if category in master_data_cache:
                            field["options"] = master_data_cache[category]
                    except Exception as e:
                        print(f"Error loading master_data.json: {e}")
            
            field["required"] = bool(field.get("required", False))
            field["options"] = field.get("options", [])
            field["width"] = str(field.get("width", "full"))
            if field.get("placeholder") is None:
                field["placeholder"] = ""
            if field.get("db_note") is None:
                field["db_note"] = "Data field"
            # Conditional Logic: preserve condition_field and condition_value
            if "condition_field" in field:
                field["condition_field"] = field["condition_field"]
            if "condition_value" in field:
                field["condition_value"] = field["condition_value"]
    return schema

async def call_ai_schema(prompt: str, image_bytes: bytes | None = None, image_mime: str = "image/png", audio_bytes: bytes | None = None, audio_mime: str | None = None) -> dict[str, Any]:
    import asyncio

    contents = []
    
    if image_bytes:
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=image_mime
        )
        contents.append(image_part)
        
    if audio_bytes and audio_mime:
        audio_part = types.Part.from_bytes(
            data=audio_bytes,
            mime_type=audio_mime
        )
        contents.append(audio_part)
        
    contents.append(prompt)

    config = types.GenerateContentConfig(
        system_instruction=build_system_instruction(),
        response_mime_type="application/json",
    )

    # รายชื่อ model ที่จะลองใช้ตามลำดับ (fallback chain)
    FALLBACK_MODELS = [GEMINI_MODEL, "gemini-2.0-flash"]
    # ตรวจสอบว่า GEMINI_MODEL ไม่ซ้ำกัน
    seen = set()
    unique_models = []
    for m in FALLBACK_MODELS:
        if m not in seen:
            seen.add(m)
            unique_models.append(m)

    MAX_RETRIES = 3
    RETRY_DELAYS = [5, 10, 20]  # วินาที (exponential backoff)
    
    last_error = None
    
    for model_name in unique_models:
        for attempt in range(MAX_RETRIES):
            try:
                print(f"🤖 Gemini request: model={model_name}, attempt={attempt + 1}/{MAX_RETRIES}")
                response = await run_in_threadpool(
                    client.models.generate_content,
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                raw_content = response.text
                
                if not raw_content:
                    raise ValueError("AI ไม่ได้ตอบกลับมาเป็นข้อความ")

                raw_content = raw_content.strip()
                try:
                    result = json.loads(raw_content)
                    if model_name != GEMINI_MODEL:
                        print(f"✅ สำเร็จด้วย fallback model: {model_name}")
                    return result
                except Exception as exc:
                    try:
                        import re
                        m = re.search(r"\{[\s\S]*\}", raw_content)
                        if m:
                            candidate = m.group(0)
                            result = json.loads(candidate)
                            return result
                    except Exception:
                        pass
                    preview = (raw_content[:1000] + "...") if len(raw_content) > 1000 else raw_content
                    raise ValueError(f"AI คืนค่าโครงสร้างที่แปลงเป็น JSON ไม่ได้ (preview): {preview}") from exc
                    
            except ValueError:
                # JSON parse error — ไม่ใช่ rate limit, ไม่ต้อง retry
                raise
            except Exception as e:
                error_str = str(e).lower()
                last_error = e
                is_rate_limit = "429" in str(e) or "resource_exhausted" in error_str or "too many requests" in error_str
                is_unavailable = "503" in str(e) or "service unavailable" in error_str or "overloaded" in error_str
                
                if is_rate_limit or is_unavailable:
                    error_type = "429 Rate Limit" if is_rate_limit else "503 Unavailable"
                    if attempt < MAX_RETRIES - 1:
                        wait_sec = RETRY_DELAYS[attempt]
                        print(f"⏳ {error_type} — รอ {wait_sec}s แล้ว retry... (model={model_name}, attempt={attempt + 1})")
                        await asyncio.sleep(wait_sec)
                        continue
                    else:
                        print(f"❌ หมด retry สำหรับ model={model_name} — ลอง fallback model ต่อไป")
                        break  # ออกจาก retry loop → ลอง model ถัดไป
                else:
                    # Error อื่น ๆ ที่ไม่ใช่ rate limit → raise ทันที
                    print(f"🚨 Gemini API Error (non-retriable):")
                    traceback.print_exc()
                    raise RuntimeError(f"เรียก Gemini ล้มเหลว: {e}") from e
    
    # ถ้าลองหมดทุก model แล้วยังไม่ได้
    print(f"🚨 Gemini ล้มเหลวทุก model และทุก retry:")
    traceback.print_exc()
    
    # Check if the last error is a rate limit / quota exhausted error
    last_error_str = str(last_error).lower()
    if "429" in last_error_str or "resource_exhausted" in last_error_str or "too many requests" in last_error_str:
        raise HTTPException(status_code=429, detail="QUOTA_EXCEEDED")
        
    raise RuntimeError(
        f"⚠️ ระบบ Gemini AI ไม่สามารถตอบสนองได้ในขณะนี้ (ลองทั้งหมด {len(unique_models)} models, {MAX_RETRIES} ครั้ง/model) "
        f"สาเหตุ: {last_error} — กรุณาลองใหม่อีกครั้งใน 1-2 นาทีครับ"
    )

@app.post("/api/v1/forms/generate")
async def generate_form(request: Request, file: UploadFile | None = File(None)):
    try:
        body = await parse_request_body(request)
        input_type = str(body.get("input_type", "text_prompt")).lower()
        
        # Map frontend values to backend values if they differ
        mapping = {
            "voice_instruction": "voice",
            "markdown_document": "markdown",
            "legacy_spreadsheet": "spreadsheet",
            "json_configuration": "json_config"
        }
        input_type = mapping.get(input_type, input_type)
        
        prompt = body.get("prompt") or body.get("text_prompt") or body.get("text") or ""
        
        image_bytes = None
        image_mime = "image/png"
        extracted_data = None
        audio_bytes = None
        audio_mime = None

        # แก้ปัญหา FastAPI parameter binding/stream โดยดึงไฟล์จาก body ที่แกะมาได้ หรือ parameter file
        uploaded_file = body.get("file") or file
        file_bytes = None
        
        if uploaded_file:
            if isinstance(uploaded_file, UploadFile):
                await uploaded_file.seek(0)
                file_bytes = await uploaded_file.read()
            elif hasattr(uploaded_file, "file"):
                file_bytes = uploaded_file.file.read()
            elif isinstance(uploaded_file, bytes):
                file_bytes = uploaded_file

        if input_type == "text_prompt":
            pass
        elif input_type in ["physical_paper", "handwritten_sketch", "ui_screenshot", "scanned_image"]:
            if not file_bytes:
                raise HTTPException(status_code=400, detail=f"กรุณาแนบไฟล์รูปภาพสำหรับประเภท {input_type} ด้วยครับ")
            image_bytes = file_bytes
            if uploaded_file and hasattr(uploaded_file, "content_type") and uploaded_file.content_type:
                image_mime = uploaded_file.content_type
            elif uploaded_file and hasattr(uploaded_file, "filename"):
                if str(uploaded_file.filename).lower().endswith(".pdf"):
                    image_mime = "application/pdf"
                elif str(uploaded_file.filename).lower().endswith(".jpg") or str(uploaded_file.filename).lower().endswith(".jpeg"):
                    image_mime = "image/jpeg"
                else:
                    image_mime = "image/png"
            else:
                image_mime = "image/png"
        elif input_type == "voice":
            if not file_bytes:
                raise HTTPException(status_code=400, detail="กรุณาแนบไฟล์เสียงสั่งการเข้ามาด้วยครับ")
            audio_bytes = file_bytes
            
            # กำหนด Audio Mime Type ให้ตรงกับไฟล์ที่อัปโหลด
            audio_mime = "audio/wav"  # Default fallback
            content_type = uploaded_file.content_type if hasattr(uploaded_file, "content_type") else None
            filename = uploaded_file.filename if hasattr(uploaded_file, "filename") else ""
            
            if content_type:
                audio_mime = content_type
            elif filename:
                ext = filename.lower()
                if ext.endswith(".mp3"):
                    audio_mime = "audio/mp3"
                elif ext.endswith(".m4a"):
                    audio_mime = "audio/m4a"
                elif ext.endswith(".wav"):
                    audio_mime = "audio/wav"
                elif ext.endswith(".mpeg"):
                    audio_mime = "audio/mpeg"
                elif ext.endswith(".ogg"):
                    audio_mime = "audio/ogg"
                elif ext.endswith(".aac"):
                    audio_mime = "audio/aac"
        elif input_type == "markdown":
            if not file_bytes:
                raise HTTPException(status_code=400, detail="กรุณาอัปโหลดไฟล์เอกสาร Markdown (.md) เข้ามาด้วยครับ")
            extracted_data = file_bytes.decode("utf-8", errors="ignore")
        elif input_type == "digital_pdf":
            if not file_bytes:
                raise HTTPException(status_code=400, detail="กรุณาแนบไฟล์เอกสาร Digital PDF เข้ามาด้วยครับ")
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                num_pages = len(reader.pages)
                # กรอง None ออก (บางหน้าใน pypdf อาจคืนค่า None แทน string)
                page_texts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:  # กรอง None และ empty string
                        page_texts.append(text)
                extracted_data = "\n\n".join(page_texts)
                
                if not extracted_data or not extracted_data.strip():
                    raise HTTPException(
                        status_code=400,
                        detail="ไม่สามารถดึงข้อความจาก PDF ได้ เนื่องจากเป็นไฟล์แบบ Scanned Image กรุณาเปลี่ยนไปใช้ฟังก์ชัน '10. Scanned Image' แทนครับ"
                    )
                
                # Truncate ถ้ายาวเกิน 80,000 ตัวอักษร เพื่อไม่เกิน Gemini token limit
                MAX_TEXT_LEN = 80000
                if len(extracted_data) > MAX_TEXT_LEN:
                    extracted_data = extracted_data[:MAX_TEXT_LEN] + f"\n\n[...ข้อความถูกตัดเพื่อความปลอดภัย เอกสารมี {num_pages} หน้า แสดงเพียง {MAX_TEXT_LEN:,} ตัวอักษรแรก...]"
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"ไม่สามารถสกัดข้อความจากเอกสาร PDF ได้: {str(e)}")
        elif input_type == "spreadsheet":
            if not file_bytes:
                raise HTTPException(status_code=400, detail="กรุณาแนบไฟล์ตาราง Excel หรือ CSV เข้ามาด้วยครับ")
            try:
                import pandas as pd
                filename = uploaded_file.filename if hasattr(uploaded_file, "filename") else ""
                if filename and filename.lower().endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(file_bytes), nrows=1)
                else:
                    df = pd.read_excel(io.BytesIO(file_bytes), nrows=1)
                extracted_data = ", ".join(df.columns.tolist())
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"ไม่สามารถอ่านข้อมูลหัวตารางสเปรดชีตได้: {str(e)}")
        elif input_type == "json_config":
            raw_schema = None
            if file_bytes:
                try:
                    raw_schema = json.loads(file_bytes.decode("utf-8", errors="ignore"))
                except json.JSONDecodeError:
                    pass
            
            if not raw_schema:
                raw_schema = body.get("schema") or prompt
                
            if isinstance(raw_schema, str):
                try:
                    raw_schema = json.loads(raw_schema)
                except json.JSONDecodeError:
                    extracted_data = raw_schema
            
            if isinstance(raw_schema, dict):
                try:
                    validated_form = validate_form_schema(raw_schema)
                    form_document = {
                        "title": validated_form.get("title", "Imported JSON Form"),
                        "description": validated_form.get("description", ""),
                        "theme_color": validated_form.get("theme_color", "#ffffff"),
                        "theme": validated_form.get("theme", {}),
                        "input_type_used": input_type,
                        "sections": validated_form["sections"], # 🛠️ เปลี่ยนเป็น sections
                        "created_at": datetime.datetime.now(datetime.timezone.utc),
                    }
                    inserted = await run_in_threadpool(forms_collection.insert_one, form_document)
                    form_document["id"] = str(inserted.inserted_id)
                    return JSONResponse({
                        "status": "success",
                        "reply": "วิเคราะห์และเปิดใช้งานฟอร์มจากระบบโครงสร้าง JSON Configuration เรียบร้อยแล้วครับ!",
                        "form": normalize_doc(form_document)
                    })
                except Exception as e:
                    if not extracted_data:
                        raise HTTPException(status_code=400, detail=f"โครงสร้าง JSON ผิดพลาด: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail=f"ไม่รู้จักประเภทข้อมูลเข้า (input_type) แบบ: {input_type}")

        ai_prompt = build_ai_prompt(input_type, prompt=prompt, extracted_data=extracted_data)
        
        try:
            ai_response = await call_ai_schema(
                ai_prompt, 
                image_bytes=image_bytes,
                image_mime=image_mime,
                audio_bytes=audio_bytes, 
                audio_mime=audio_mime
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

        reply_text = ai_response.get("reply", "สร้างฟอร์มตามเงื่อนไขที่กำหนดเสร็จสมบูรณ์แล้วครับ!")
        raw_form_data = ai_response.get("form")
        form_document = None

        if raw_form_data and isinstance(raw_form_data, dict):
            try:
                schema = validate_form_schema(raw_form_data)
                form_document = {
                    "title": schema.get("title", "Generated Form"),
                    "description": schema.get("description", ""),
                    "theme_color": schema.get("theme_color", "#ffffff"),
                    "theme": schema.get("theme", {}),
                    "input_type_used": input_type,
                    "sections": schema["sections"], # 🛠️ เปลี่ยนเป็น sections
                    "created_at": datetime.datetime.now(datetime.timezone.utc),
                }
                inserted = await run_in_threadpool(forms_collection.insert_one, form_document)
                form_document["id"] = str(inserted.inserted_id)
                form_document = normalize_doc(form_document)
            except ValueError as val_err:
                reply_text += f" (หมายเหตุระบบ: ฟอร์มที่ AI เจนเนอเรตมีข้อผิดพลาด: {str(val_err)})"
                # คืนค่า raw กลับไปให้ Frontend จัดการต่อเผื่อมันเป็นฟิลด์เดี่ยวๆ
                form_document = raw_form_data 

        return JSONResponse({
            "status": "success",
            "reply": reply_text,
            "form": form_document
        })

    except Exception as server_error:
        print("\n" + "="*60)
        print("🚨 [CRITICAL ERROR] เกิดข้อผิดพลาดฝั่ง Backend:")
        traceback.print_exc()
        print("="*60 + "\n")
        
        if isinstance(server_error, HTTPException):
            return JSONResponse(status_code=server_error.status_code, content={"detail": server_error.detail})
        return JSONResponse(status_code=500, content={"detail": f"Internal Server Error: {str(server_error)}"})

@app.post("/api/v1/forms/edit-schema")
async def edit_form_schema(request: Request):
    try:
        body = await parse_request_body(request)
        prompt = body.get("prompt", "")
        current_schema = body.get("current_schema")
        
        if not current_schema:
            raise HTTPException(status_code=400, detail="Missing current_schema in request body")
            
        system_instruction = (
            "You are an expert JSON form schema editor. "
            "You will be given the current JSON schema of a form and a user instruction to modify it. "
            "Return the FULL updated JSON schema (no markdown blocks, just raw JSON). "
            "Preserve all existing fields and structure unless the user explicitly asks to remove or change them. "
            "The schema must still conform to the expected format. "
            "LOGO RULE: If the user provides an image URL in their instruction and asks for it to be a logo, set the theme.logo_url to that URL. If they do NOT ask for a logo, strictly preserve the existing theme.logo_url and do NOT inject an empty placeholder or nullify it. "
            "MASTER DATA RULE: Whenever the user requests common data fields (like Provinces, Faculties, or Title Names), you MUST change the field type to 'master_data' and set a 'master_data_category' property to the corresponding value (e.g., 'provinces', 'faculties', 'title_names'). Do not default to text input for these fields."
        )
        
        contents = [
            f"User Instruction: {prompt}\n\nCurrent Schema:\n{json.dumps(current_schema, ensure_ascii=False)}"
        ]
        
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                response_mime_type="application/json",
            )
        )
        
        updated_schema = json.loads(response.text)
        updated_schema = validate_form_schema(updated_schema)
        
        return {"status": "success", "form": updated_schema}
        
    except Exception as e:
        print(f"Edit schema error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "mongo_uri": MONGO_URI, "gemini_model": GEMINI_MODEL, "gemini_key_present": bool(os.getenv("GEMINI_API_KEY"))}

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Generate a secure filename
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join("uploads", filename)
        
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"status": "success", "url": f"/api/v1/uploads/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@app.get("/api/v1/forms")
async def list_forms():
    def get_forms():
        return list(forms_collection.find().sort("created_at", -1))
    forms = await run_in_threadpool(get_forms)
    return {"status": "success", "forms": [normalize_doc(f) for f in forms]}

@app.get("/api/v1/master-data/{category}")
async def get_master_data(category: str):
    try:
        with open("master_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        if category in data:
            return {"status": "success", "data": data[category]}
        else:
            raise HTTPException(status_code=404, detail="Category not found in master data")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="master_data.json file is missing")

@app.get("/api/v1/forms/{form_id}")
async def get_form(form_id: str):
    try:
        object_id = ObjectId(form_id)
    except Exception:
        raise HTTPException(status_code=400, detail="รูปแบบ ID ของฟอร์มไม่ถูกต้อง")
    
    doc = await run_in_threadpool(forms_collection.find_one, {"_id": object_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="ไม่พบฟอร์มที่ค้นหา")
    return {"status": "success", "form": normalize_doc(doc)}

@app.delete("/api/v1/forms/{form_id}")
async def delete_form(form_id: str):
    try:
        object_id = ObjectId(form_id)
    except Exception:
        raise HTTPException(status_code=400, detail="รูปแบบ ID ของฟอร์มไม่ถูกต้อง")
    
    result = await run_in_threadpool(forms_collection.delete_one, {"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="ไม่พบฟอร์มที่ต้องการลบ")
    
    # ลบข้อมูล submissions
    await run_in_threadpool(submissions_collection.delete_many, {"form_id": form_id})
    await run_in_threadpool(responses_collection.delete_many, {"form_id": form_id})
    return {"status": "success", "message": "ลบฟอร์มและข้อมูลที่เกี่ยวข้องเรียบร้อยแล้ว"}

@app.post("/api/v1/forms")
async def create_form(request: Request):
    body = await request.json()
    if not body:
        raise HTTPException(status_code=400, detail="ไม่พบข้อมูลสำหรับการสร้างฟอร์ม")
        
    try:
        schema = validate_form_schema(body)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=f"โครงสร้างฟอร์มไม่ถูกต้อง: {str(val_err)}")
        
    new_form = {
        "title": schema.get("title", "Generated Form"),
        "description": schema.get("description", ""),
        "theme_color": schema.get("theme_color", "#ffffff"),
        "theme": schema.get("theme", {}),
        "input_type_used": body.get("input_type_used", "manual"),
        "sections": schema["sections"],
        "created_at": datetime.datetime.now(datetime.timezone.utc),
    }
    
    if "theme" in body and isinstance(body["theme"], dict):
        new_form["theme"] = body["theme"]
        
    inserted = await run_in_threadpool(forms_collection.insert_one, new_form)
    new_form["id"] = str(inserted.inserted_id)
    return {"status": "success", "message": "สร้างฟอร์มสำเร็จ", "form": normalize_doc(new_form)}

@app.put("/api/v1/forms/{form_id}")
async def update_form(form_id: str, request: Request):
    try:
        object_id = ObjectId(form_id)
    except Exception:
        raise HTTPException(status_code=400, detail="รูปแบบ ID ของฟอร์มไม่ถูกต้อง")
    
    body = await request.json()
    if not body:
        raise HTTPException(status_code=400, detail="ไม่พบข้อมูลสำหรับการแก้ไข")
        
    try:
        schema = validate_form_schema(body)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=f"โครงสร้างฟอร์มไม่ถูกต้อง: {str(val_err)}")
        
    updated_fields = {
        "title": schema.get("title", "Generated Form"),
        "description": schema.get("description", ""),
        "theme_color": schema.get("theme_color", "#ffffff"),
        "sections": schema["sections"],
    }
    
    # Persist AI Theme object if present
    if "theme" in body and isinstance(body["theme"], dict):
        updated_fields["theme"] = body["theme"]
    
    result = await run_in_threadpool(
        forms_collection.update_one,
        {"_id": object_id},
        {"$set": updated_fields}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="ไม่พบฟอร์มที่ต้องการอัปเดต")
        
    doc = await run_in_threadpool(forms_collection.find_one, {"_id": object_id})
    return {"status": "success", "form": normalize_doc(doc)}

# ==========================================
# 🎨 AI Theme Engine Endpoint (Gemini 2.0 Flash — Optimized)
# ==========================================
@app.post("/api/v1/ai/theme")
async def generate_theme(request: Request):
    import asyncio
    
    try:
        body = await request.json()
        prompt = body.get("prompt", "")
        
        if not prompt or not prompt.strip():
            raise HTTPException(status_code=400, detail="กรุณาระบุคำสั่งสไตล์ธีมที่ต้องการ เช่น 'ธีม Dark Mode สไตล์ Cyberpunk'")
        
        theme_system_instruction = (
            "You are a UI Theme Designer AI.\n"
            "The user will describe a visual theme they want for their form. "
            "Your task is to generate a harmonious, visually appealing color palette as a JSON object.\n\n"
            "CRITICAL CONTRAST GUARDRAIL: You MUST ensure that text colors always have sufficient contrast "
            "against their respective background colors. Text must always be readable — never generate "
            "color combinations where text blends into or is too similar to the background. "
            "Follow WCAG AA guidelines (minimum contrast ratio 4.5:1 for normal text).\n\n"
            "Return ONLY a valid JSON object with these exact keys:\n"
            "{\n"
            "  \"theme_color\": \"#hex — primary accent color\",\n"
            "  \"bg_color\": \"#hex — page/app background color\",\n"
            "  \"card_bg\": \"#hex — card/section background color\",\n"
            "  \"text_color\": \"#hex — primary text color (MUST contrast with card_bg)\",\n"
            "  \"border_color\": \"#hex — border/divider color\",\n"
            "  \"input_bg\": \"#hex — input field background\",\n"
            "  \"input_text\": \"#hex — input text color (MUST contrast with input_bg)\",\n"
            "  \"border_radius\": \"Npx — border radius value (e.g. 8px, 12px, 16px)\",\n"
            "  \"label_color\": \"#hex — label text color (MUST contrast with card_bg)\"\n"
            "}\n\n"
            "Do not include markdown block ticks. Only return the raw JSON object."
        )
        
        # 🚀 Model: ใช้โมเดลตระกูล Gemini 2.5 ตัวเดียวกับระบบหลักเพื่อเลี่ยงปัญหา Quota
        THEME_MODEL = GEMINI_MODEL
        
        config = types.GenerateContentConfig(
            system_instruction=theme_system_instruction,
            response_mime_type="application/json",
        )
        
        MAX_RETRIES = 3
        RETRY_DELAYS = [3, 6, 12]
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            try:
                print(f"🎨 Theme AI request: model={THEME_MODEL}, attempt={attempt + 1}/{MAX_RETRIES}, prompt='{prompt[:80]}'")
                response = await run_in_threadpool(
                    client.models.generate_content,
                    model=THEME_MODEL,
                    contents=[f"สร้างธีมสีตามคำอธิบายนี้: {prompt}"],
                    config=config,
                )
                raw_content = response.text
                
                if not raw_content:
                    raise ValueError("AI ไม่ได้ตอบกลับมาเป็นข้อความ")
                
                raw_content = raw_content.strip()
                theme_data = json.loads(raw_content)
                
                # Validate required keys
                required_keys = ["theme_color", "bg_color", "card_bg", "text_color"]
                for key in required_keys:
                    if key not in theme_data:
                        raise ValueError(f"Missing required key: {key}")
                
                print(f"✅ Theme generated successfully: {theme_data}")
                return JSONResponse({
                    "status": "success",
                    "theme": theme_data
                })
                
            except (json.JSONDecodeError, ValueError) as parse_err:
                last_error = parse_err
                print(f"⚠️ Theme parse error: {parse_err}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAYS[attempt])
                    continue
                raise HTTPException(status_code=500, detail=f"AI สร้างธีมไม่สำเร็จ: {str(parse_err)}")
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                is_rate_limit = "429" in str(e) or "resource_exhausted" in error_str or "too many requests" in error_str
                is_retriable = is_rate_limit or "503" in str(e) or "overloaded" in error_str
                
                if is_retriable and attempt < MAX_RETRIES - 1:
                    wait_sec = RETRY_DELAYS[attempt]
                    print(f"⏳ Theme API rate-limited — รอ {wait_sec}s แล้ว retry...")
                    await asyncio.sleep(wait_sec)
                    continue
                
                if is_rate_limit:
                    raise HTTPException(status_code=429, detail="QUOTA_EXCEEDED")
                raise HTTPException(status_code=500, detail=f"เรียก Gemini Theme AI ล้มเหลว: {str(e)}")
        
        last_error_str = str(last_error).lower()
        if "429" in last_error_str or "resource_exhausted" in last_error_str or "too many requests" in last_error_str:
            raise HTTPException(status_code=429, detail="QUOTA_EXCEEDED")
        raise HTTPException(status_code=500, detail=f"Theme AI ล้มเหลวหลังจากลอง {MAX_RETRIES} ครั้ง: {str(last_error)}")
    
    except HTTPException:
        raise
    except Exception as server_error:
        print(f"🚨 Theme endpoint error: {server_error}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(server_error)}")


@app.post("/api/v1/submit/{form_id}")
async def submit_form(form_id: str, request: Request):
    body = await parse_request_body(request)
    if not body:
        raise HTTPException(status_code=400, detail="ไม่พบข้อมูลสำหรับการส่งบันทึก")

    respondent_info = body.pop("respondent_info", {})
    answers = {}

    for key, value in body.items():
        if isinstance(value, UploadFile):
            file_data = await value.read()
            answers[key] = file_data.decode("utf-8", errors="ignore")
        else:
            answers[key] = value

    response_data = ResponseSubmission(
        form_id=form_id,
        answers=answers,
        respondent_info=respondent_info
    )

    inserted = await run_in_threadpool(responses_collection.insert_one, response_data.model_dump() if hasattr(response_data, 'model_dump') else response_data.dict())
    response_doc = response_data.model_dump() if hasattr(response_data, 'model_dump') else response_data.dict()
    response_doc["id"] = str(inserted.inserted_id)
    return {"status": "success", "submission": normalize_doc(response_doc)}

@app.get("/api/v1/forms/{form_id}/responses")
async def get_form_responses(form_id: str):
    try:
        def fetch_responses():
            cursor = responses_collection.find({"form_id": form_id}).sort("created_at", -1)
            return list(cursor)
        
        responses = await run_in_threadpool(fetch_responses)
        # normalize_doc รับเฉพาะ dict — ต้อง map ทีละ document
        return {"status": "success", "data": [normalize_doc(r) for r in responses]}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/responses/all")
async def get_all_responses():
    try:
        def fetch_all():
            responses = list(responses_collection.find().sort("created_at", -1))
            all_forms = list(forms_collection.find({}, {"_id": 1, "title": 1, "_aid": 1}))
            form_map = {str(f["_id"]): f.get("title", "Unknown Form") for f in all_forms}
            # Add _aid fallback mapping just in case
            for f in all_forms:
                if f.get("_aid"):
                    form_map[f["_aid"]] = f.get("title", "Unknown Form")
            for r in responses:
                r["form_title"] = form_map.get(str(r.get("form_id")), "Unknown Form")
            return responses
            
        responses = await run_in_threadpool(fetch_all)
        # normalize_doc รับเฉพาะ dict — ต้อง map ทีละ document
        return {"status": "success", "data": [normalize_doc(r) for r in responses]}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/responses/export-excel")
async def export_responses_excel(form_id: str = None):
    try:
        def fetch_export_data():
            query = {}
            if form_id and form_id != "all":
                query["form_id"] = form_id
            
            responses = list(responses_collection.find(query).sort("created_at", -1))
            all_forms = list(forms_collection.find({}, {"_id": 1, "title": 1, "_aid": 1}))
            form_map = {str(f["_id"]): f.get("title", "Unknown Form") for f in all_forms}
            for f in all_forms:
                if f.get("_aid"):
                    form_map[f["_aid"]] = f.get("title", "Unknown Form")
                    
            export_list = []
            for r in responses:
                row = {
                    "Form Title": form_map.get(str(r.get("form_id")), "Unknown Form"),
                    "Form ID": str(r.get("form_id", "")),
                    "Submission Date": r.get("created_at", "").replace(tzinfo=None) if hasattr(r.get("created_at"), 'replace') else str(r.get("created_at", "")),
                    "Respondent Email": r.get("respondent_info", {}).get("email") if isinstance(r.get("respondent_info"), dict) else r.get("respondent_info", "Anonymous")
                }
                answers = r.get("answers", {})
                for k, v in answers.items():
                    if isinstance(v, list):
                        row[k] = ", ".join(map(str, v))
                    else:
                        row[k] = str(v)
                export_list.append(row)
            return export_list
            
        data_list = await run_in_threadpool(fetch_export_data)
        
        if not data_list:
            raise HTTPException(status_code=404, detail="No responses found to export")
            
        df = pd.DataFrame(data_list)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Responses")
        
        output.seek(0)
        headers = {
            'Content-Disposition': 'attachment; filename="responses_export.xlsx"'
        }
        return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
# ==========================================
# API Phase 3: Form Templates Library
# ==========================================

@app.post("/api/v1/templates")
async def save_template(body: dict = Body(...)):
    if "sections" not in body:
        raise HTTPException(status_code=400, detail="Invalid template format: Missing sections")
    
    template_doc = {
        "title": body.get("title", "Untitled Template"),
        "description": body.get("description", ""),
        "theme_color": body.get("theme_color", "#ffffff"),
        "theme": body.get("theme", {}),
        "sections": body["sections"],
        "created_at": datetime.datetime.now(datetime.timezone.utc)
    }
    inserted = await run_in_threadpool(templates_collection.insert_one, template_doc)
    template_doc["id"] = str(inserted.inserted_id)
    return {"status": "success", "template": normalize_doc(template_doc)}

@app.get("/api/v1/templates")
async def list_templates():
    def get_templates():
        return list(templates_collection.find().sort("created_at", -1))
    templates = await run_in_threadpool(get_templates)
    return {"status": "success", "templates": [normalize_doc(t) for t in templates]}

@app.delete("/api/v1/templates/{template_id}")
async def delete_template(template_id: str):
    try:
        object_id = ObjectId(template_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid Template ID")
    result = await run_in_threadpool(templates_collection.delete_one, {"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"status": "success", "message": "Template deleted"}

