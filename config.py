"""
ตัวช่วยจัดการ API Keys และการเชื่อม AI ต่างๆ
เอา .env มา สร้าง Singleton ที่ใช้ API keys ได้ปลอดภัย
"""
import os
from dotenv import load_dotenv

# โหลด .env
load_dotenv()

class Config:
    """จัดการการตั้งค่าทั้งหมด"""
    
    # Central Brain
    CENTRAL_BRAIN_URL = os.getenv("CENTRAL_BRAIN_URL", "http://localhost:7799")
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Copilot
    COPILOT_ENABLED = os.getenv("COPILOT_ENABLED", "true").lower() == "true"
    COPILOT_NAME = os.getenv("COPILOT_NAME", "copilot-cli")
    
    @staticmethod
    def validate():
        """ตรวจว่า API keys ครบไหม"""
        missing = []
        
        if not Config.ANTHROPIC_API_KEY:
            missing.append("ANTHROPIC_API_KEY")
        if not Config.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not Config.GOOGLE_API_KEY:
            missing.append("GOOGLE_API_KEY")
        
        if missing:
            print(f"⚠️  Missing API keys: {', '.join(missing)}")
            print("📋 ทำการสร้าง .env โดยเอา .env.example มาแก้")
            return False
        
        print("✅ API keys ครบ")
        return True

if __name__ == "__main__":
    Config.validate()
    print(f"🧠 Central Brain: {Config.CENTRAL_BRAIN_URL}")
    print(f"🤖 Copilot: {'Enabled' if Config.COPILOT_ENABLED else 'Disabled'}")
