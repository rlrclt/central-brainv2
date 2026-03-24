"""
หลาย AI คุยกันผ่านสมองกลาง
Claude กับ GPT-4 ใช้ session เดียวกัน — ทั้งสองเห็นการคุยกัน
"""
import requests
from anthropic import Anthropic
import openai
import os

BASE = "http://localhost:7799"

class MultiAIDebate:
    def __init__(self):
        self.claude = Anthropic()
        self.gpt = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # สร้าง session เดียวสำหรับทั้ง 2 AI
        resp = requests.post(f"{BASE}/sessions", json={
            "ai_agent": "multi-ai",
            "project": "debate",
            "title": "Claude vs GPT-4 Debate"
        })
        self.session_id = resp.json()["session_id"]
        print(f"✅ Debate Session: {self.session_id}\n")
    
    def _get_context(self) -> str:
        """ดึง context สำหรับ AI ทั้งสอง"""
        resp = requests.get(f"{BASE}/context/{self.session_id}")
        return resp.json()["context_block"]
    
    def _save_message(self, role: str, content: str):
        """บันทึก message ลงสมองกลาง"""
        requests.post(f"{BASE}/messages", json={
            "session_id": self.session_id,
            "role": role,
            "content": content
        })
    
    def debate(self, topic: str, rounds: int = 2):
        """
        Claude และ GPT-4 คุยกันในหัวข้อเดียว
        """
        
        # บันทึกหัวข้อ
        self._save_message("user", f"Debate topic: {topic}")
        
        print(f"🎤 Debate Topic: {topic}\n")
        print("="*60)
        
        for round_num in range(1, rounds + 1):
            print(f"\n🔄 Round {round_num}")
            print("-"*60)
            
            # === Claude's turn ===
            context = self._get_context()
            
            prompt = f"""Topic: {topic}

Previous discussion:
{context}

Give your perspective as Claude. Be concise and thoughtful. Respond in Thai."""
            
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system="You are Claude, an AI assistant in a debate. Respond thoughtfully.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            claude_response = response.content[0].text
            print(f"\n🤖 Claude: {claude_response}")
            self._save_message("ai:claude", claude_response)
            
            # ดึง context อัพเดท
            context = self._get_context()
            
            # === GPT-4's turn ===
            prompt = f"""Topic: {topic}

Previous discussion:
{context}

Give your perspective as GPT-4. Be concise and thoughtful. Respond in Thai."""
            
            response = self.gpt.chat.completions.create(
                model="gpt-4",
                max_tokens=1024,
                system="You are GPT-4, an AI assistant in a debate. Respond thoughtfully.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            gpt_response = response.choices[0].message.content
            print(f"\n🤖 GPT-4: {gpt_response}")
            self._save_message("ai:gpt4", gpt_response)
        
        print("\n" + "="*60)
        print("✅ Debate finished!")

# ใช้งาน
if __name__ == "__main__":
    debate = MultiAIDebate()
    
    debate.debate(
        topic="ภาษาอะไรดีที่สุดสำหรับเขียน Web API — Python vs Node.js?",
        rounds=2
    )
