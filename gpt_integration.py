"""
เชื่อม GPT-4 กับ Central Brain API
ใช้วิธีเดียวกับ Claude — ดึง context แล้วให้ GPT ตอบ
"""
import requests
import os

BASE = "http://localhost:7799"

class GPTBrain:
    def __init__(self, session_id: str = None, model: str = "gpt-4"):
        try:
            import openai
        except ImportError:
            print("⚠️  ต้องติดตั้ง: pip install openai")
            return
        
        self.model = model
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # สร้าง session ใหม่ถ้าไม่มี
        if not session_id:
            resp = requests.post(f"{BASE}/sessions", json={
                "ai_agent": "gpt4",
                "project": "default",
                "title": "GPT-4 Session"
            })
            self.session_id = resp.json()["session_id"]
        else:
            self.session_id = session_id
            
        print(f"✅ Session ID: {self.session_id} (Model: {model})")
    
    def think(self, user_input: str) -> str:
        """
        ทำเหมือน Claude แต่ใช้ OpenAI API
        """
        
        # ✅ บันทึก user message
        requests.post(f"{BASE}/messages", json={
            "session_id": self.session_id,
            "role": "user",
            "content": user_input
        })
        
        # ✅ ดึง context จากสมองกลาง
        context_resp = requests.get(f"{BASE}/context/{self.session_id}")
        context_block = context_resp.json()["context_block"]
        
        # ✅ เตรียม system prompt
        system_prompt = f"""คุณคือ GPT-4 AI ผู้ช่วยเหลือ

=== ประวัติและข้อมูลที่เก็บไว้ ===
{context_block}

=== คำแนะนำ ===
- ตอบในภาษาไทย
- อ้างอิงการคุยที่ผ่านมา
- ให้ความเห็นที่สร้างสรรค์"""
        
        # ✅ ถาม GPT
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        
        answer = response.choices[0].message.content
        
        # ✅ บันทึก GPT response
        requests.post(f"{BASE}/messages", json={
            "session_id": self.session_id,
            "role": "assistant",
            "content": answer
        })
        
        return answer
    
    def set_memory(self, key: str, value: str):
        """เก็บข้อมูลลงสมองกลาง"""
        requests.post(f"{BASE}/memory", json={
            "key": key,
            "value": value,
            "scope": "global",
            "ai_agent": "all"
        })
        print(f"💾 Saved: {key}")

# ใช้งาน
if __name__ == "__main__":
    gpt = GPTBrain()
    
    print("\n" + "="*60)
    print("🧠 GPT-4 ใช้สมองกลาง")
    print("="*60)
    
    result = gpt.think("ช่วยอธิบายว่า Central Brain API ทำงานยังไง")
    print(f"\n✅ GPT-4: {result}\n")
