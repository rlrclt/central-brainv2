# 🚀 Quick Start — Central Brain AI Integration

## 📋 สรุปสั้น

ระบบสมองกลางของคุณตอนนี้พร้อมเชื่อม AI แล้ว!

---

## ⚡ 3 ขั้นตอนเริ่มต้น

### 1️⃣ สร้าง `.env` ใส่ API Keys
```bash
cp .env.example .env
nano .env  # แก้ไขใส่ API keys
```

### 2️⃣ รัน Central Brain Server (Terminal 1)
```bash
bash start.sh
# ✅ http://localhost:7799
```

### 3️⃣ เขียน Script ใช้ BrainHub (Terminal 2)
```python
from brain_hub import BrainHub

hub = BrainHub("claude", "my-project")
answer = hub.ask_claude("ช่วยเขียนโค้ด Python")
print(answer)
```

---

## 📚 File สำคัญ

| File | ทำหน้าที่ |
|------|---------|
| `brain_hub.py` | ตัวเชื่อมหลัก — ใช้นี่เลย ⭐ |
| `config.py` | อ่าน .env และเช็ค API keys |
| `.env.example` | Template API keys |
| `AI_INTEGRATION_GUIDE.md` | คู่มือเต็มๆ |
| `test_setup.py` | ทดสอบว่าติดตั้งถูก |

---

## 💡 ตัวอย่าง Script

### Claude
```python
from brain_hub import BrainHub

hub = BrainHub("claude", "project-name")
hub.set_memory("goal", "เขียน code review")

answer = hub.ask_claude("ช่วยเขียน code review สำหรับ function นี้")
print(answer)
```

### GPT-4
```python
from brain_hub import BrainHub

hub = BrainHub("gpt4", "project-name")
answer = hub.ask_gpt("อธิบาย API design patterns")
print(answer)
```

### หลาย AI คุยกัน (ใช้ session เดียวกัน)
```python
from brain_hub import BrainHub

claude = BrainHub("claude", "debate-project")
gpt = BrainHub("gpt4", "debate-project")

claude.set_memory("topic", "Python vs JavaScript")

claude_view = claude.ask_claude("Python ดีตรงไหน?")
gpt_view = gpt.ask_gpt("JavaScript ดีตรงไหน?")

print(f"Claude: {claude_view}")
print(f"GPT: {gpt_view}")
```

---

## 🔍 ตรวจสอบการตั้งค่า

```bash
python3 test_setup.py
```

ควรเห็น:
```
✅ config.py loaded
✅ brain_hub.py loaded
✅ Setup OK!
```

---

## 🎯 ว่างๆ แล้ว?

ที่นี่หาอ่านเพิ่มเติม:
- `AI_INTEGRATION_GUIDE.md` - คู่มือเต็มๆ
- `.github/copilot-instructions.md` - สำหรับ Copilot sessions

---

## ⚠️ ถ้ามีปัญหา

### Error: Module not found
```bash
/Library/Developer/CommandLineTools/usr/bin/python3 -m pip install -r requirements.txt
```

### Error: API key not found
```bash
cp .env.example .env
# เติม API keys ลงใน .env
```

### Error: Connection refused (port 7799)
```bash
# ขาดเซิร์ฟเวอร์ — รัน Terminal 1:
bash start.sh
```

---

**ลองดู!** 🚀
