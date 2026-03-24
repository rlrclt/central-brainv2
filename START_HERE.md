# 🚀 START HERE — Central Brain AI System

## 📌 คุณติดตั้งได้อะไรแล้วบ้าง?

### ✅ ที่ทำแล้ว:
1. **Copilot Instructions** (`.github/copilot-instructions.md`)
2. **API Integration Hub** (`brain_hub.py`)
3. **Config Management** (`config.py`)
4. **Example Scripts** (Claude, GPT-4, Multi-AI)
5. **Testing Suite** (`test_full.py`)
6. **Documentation** (Thai language)

---

## 🎯 ทดสอบให้เห็นผล (2 นาที)

### Terminal 1: เปิดตัวนี้
```bash
python3 test_full.py
```

**ผลที่เห็น:**
```
✅ Python Imports
⚠️  Server Connection (ยังไม่รัน)
✅ Configuration
✅ BrainHub Integration

Result: 3/4 passed
```

→ **ถ้าเห็นแบบนี้ = ตัดตั้งถูก!** ✅

---

## 📖 ดูเพิ่มเติม

| ไฟล์ | สำหรับ |
|------|-------|
| `QUICK_START.md` | 3 ขั้นตอนรวดเร็ว |
| `AI_INTEGRATION_GUIDE.md` | คู่มือละเอียด |
| `TESTING_CHECKLIST.md` | ขั้นตอนทดสอบ |
| `.github/copilot-instructions.md` | Copilot notes |

---

## 🔑 ถ้ามี API Keys

### Step 1: ตั้งค่า .env
```bash
cp .env.example .env
nano .env
# เติม ANTHROPIC_API_KEY หรือ OPENAI_API_KEY
```

### Step 2: รัน Server
```bash
bash start.sh
# Terminal 1 ไว้รัน นี่
```

### Step 3: ใช้ BrainHub
```python
# my_script.py
from brain_hub import BrainHub

hub = BrainHub("claude", "my-project")
answer = hub.ask_claude("ช่วยเขียนโค้ด")
print(answer)
```

### Step 4: รัน
```bash
# Terminal 2 ต่างหาก
python3 my_script.py
```

---

## ✨ สิ่งที่คุณมี

- ✅ **API Server** — Central Brain (port 7799)
- ✅ **Config System** — Manage API keys safely
- ✅ **Integration Hub** — BrainHub (Claude, GPT-4)
- ✅ **Examples** — Ready-to-run scripts
- ✅ **Tests** — Verify everything works
- ✅ **Docs** — Thai language

---

## ⚡ ต้องการ Quick Test?

ลองรัน:
```bash
python3 test_full.py
```

ได้ผลดีสุด = ทุกอย่างพร้อมแล้ว! 🎉
