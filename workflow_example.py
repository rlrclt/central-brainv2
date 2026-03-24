"""
ตัวอย่างการใช้ Workflow Engine — Debate & Pipeline
เรียกใช้โดย script ของคุณ ไม่ใช่ AI เรียกเอง
"""
import requests, time

BASE = "http://localhost:7799"

# ══════════════════════════════════════════════════════
# ตัวอย่าง 1: DEBATE MODE
# Claude กับ GPT ถกกันหาคำแนะนำที่ดีที่สุด
# ══════════════════════════════════════════════════════
def run_debate_example():
    print("\n=== DEBATE MODE ===")

    # สร้าง workflow
    wf = requests.post(f"{BASE}/workflow", json={
        "task": "เปรียบเทียบ Python vs Go สำหรับ backend API — ควรเลือกอะไร?",
        "mode": "auto",          # ระบบตรวจคำว่า "เปรียบเทียบ" → เลือก debate อัตโนมัติ
        "agents": ["claude", "gpt4"],
        "max_rounds": 3,
        "stop_keyword": "[DONE]"
    }).json()

    wf_id = wf["workflow_id"]
    print(f"Workflow: {wf_id} | Mode: {wf['mode']}")

    # ── Round 1: Claude ──
    # ในโค้ดจริง: ส่ง wf["next_context"]["system_prompt"] ให้ Claude แล้วรับคำตอบ
    claude_answer = "Python เหมาะกว่าเพราะ ecosystem ใหญ่กว่า library ครบกว่า..."
    result = requests.post(f"{BASE}/workflow/turn", json={
        "workflow_id": wf_id,
        "agent": "claude",
        "content": claude_answer,
        "status": "continue"
    }).json()
    print(f"After Claude → next: {result.get('next_agent')}")

    # ── Round 1: GPT โต้แย้ง ──
    gpt_answer = "Go ดีกว่าเพราะ performance สูงกว่ามาก concurrency ดีกว่า [DONE]"
    result = requests.post(f"{BASE}/workflow/turn", json={
        "workflow_id": wf_id,
        "agent": "gpt4",
        "content": gpt_answer,
        "status": "continue"
    }).json()
    print(f"Status: {result.get('status')}")
    if result.get("status") == "done":
        print(f"Result: {result.get('result')[:100]}...")


# ══════════════════════════════════════════════════════
# ตัวอย่าง 2: PIPELINE MODE
# Planner → Coder → Reviewer
# ══════════════════════════════════════════════════════
def run_pipeline_example():
    print("\n=== PIPELINE MODE ===")

    wf = requests.post(f"{BASE}/workflow", json={
        "task": "เขียน Python function สำหรับ hash password ด้วย bcrypt",
        "mode": "auto",          # ระบบตรวจคำว่า "เขียน" → เลือก pipeline อัตโนมัติ
        "agents": ["planner", "coder", "reviewer"],
        "project": "security-module"
    }).json()

    wf_id = wf["workflow_id"]
    print(f"Workflow: {wf_id} | Mode: {wf['mode']}")

    # ── Step 0: Planner ──
    # ดึง context: GET /workflow/{id}/context/planner
    ctx = requests.get(f"{BASE}/workflow/{wf_id}/context/planner").json()
    print(f"Planner system_prompt preview: {ctx['system_prompt'][:80]}...")

    plan = "1. import bcrypt\n2. function hash_password(password) -> hashed\n3. function verify_password..."
    result = requests.post(f"{BASE}/workflow/turn", json={
        "workflow_id": wf_id,
        "agent": "planner",
        "content": plan,
        "status": "continue"
    }).json()
    print(f"After Planner → next: {result.get('next_agent')}")

    # ── Step 1: Coder ──
    code = """
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
"""
    result = requests.post(f"{BASE}/workflow/turn", json={
        "workflow_id": wf_id,
        "agent": "coder",
        "content": code,
        "status": "continue"
    }).json()
    print(f"After Coder → next: {result.get('next_agent')}")

    # ── Step 2: Reviewer ──
    review = "Code ถูกต้อง ครบถ้วน ใช้ bcrypt อย่างถูกวิธี [DONE]"
    result = requests.post(f"{BASE}/workflow/turn", json={
        "workflow_id": wf_id,
        "agent": "reviewer",
        "content": review,
        "status": "done"
    }).json()
    print(f"Status: {result.get('status')}")


# ══════════════════════════════════════════════════════
# Pattern สำหรับ loop จริงกับ AI API
# ══════════════════════════════════════════════════════
def real_ai_loop(task: str, mode: str = "auto"):
    """
    Template สำหรับรัน workflow จริงกับ AI API
    แทนที่ call_ai() ด้วยการเรียก OpenAI / Claude / Gemini จริง
    """
    import anthropic  # หรือ openai, google.generativeai

    wf = requests.post(f"{BASE}/workflow", json={
        "task": task,
        "mode": mode,
        "agents": ["claude", "gpt4"],
    }).json()

    wf_id = wf["workflow_id"]
    next_agent = wf["next_agent"]
    next_ctx = wf["next_context"]

    while True:
        system_prompt = next_ctx["system_prompt"]

        # ── เรียก AI จริง (ตัวอย่าง Claude) ──
        # client = anthropic.Anthropic()
        # response = client.messages.create(
        #     model="claude-opus-4-20250514",
        #     max_tokens=2000,
        #     system=system_prompt,
        #     messages=[{"role": "user", "content": "ดำเนินการตาม instruction ด้านบน"}]
        # )
        # ai_output = response.content[0].text

        ai_output = f"[{next_agent}] ตอบ: ..."  # placeholder

        result = requests.post(f"{BASE}/workflow/turn", json={
            "workflow_id": wf_id,
            "agent": next_agent,
            "content": ai_output,
            "status": "continue"
        }).json()

        if result.get("status") == "done":
            print("Workflow complete!")
            print("Result:", result.get("result"))
            break

        next_agent = result["next_agent"]
        next_ctx = result["next_context"]
        time.sleep(1)  # หน่วงนิดนึงไม่ให้ call เร็วเกิน


if __name__ == "__main__":
    run_debate_example()
    run_pipeline_example()
