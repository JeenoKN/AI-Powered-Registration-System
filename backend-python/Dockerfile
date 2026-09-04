FROM python:3.10-slim

WORKDIR /app

# คัดลอกไฟล์ requirements และติดตั้ง Library
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดหลังบ้านทั้งหมด
COPY . .

EXPOSE 8000

# สั่งรัน FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]