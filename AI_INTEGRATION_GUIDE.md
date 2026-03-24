# 🧠 วิธีใช้ Central Brain กับ AI ต่างๆ

## 🚀 ขั้นตอนที่ 1: ตั้งค่า API Keys

### 1. สร้าง `.env` file
```bash
cp .env.example .env
```

### 2. เติม API Keys ของคุณ
```bash
nano .env
```

```
ANTHROPIC_API_KEY=sk-ant-xxxxx       # ดาวน์โหลดจาก https://console.anthropic.com
OPENAI_API_KEY=sk-xxxxx              # ดาวน์โหลดจาก https://platform.openai.com
GOOGLE_API_KEY=xxxxx                 # ดาวน์โหลดจาก https://aistudio.google.com
CENTRAL_BRAIN_URL=http://localhost:7799
```

---

## 🎯 ขั้นตอนที่ 2: ใช้ BrainHub (ตัวเชื่อมหลัก)

### วิธีใช้ที่ 1: ถาม Claude
```python
from brain_hub import BrainHub

# สร้าง hub สำหรับ Claude
hub = BrainHub("claude", "my-project")

# เซ็ต shared memory
hub.set_memory("user_name", "ชื่อผู้ใช้")
hub.set_memory("goal", "สร้าง AI system")

# ถาม Claude
answer = hub.ask_claude("ช่วยเขียนโค้ด Python หน่อย")
print(answer)
```

### วิธีใช้ที่ 2: ถาม GPT-4
```python
from brain_hub import BrainHub

hub = BrainHub("gpt4", "my-project")
answer = hub.ask_gpt("อธิบายว่า API คืออะไร")
print(answer)
```

### วิธีใช้ที่ 3: ใช้ AI หลายตัว (เห็นกันหมด)
```python
from brain_hub import BrainHub

# สร้าง hub สำหรับ Claude (session เดียวกัน)
claude = BrainHub("claude", "debate-project")
gpt = BrainHub("gpt4", "debate-project")

# เซ็ต shared memory (ทั้ง 2 เห็น)
claude.set_memory("topic", "Python vs Node.js")

# Claude ตอบ
claude_view = claude.ask_claude("ให้ความเห็นเกี่ยวกับ Python")

# GPT ตอบ (เห็นสิ่งที่ Claude ตอบแล้ว)
gpt_view = gpt.ask_gpt("ให้ความเห็นเกี่ยวกับ Node.js")

print(f"Claude: {claude_view}")
print(f"GPT: {gpt_view}")
```

---

## 💻 ขั้นตอนที่ 3: วิธีการรัน

### Terminal ที่ 1: รัน Central Brain Server
```bash
bash start.sh
# ✅ Server รันที่ http://localhost:7799
```

### Terminal ที่ 2: รันโปรแกรม AI
```bash
python3 brain_hub.py
# หรือสร้างโปรแกรมของคุณเอง ที่ใช้ BrainHub
```

---

## 🤖 Copilot (ตัวเอง) เป็น Agent

ถ้าต้องการให้ Copilot เป็น agent ตัวหนึ่งในระบบ:

```python
from brain_hub import BrainHub

# Copilot เป็น agent ตัวหนึ่ง
copilot_hub = BrainHub("copilot", "copilot-project")

# บันทึกว่า Copilot กำลังช่วยอะไร
copilot_hub.set_memory("copilot_task", "Reviewing code changes")

# บันทึก action ของ Copilot
copilot_hub.save_message("ai:copilot", "Found 2 issues in file.py")

# AI อื่นเห็น
```

---

## 📋 Configuration (config.py)

ไฟล์ `config.py` อ่าน .env และเช็คว่า API keys ครบ:

```python
python3 config.py
# ✅ API keys ครบ
# 🧠 Central Brain: http://localhost:7799
# 🤖 Copilot: Enabled
```

---

## 🔐 Security Notes

- ✅ API keys เก็บใน `.env` (ไม่ commit ลงในตัวระบบ)
- ✅ ใช้ `from config import Config` ไม่ต้องกังวล
- ✅ BrainHub ซ่อน API keys ไม่ให้ client code เห็น

---

## 🚀 ตัวอย่าง Script

สร้างไฟล์ `my_app.py`:

```python
from brain_hub import BrainHub
from config import Config

# ตรวจว่า API keys ครบ
if not Config.validate():
    exit(1)

# สร้าง hub
hub = BrainHub("claude", "my-project")

# เซ็ต memory
hub.set_memory("task", "Writing code review")
hub.set_memory("language", "Thai")

# ถาม Claude
print("\n🤖 Claude ช่วยเขียน code review:\n")
answer = hub.ask_claude("""
ช่วยเขียน code review สำหรับ:
```python
def add(a, b):
    return a + b
```
""")
print(answer)

# บันทึก feedback
hub.save_message("user", "ขอบคุณ")
```

รัน:
```bash
python3 my_app.py
```

---

## ✅ สรุป

| ขั้นตอน | คำสั่ง | หมายเหตุ |
|--------|--------|---------|
| 1. ตั้ง keys | `cp .env.example .env` | เติม API keys |
| 2. โหลด config | `from config import Config` | ตรวจ keys |
| 3. สร้าง hub | `hub = BrainHub("claude", "project")` | ใช้ API keys โดยปลอดภัย |
| 4. รัน server | `bash start.sh` | Terminal 1 |
| 5. รันโปรแกรม | `python3 my_app.py` | Terminal 2 |

---

## 🎯 Copilot ใช้งานไงหรือ?

Copilot (ตัวที่รัน CLI นี้) สามารถ:
- ✅ อ่านไฟล์ `brain_hub.py`
- ✅ ช่วยแก้ code
- ✅ อธิบาย API

แต่ Copilot ไม่เชื่อมกับ Central Brain โดยอัตโนมัติ ต้องให้คุณเขียน code ที่เรียก `BrainHub` เอง

ถ้าต้องการให้ Copilot เป็น agent ตัวหนึ่ง ต้องเขียน `/slash-command` หรือ `script` ที่ใช้ BrainHub
