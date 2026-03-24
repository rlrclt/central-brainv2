#!/usr/bin/env python3
"""
ทดสอบ setup ว่าครบไหม
"""
import sys

print("🧪 Testing Central Brain Setup\n")

try:
    print("1️⃣  Testing config.py...")
    from config import Config
    print("   ✅ config.py loaded")
    print(f"   ℹ️  Central Brain URL: {Config.CENTRAL_BRAIN_URL}")
    
    print("\n2️⃣  Testing .env file...")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    if os.getenv("ANTHROPIC_API_KEY"):
        print("   ✅ ANTHROPIC_API_KEY found")
    else:
        print("   ⚠️  ANTHROPIC_API_KEY not found (create .env)")
    
    print("\n3️⃣  Testing BrainHub...")
    from brain_hub import BrainHub
    print("   ✅ brain_hub.py loaded")
    
    print("\n✅ Setup OK! Ready to use:\n")
    print("   1. Create .env from .env.example")
    print("   2. Fill in your API keys")
    print("   3. Run: bash start.sh")
    print("   4. In another terminal: python3 my_script.py")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nFix: pip3 install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
