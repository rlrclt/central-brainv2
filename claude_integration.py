"""
เชื่อม Claude กับ Central Brain API
สมองกลางแห่งข้อมูล — Claude จะจำการคุยได้ไม่มีที่สิ้นสุด
"""
import requests
from anthropic import Anthropic

BASE = "http://localhost:7799"

class ClaudeBrain:
    def __init__(self, session_id: str = None):
        self.client = Anthropic()
        
        # สร้าง session ใหม่ถ้าไม่มี
        if not session_id:
            resp = requests.post(f"{BASE}/sessions", json={
                "ai_agent": "claude",
                "project": "default",
                "title": "Claude Session"
            })
            self.session_id = resp.json()["session_id"]
        else:
            self.session_id = session_id
            
        print(f"✅ Session ID: {self.session_id}")
    
    def think(self, user_input: str) -> str:
        """
        1. บันทึก user input ลงสมองกลาง
        2. ดึง context จากสมองกลาง (การคุยที่ผ่านมา + shared memory)
        3. ให้ Claude ตอบโดยอ่าน context
        4. บันทึก Claude response ลงสมองกลาง
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
        system_prompt = f"""คุณคือ Claude AI ผู้ช่วยเหลือ อ่านประวัติการคุยและข้อมูลที่เก็บไว้

=== ประวัติและข้อมูลที่เก็บไว้ ===
{context_block}

=== คำแนะนำ ===
- ตอบในภาษาไทย
- อ้างอิงการคุยที่ผ่านมา
- ให้ความเห็นที่สร้างสรรค์และสมจริง
- ถ้าไม่รู้ก็บอกตรงๆ"""
        
        # ✅ ถาม Claude
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_input}]
        )
        
        answer = response.content[0].text
        
        # ✅ บันทึก Claude response
        requests.post(f"{BASE}/messages", json={
            "session_id": self.session_id,
            "role": "assistant",
            "content": answer
        })
        
        return answer
    
    def set_memory(self, key: str, value: str):
        """เก็บข้อมูลลงสมองกลาง (สำหรับทุก AI ใช้)"""
        requests.post(f"{BASE}/memory", json={
            "key": key,
            "value": value,
            "scope": "global",
            "ai_agent": "all"
        })
        print(f"💾 Saved: {key}")
    
    def get_memory(self):
        """ดึงข้อมูลทั้งหมดจากสมองกลาง"""
        resp = requests.get(f"{BASE}/memory")
        return resp.json()

# ใช้งาน
if __name__ == "__main__":
    claude = ClaudeBrain()
    
    # ตั้งค่า shared memory
    claude.set_memory("user_name", "ผู้ใช้ท่านนี้")
    claude.set_memory("project_goal", "สร้าง Central Brain สำหรับ AI หลายตัว")
    claude.set_memory("language", "ภาษาไทยเป็นหลัก")
    
    print("\n" + "="*60)
    print("🧠 Claude จำวสมองกลาง")
    print("="*60)
    
    # คำถามที่ 1
    print("\n📝 Q1: ช่วยเขียนฟังก์ชัน Python สำหรับ reverse string")
    result1 = claude.think("ช่วยเขียนฟังก์ชัน Python สำหรับ reverse string")
    print(f"\n✅ Claude: {result1}\n")
    
    # คำถามที่ 2 (Claude จะจำการคุยครั้งแรก)
    print("\n" + "="*60)
    print("📝 Q2: ช่วยเพิ่ม error handling ให้โค้ดด้านบน")
    result2 = claude.think("ช่วยเพิ่ม error handling ให้โค้ดด้านบน")
    print(f"\n✅ Claude: {result2}\n")
    
    # คำถามที่ 3 (ยังจำได้)
    print("\n" + "="*60)
    print("📝 Q3: เขียนภาษาไทยสรุปที่เราคุยกันไป")
    result3 = claude.think("เขียนภาษาไทยสรุปที่เราคุยกันไป")
    print(f"\n✅ Claude: {result3}\n")
