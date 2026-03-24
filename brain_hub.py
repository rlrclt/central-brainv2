"""
Brain Hub — ตัวควบคุมหลัก
ให้ AI ทุกตัว (Claude, GPT, Gemini, Copilot) เชื่อมสมองกลาง
"""
import requests
from config import Config
from anthropic import Anthropic
import openai
import os

class BrainHub:
    """
    ตัวกลาง (Hub) ที่ AI ใช้ในการเชื่อมกับ Central Brain
    - หลีกเลี่ยง API key ไม่ให้โปรแกรมอื่นเห็น
    - ช่วยให้เรียก API ง่ายๆ
    """
    
    def __init__(self, ai_agent: str, project: str = "default"):
        """
        ai_agent: ชื่อ AI (เช่น "claude", "gpt4", "gemini", "copilot")
        project: โปรเจกต์ (default: "default")
        """
        self.base_url = Config.CENTRAL_BRAIN_URL
        self.ai_agent = ai_agent
        self.project = project
        
        # เก็บ session id
        self.session_id = self._create_session()
        
        # สร้าง AI client
        if ai_agent == "claude":
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        elif ai_agent == "gpt4":
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        else:
            self.client = None
    
    def _create_session(self) -> str:
        """สร้าง session ใหม่ที่ Central Brain"""
        resp = requests.post(f"{self.base_url}/sessions", json={
            "ai_agent": self.ai_agent,
            "project": self.project,
            "title": f"{self.ai_agent.upper()} Session"
        })
        session_id = resp.json()["session_id"]
        print(f"✅ {self.ai_agent.upper()} connected | Session: {session_id}")
        return session_id
    
    def get_context(self) -> str:
        """ดึง context จากสมองกลาง (ประวัติ + shared memory)"""
        resp = requests.get(f"{self.base_url}/context/{self.session_id}")
        return resp.json()["context_block"]
    
    def save_message(self, role: str, content: str):
        """บันทึก message ลงสมองกลาง"""
        requests.post(f"{self.base_url}/messages", json={
            "session_id": self.session_id,
            "role": role,
            "content": content
        })
    
    def set_memory(self, key: str, value: str, scope: str = "global"):
        """เก็บข้อมูลลงสมองกลาง (shared memory)"""
        requests.post(f"{self.base_url}/memory", json={
            "key": key,
            "value": value,
            "scope": scope,
            "ai_agent": "all"  # ทุก AI เห็น
        })
    
    def ask_claude(self, prompt: str, system: str = None) -> str:
        """ถาม Claude"""
        if self.ai_agent != "claude":
            raise ValueError("This hub is not configured for Claude")
        
        # บันทึก user prompt
        self.save_message("user", prompt)
        
        # ดึง context
        context = self.get_context()
        
        # ประกอบ system prompt
        if not system:
            system = f"You are Claude AI assistant.\n\nMemory:\n{context}"
        else:
            system = f"{system}\n\nMemory:\n{context}"
        
        # ถาม Claude
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        
        answer = response.content[0].text
        
        # บันทึก response
        self.save_message("assistant", answer)
        
        return answer
    
    def ask_gpt(self, prompt: str, system: str = None) -> str:
        """ถาม GPT-4"""
        if self.ai_agent != "gpt4":
            raise ValueError("This hub is not configured for GPT-4")
        
        # บันทึก user prompt
        self.save_message("user", prompt)
        
        # ดึง context
        context = self.get_context()
        
        # ประกอบ system prompt
        if not system:
            system = f"You are GPT-4 AI assistant.\n\nMemory:\n{context}"
        else:
            system = f"{system}\n\nMemory:\n{context}"
        
        # ถาม GPT
        response = self.client.chat.completions.create(
            model="gpt-4",
            max_tokens=2048,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        )
        
        answer = response.choices[0].message.content
        
        # บันทึก response
        self.save_message("assistant", answer)
        
        return answer

# ใช้งาน
if __name__ == "__main__":
    print("🧠 Central Brain Hub\n")
    
    # ตรวจว่า API keys ครบ
    if not Config.validate():
        exit(1)
    
    print("\n" + "="*60)
    print("Example: ถาม Claude ผ่าน Central Brain")
    print("="*60)
    
    # สร้าง hub สำหรับ Claude
    hub = BrainHub("claude", "demo-project")
    
    # เซ็ต shared memory
    hub.set_memory("user_goal", "สร้าง Central Brain AI system")
    hub.set_memory("language", "Thai")
    
    # ถาม Claude
    answer = hub.ask_claude("ช่วยอธิบาย Central Brain API ให้ง่าย")
    print(f"\n✅ Claude: {answer}")
