"""
ตัวอย่างการใช้งาน Central Brain API กับ AI ต่างๆ
"""
import requests

BASE = "http://localhost:7799"

# ═══════════════════════════════════════
# 1. สร้าง session ใหม่
# ═══════════════════════════════════════
def new_session(ai_agent: str, project: str = "default", title: str = None):
    r = requests.post(f"{BASE}/sessions", json={
        "ai_agent": ai_agent,
        "project": project,
        "title": title
    })
    return r.json()["session_id"]

# ═══════════════════════════════════════
# 2. บันทึก message
# ═══════════════════════════════════════
def save_message(session_id: str, role: str, content: str):
    return requests.post(f"{BASE}/messages", json={
        "session_id": session_id,
        "role": role,
        "content": content
    }).json()

# ═══════════════════════════════════════
# 3. ดึง context พร้อม inject ใน prompt
# ═══════════════════════════════════════
def get_context(session_id: str) -> str:
    r = requests.get(f"{BASE}/context/{session_id}")
    return r.json()["context_block"]

# ═══════════════════════════════════════
# 4. เซ็ต memory ที่ใช้ร่วมกันทุก AI
# ═══════════════════════════════════════
def set_memory(key: str, value: str, scope: str = "global"):
    return requests.post(f"{BASE}/memory", json={
        "key": key,
        "value": value,
        "scope": scope,
        "ai_agent": "all"
    }).json()

# ═══════════════════════════════════════
# ตัวอย่าง workflow จริง
# ═══════════════════════════════════════
if __name__ == "__main__":

    # สร้าง session สำหรับ Claude
    sid = new_session("claude", project="my-project", title="งาน backend API")
    print(f"Session: {sid}")

    # เก็บ memory ที่ AI ทุกตัวควรรู้
    set_memory("user_name", "เจ้าของระบบ")
    set_memory("project_goal", "สร้าง central brain ให้ AI ทุกตัว")
    set_memory("language", "Thai preferred")

    # บันทึก conversation
    save_message(sid, "user", "ช่วยเขียน FastAPI endpoint ให้หน่อย")
    save_message(sid, "assistant", "ได้เลยครับ นี่คือ code...")

    # ดึง context ก่อนส่งให้ AI ตัวต่อไป
    ctx = get_context(sid)
    print("\n=== Context Block ===")
    print(ctx)

    # ═══════════════════════════════════
    # ตัวอย่างกับ OpenAI
    # ═══════════════════════════════════
    # import openai
    # ctx = get_context(sid)
    # response = openai.chat.completions.create(
    #     model="gpt-4",
    #     messages=[
    #         {"role": "system", "content": f"You have access to this memory:\n{ctx}"},
    #         {"role": "user", "content": "สรุปสิ่งที่คุยกันมา"}
    #     ]
    # )
    # save_message(sid, "assistant", response.choices[0].message.content)

    # ═══════════════════════════════════
    # ตัวอย่างกับ Gemini
    # ═══════════════════════════════════
    # import google.generativeai as genai
    # ctx = get_context(sid)
    # model = genai.GenerativeModel('gemini-pro')
    # result = model.generate_content(f"Context:\n{ctx}\n\nUser: สรุปสิ่งที่คุยกัน")
    # save_message(sid, "assistant", result.text)
