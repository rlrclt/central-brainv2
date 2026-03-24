# 🧠 Central Brain API

สมองกลางสำหรับ AI ทุกตัว — รันบน Linux, เก็บข้อมูลใน SQLite local

---

## ⚡ วิธีติดตั้งและรัน

```bash
# 1. คัดลอกโฟลเดอร์ไปวางบนเครื่อง
cp -r central-brain/ /opt/central-brain/

# 2. ติดตั้ง dependencies
cd /opt/central-brain
pip3 install -r requirements.txt

# 3. รัน
bash start.sh
```

API พร้อมใช้ที่ `http://localhost:7799`
Swagger docs ที่ `http://localhost:7799/docs`

---

## 🔁 Auto-start เมื่อเปิดเครื่อง (systemd)

```bash
sudo cp central-brain.service /etc/systemd/system/central-brain@.service
sudo systemctl enable central-brain@$(whoami)
sudo systemctl start central-brain@$(whoami)
```

---

## 📡 API Endpoints

| Method | Path | ความหมาย |
|--------|------|-----------|
| POST | `/sessions` | สร้าง session ใหม่ |
| GET | `/sessions` | ดู sessions ทั้งหมด |
| GET | `/sessions/{id}` | ดู session + messages |
| DELETE | `/sessions/{id}` | ลบ session |
| POST | `/messages` | เพิ่ม message (auto-compress) |
| GET | `/messages/{session_id}` | ดึง messages |
| POST | `/memory` | เซ็ต memory key-value |
| GET | `/memory` | ดึง memory ทั้งหมด |
| GET | `/memory/{key}` | ดึง memory key เดียว |
| DELETE | `/memory/{key}` | ลบ memory key |
| GET | `/context/{session_id}` | ดึง context พร้อมใช้งาน |
| POST | `/compress` | บันทึก summary แทน messages เก่า |

---

## 🔧 การตั้งค่า Auto-compress

ใน `app/main.py` บรรทัดต้น:

```python
MAX_MESSAGES_BEFORE_COMPRESS = 50   # compress อัตโนมัติเมื่อมากกว่านี้
KEEP_RECENT_MESSAGES = 10           # เก็บ message ล่าสุดไว้กี่อัน
```

---

## 🤖 วิธีใช้กับ AI ต่างๆ

### Pattern พื้นฐาน (ทุก AI ใช้เหมือนกัน)

```python
# 1. เริ่ม session
POST /sessions  →  ได้ session_id

# 2. ก่อนส่ง prompt ให้ AI
GET /context/{session_id}  →  ได้ context_block
  → ใส่ context_block ใน system prompt

# 3. หลัง AI ตอบ
POST /messages  →  บันทึก user message
POST /messages  →  บันทึก assistant response
```

### ดู example_usage.py สำหรับ code ตัวอย่าง

---

## 📁 โครงสร้างไฟล์

```
central-brain/
├── app/
│   └── main.py          # API server
├── data/
│   └── brain.db         # SQLite database (สร้างอัตโนมัติ)
├── requirements.txt
├── start.sh
├── central-brain.service
├── example_usage.py
└── README.md
```
