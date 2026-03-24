# 🧪 Testing Checklist — Central Brain

## ⚡ ทดสอบเร็ว (5 นาที)

### Step 1: ตรวจการติดตั้ง
```bash
python3 test_full.py
```

**ผลที่คาดหวัง:**
```
✅ Python Imports
⚠️  Server Connection (ยังไม่รัน server)
✅ Configuration
✅ BrainHub Integration

Result: 3/4 passed
```

---

### Step 2: รัน Server (Terminal 1)
```bash
bash start.sh
```

**ผลที่คาดหวัง:**
```
✅ Running at http://localhost:7799
📖 Docs at  http://localhost:7799/docs
```

---

### Step 3: ทดสอบการเชื่อม (Terminal 2)
```bash
python3 test_full.py
```

**ผลที่คาดหวัง:**
```
✅ Python Imports
✅ Server Connection
✅ Configuration
✅ BrainHub Integration

Result: 4/4 passed
```

---

## 🎯 ทดสอบเต็มรูป (15 นาที)

### Step 1-3: ทำตามด้านบน ✅

### Step 4: ตั้งค่า .env (ถ้ามี API Keys)
```bash
cp .env.example .env
nano .env
```

เติม:
- `ANTHROPIC_API_KEY=sk-ant-xxxxx` (ถ้ามี Claude)
- `OPENAI_API_KEY=sk-xxxxx` (ถ้ามี GPT)

### Step 5: ทดสอบ Claude
```bash
python3 claude_integration.py
```

**ผลที่คาดหวัง:**
```
✅ Session ID: a1b2c3d4e5f6
📝 Q1: ช่วยเขียนฟังก์ชัน Python...
✅ Claude: def reverse_string(s: str)...
```

### Step 6: ทดสอบ GPT (ถ้ามี key)
```bash
python3 gpt_integration.py
```

### Step 7: ทดสอบ Multi-AI (ถ้ามี key สองตัว)
```bash
python3 multi_ai.py
```

---

## ✅ Checklist ก่อนทดสอบ

- [ ] ติดตั้ง dependencies: `pip3 install -r requirements.txt`
- [ ] รัน test import: `python3 test_setup.py`
- [ ] ดูไฟล์:
  - [ ] `brain_hub.py` (ตัวเชื่อมหลัก)
  - [ ] `config.py` (ตั้งค่า)
  - [ ] `.env.example` (template)
  - [ ] `QUICK_START.md` (คู่มือ)

---

## ⚠️ Troubleshooting

### Error: Module not found
```bash
pip3 install -r requirements.txt
```

### Error: Cannot connect to localhost:7799
```bash
# Terminal 1:
bash start.sh
```

### Error: API key not found
```bash
# ถ้าต้องการใช้ AI:
cp .env.example .env
nano .env
# เติม ANTHROPIC_API_KEY หรือ OPENAI_API_KEY
```

### Error: Connection refused
```bash
# ตรวจว่า server รันไหม:
curl http://localhost:7799/
# ควรเห็น: {"message":"Health check"}
```

---

## 🎯 ผลการทดสอบสำเร็จ

ถ้า `test_full.py` ให้ผลดังนี้:
```
✅ Python Imports
✅ Server Connection
✅ Configuration
✅ BrainHub Integration

Result: 4/4 passed
```

**แสดงว่า:**
- ✅ ติดตั้ง dependencies OK
- ✅ Server เชื่อมได้
- ✅ Config ตั้งค่าถูก
- ✅ BrainHub พร้อมใช้

**ตอนนี้พร้อมเชื่อม AI แล้ว!** 🚀

---

## 📚 ไฟล์เพื่อการทดสอบ

| ไฟล์ | ทำหน้าที่ |
|------|---------|
| `test_setup.py` | ตรวจสิ่ง install (เร็ว) |
| `test_full.py` | ทดสอบทั้งหมด (รวม server) |
| `claude_integration.py` | ตัวอย่าง: Claude |
| `gpt_integration.py` | ตัวอย่าง: GPT-4 |
| `multi_ai.py` | ตัวอย่าง: Multi-AI debate |

---

## 🚀 Ready?

ลองรัน:
```bash
python3 test_full.py
```

ได้เลย! 🎉
