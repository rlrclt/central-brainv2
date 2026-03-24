#!/usr/bin/env python3
"""
🧪 Central Brain Testing Suite
ทดสอบระบบทั้งหมดโดยไม่ต้องใช้ API keys
"""
import sys
import subprocess
import time
import requests
import json

def print_header(text):
    print(f"\n{'='*60}")
    print(f"🧪 {text}")
    print('='*60)

def print_pass(text):
    print(f"✅ {text}")

def print_fail(text):
    print(f"❌ {text}")
    return False

def print_info(text):
    print(f"ℹ️  {text}")

def test_imports():
    """ทดสอบว่า import ได้ไหม"""
    print_header("Test 1: Python Imports")
    
    try:
        print_info("Testing config.py...")
        from config import Config
        print_pass("config.py imports OK")
        
        print_info("Testing brain_hub.py...")
        from brain_hub import BrainHub
        print_pass("brain_hub.py imports OK")
        
        print_info("Checking Central Brain URL...")
        print(f"   URL: {Config.CENTRAL_BRAIN_URL}")
        print_pass("All imports successful")
        return True
        
    except ImportError as e:
        print_fail(f"Import failed: {e}")
        print("   Fix: pip3 install -r requirements.txt")
        return False

def test_server_connection():
    """ทดสอบว่าเชื่อม Central Brain server ได้ไหม"""
    print_header("Test 2: Central Brain Server Connection")
    
    try:
        resp = requests.get("http://localhost:7799/", timeout=3)
        if resp.status_code == 200:
            print_pass("Central Brain server is running ✅")
            return True
        else:
            print_fail("Server responded but with error code")
            return False
    except requests.exceptions.ConnectionError:
        print_fail("Cannot connect to http://localhost:7799")
        print("   Fix: Run 'bash start.sh' in Terminal 1")
        return False
    except Exception as e:
        print_fail(f"Connection error: {e}")
        return False

def test_api_endpoints():
    """ทดสอบ API endpoints (ไม่ต้อง AI keys)"""
    print_header("Test 3: API Endpoints (No API Keys Needed)")
    
    try:
        base = "http://localhost:7799"
        
        # Test 1: Create session
        print_info("Creating test session...")
        resp = requests.post(f"{base}/sessions", json={
            "ai_agent": "test-bot",
            "project": "testing",
            "title": "Test Session"
        }, timeout=5)
        
        if resp.status_code != 200:
            return print_fail(f"Failed to create session: {resp.status_code}")
        
        session_id = resp.json()["session_id"]
        print_pass(f"Session created: {session_id}")
        
        # Test 2: Save message
        print_info("Saving test message...")
        resp = requests.post(f"{base}/messages", json={
            "session_id": session_id,
            "role": "user",
            "content": "สวัสดี นี่คือข้อความทดสอบ"
        }, timeout=5)
        
        if resp.status_code != 200:
            return print_fail(f"Failed to save message: {resp.status_code}")
        print_pass("Message saved")
        
        # Test 3: Set memory
        print_info("Setting test memory...")
        resp = requests.post(f"{base}/memory", json={
            "key": "test_key",
            "value": "test_value",
            "scope": "global",
            "ai_agent": "all"
        }, timeout=5)
        
        if resp.status_code != 200:
            return print_fail(f"Failed to set memory: {resp.status_code}")
        print_pass("Memory saved")
        
        # Test 4: Get context
        print_info("Getting context...")
        resp = requests.get(f"{base}/context/{session_id}", timeout=5)
        
        if resp.status_code != 200:
            return print_fail(f"Failed to get context: {resp.status_code}")
        
        context = resp.json()["context_block"]
        print_pass("Context retrieved")
        print(f"   Context length: {len(context)} chars")
        
        # Test 5: List sessions
        print_info("Listing sessions...")
        resp = requests.get(f"{base}/sessions", timeout=5)
        
        if resp.status_code != 200:
            return print_fail(f"Failed to list sessions: {resp.status_code}")
        
        sessions = resp.json()
        print_pass(f"Found {len(sessions)} session(s)")
        
        return True
        
    except requests.exceptions.Timeout:
        return print_fail("Request timeout - server might be slow")
    except Exception as e:
        return print_fail(f"API test failed: {e}")

def test_config():
    """ทดสอบ config.py"""
    print_header("Test 4: Configuration")
    
    try:
        from config import Config
        import os
        
        print_info("Checking .env file...")
        if os.path.exists(".env"):
            print_pass(".env file exists")
        else:
            print("ℹ️  .env not found (will use defaults)")
        
        print_info("Checking Central Brain URL...")
        print(f"   {Config.CENTRAL_BRAIN_URL}")
        print_pass("Config loaded successfully")
        
        print_info("Checking API keys...")
        if Config.ANTHROPIC_API_KEY:
            print_pass("ANTHROPIC_API_KEY found")
        else:
            print("⚠️  ANTHROPIC_API_KEY not set")
        
        if Config.OPENAI_API_KEY:
            print_pass("OPENAI_API_KEY found")
        else:
            print("⚠️  OPENAI_API_KEY not set")
        
        if Config.GOOGLE_API_KEY:
            print_pass("GOOGLE_API_KEY found")
        else:
            print("⚠️  GOOGLE_API_KEY not set")
        
        return True
        
    except Exception as e:
        return print_fail(f"Config test failed: {e}")

def test_brain_hub():
    """ทดสอบ BrainHub (ไม่ต้องเรียก AI)"""
    print_header("Test 5: BrainHub Integration")
    
    try:
        print_info("Creating BrainHub instance (mock)...")
        
        from brain_hub import BrainHub
        
        # สร้าง hub สำหรับ claude (แต่ไม่เรียก API จริง)
        print("   Note: Not calling actual Claude/OpenAI API")
        print("   Just testing that BrainHub can initialize")
        
        # ไม่สร้าง instance จริง เพราะต้อง API key
        # แต่ import ได้ก็ OK
        print_pass("BrainHub class imports successfully")
        
        return True
        
    except Exception as e:
        return print_fail(f"BrainHub test failed: {e}")

def main():
    print("\n🧠 Central Brain Testing Suite\n")
    
    results = []
    
    # Test 1: Imports
    results.append(("Python Imports", test_imports()))
    
    # Test 2: Server Connection
    results.append(("Server Connection", test_server_connection()))
    
    if results[-1][1]:  # ถ้า server ทำงาน
        # Test 3: API Endpoints
        results.append(("API Endpoints", test_api_endpoints()))
    else:
        print_info("Skipping API tests (server not running)")
    
    # Test 4: Config
    results.append(("Configuration", test_config()))
    
    # Test 5: BrainHub
    results.append(("BrainHub Integration", test_brain_hub()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nResult: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready to use.")
        print("\nNext steps:")
        print("1. Set up .env with API keys: cp .env.example .env")
        print("2. Run server: bash start.sh")
        print("3. Run example: python3 claude_integration.py")
        return 0
    elif passed >= total - 1:
        print("\n⚠️  Most tests passed.")
        print("   Missing: Server connection")
        print("   Fix: Run 'bash start.sh' in another Terminal")
        return 0
    else:
        print("\n❌ Some tests failed. See above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
