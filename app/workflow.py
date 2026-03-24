"""
Workflow Engine — Debate mode & Pipeline mode
ระบบเลือก mode อัตโนมัติตามประเภทงาน
"""
from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime
import sqlite3, json, os, hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/brain.db")

# ─────────────────────────────────────────
# Models
# ─────────────────────────────────────────

class WorkflowCreate(BaseModel):
    task: str                          # คำอธิบายงาน
    mode: Literal["auto", "debate", "pipeline"] = "auto"
    agents: List[str]                  # เช่น ["claude", "gpt4"] หรือ ["planner","coder","reviewer"]
    project: Optional[str] = "default"
    max_rounds: Optional[int] = 5      # สำหรับ debate mode
    stop_keyword: Optional[str] = "[DONE]"  # AI พิมพ์นี้เพื่อจบ debate

class TurnInput(BaseModel):
    workflow_id: str
    agent: str
    content: str                       # สิ่งที่ AI ตัวนี้ตอบ/ทำ
    status: Optional[Literal["continue", "done", "reject"]] = "continue"

# ─────────────────────────────────────────
# DB helpers
# ─────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def now_iso():
    return datetime.utcnow().isoformat()

def init_workflow_tables():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS workflows (
            id          TEXT PRIMARY KEY,
            task        TEXT NOT NULL,
            mode        TEXT NOT NULL,
            agents      TEXT NOT NULL,
            project     TEXT DEFAULT 'default',
            status      TEXT DEFAULT 'running',
            current_step INTEGER DEFAULT 0,
            max_rounds  INTEGER DEFAULT 5,
            rounds_done INTEGER DEFAULT 0,
            stop_keyword TEXT DEFAULT '[DONE]',
            result      TEXT,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS workflow_turns (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_id TEXT NOT NULL,
            step        INTEGER NOT NULL,
            agent       TEXT NOT NULL,
            content     TEXT NOT NULL,
            status      TEXT DEFAULT 'continue',
            timestamp   TEXT NOT NULL,
            FOREIGN KEY (workflow_id) REFERENCES workflows(id)
        );

        CREATE INDEX IF NOT EXISTS idx_wf_turns ON workflow_turns(workflow_id, step);
    """)
    conn.commit()
    conn.close()

init_workflow_tables()

# ─────────────────────────────────────────
# Router logic — auto-detect mode
# ─────────────────────────────────────────

DEBATE_KEYWORDS = [
    "วิเคราะห์", "เปรียบเทียบ", "ถกเถียง", "ตัดสินใจ", "pros cons",
    "ควรเลือก", "ดีกว่า", "แนะนำ", "คิดเห็น", "ความเห็น",
    "analyze", "compare", "debate", "decide", "recommend", "opinion", "best option"
]

PIPELINE_KEYWORDS = [
    "เขียน code", "สร้าง", "พัฒนา", "implement", "ทำให้", "step by step",
    "build", "create", "develop", "write", "generate", "draft", "design",
    "plan", "execute", "review"
]

def detect_mode(task: str) -> str:
    task_lower = task.lower()
    debate_score = sum(1 for kw in DEBATE_KEYWORDS if kw.lower() in task_lower)
    pipeline_score = sum(1 for kw in PIPELINE_KEYWORDS if kw.lower() in task_lower)
    if debate_score > pipeline_score:
        return "debate"
    return "pipeline"  # default to pipeline

# ─────────────────────────────────────────
# Context builder for workflow
# ─────────────────────────────────────────

def build_workflow_context(workflow_id: str, for_agent: str) -> dict:
    """สร้าง context ที่ agent ควรรู้ก่อนตอบ"""
    conn = get_db()
    wf = conn.execute("SELECT * FROM workflows WHERE id=?", (workflow_id,)).fetchone()
    if not wf:
        conn.close()
        return {}

    wf = dict(wf)
    agents = json.loads(wf["agents"])
    turns = conn.execute(
        "SELECT * FROM workflow_turns WHERE workflow_id=? ORDER BY step ASC",
        (workflow_id,)
    ).fetchall()
    conn.close()

    turns_list = [dict(t) for t in turns]

    # build readable history
    history_text = ""
    for t in turns_list:
        history_text += f"\n[{t['agent'].upper()} | step {t['step']}]\n{t['content']}\n"

    mode = wf["mode"]
    current_step = wf["current_step"]

    if mode == "debate":
        next_agent = agents[current_step % len(agents)]
        instruction = (
            f"คุณคือ {for_agent} กำลังร่วม debate เพื่อหาคำตอบที่ดีที่สุดสำหรับ:\n"
            f"{wf['task']}\n\n"
            f"อ่าน history ด้านล่าง แล้วโต้แย้ง/เสริม/สรุป\n"
            f"เมื่อคิดว่าได้คำตอบที่ดีพอแล้ว ให้พิมพ์ {wf['stop_keyword']} ท้ายข้อความ"
        )
    else:
        role_index = agents.index(for_agent) if for_agent in agents else current_step
        role_desc = {
            0: "วางแผนงานให้ละเอียด แบ่ง task ย่อย ระบุ output ที่ต้องการ",
            1: "อ่านแผนจาก Planner แล้วลงมือทำตาม ส่ง output ที่สมบูรณ์",
            2: "ตรวจสอบ output จาก step ก่อน ถ้าผ่านพิมพ์ [DONE] ถ้าไม่ผ่านระบุสิ่งที่ต้องแก้"
        }.get(role_index, "ทำงานตาม task ที่ได้รับ")
        instruction = (
            f"คุณคือ {for_agent} — {role_desc}\n"
            f"Task: {wf['task']}\n"
        )

    return {
        "workflow_id": workflow_id,
        "mode": mode,
        "task": wf["task"],
        "agents": agents,
        "current_step": current_step,
        "rounds_done": wf["rounds_done"],
        "max_rounds": wf["max_rounds"],
        "status": wf["status"],
        "for_agent": for_agent,
        "instruction": instruction,
        "history": history_text.strip(),
        "system_prompt": f"{instruction}\n\n--- HISTORY ---\n{history_text.strip()}" if history_text else instruction
    }

# ─────────────────────────────────────────
# Core workflow functions
# ─────────────────────────────────────────

def create_workflow(body: WorkflowCreate) -> dict:
    mode = body.mode if body.mode != "auto" else detect_mode(body.task)
    wid = hashlib.md5(f"{body.task}{now_iso()}".encode()).hexdigest()[:12]

    conn = get_db()
    conn.execute("""
        INSERT INTO workflows
        (id, task, mode, agents, project, status, current_step, max_rounds, rounds_done, stop_keyword, created_at, updated_at)
        VALUES (?,?,?,?,?,'running',0,?,0,?,?,?)
    """, (
        wid, body.task, mode, json.dumps(body.agents), body.project,
        body.max_rounds, body.stop_keyword, now_iso(), now_iso()
    ))
    conn.commit()
    conn.close()

    agents = body.agents
    first_agent = agents[0]

    return {
        "workflow_id": wid,
        "mode": mode,
        "task": body.task,
        "agents": agents,
        "next_agent": first_agent,
        "next_context": build_workflow_context(wid, first_agent)
    }


def submit_turn(body: TurnInput) -> dict:
    conn = get_db()
    wf = conn.execute("SELECT * FROM workflows WHERE id=?", (body.workflow_id,)).fetchone()
    if not wf:
        conn.close()
        raise ValueError("Workflow not found")

    wf = dict(wf)
    if wf["status"] != "running":
        conn.close()
        return {"status": wf["status"], "message": "Workflow already finished"}

    agents = json.loads(wf["agents"])
    step = wf["current_step"]
    mode = wf["mode"]
    stop_kw = wf["stop_keyword"]

    # บันทึก turn นี้
    conn.execute("""
        INSERT INTO workflow_turns (workflow_id, step, agent, content, status, timestamp)
        VALUES (?,?,?,?,?,?)
    """, (body.workflow_id, step, body.agent, body.content, body.status, now_iso()))

    # ──────────────────────────────────────
    # ตัดสินใจ next step
    # ──────────────────────────────────────
    is_done = (
        body.status == "done"
        or stop_kw in body.content
    )

    if mode == "debate":
        rounds_done = wf["rounds_done"]
        next_step = step + 1
        next_agent_index = next_step % len(agents)
        next_agent = agents[next_agent_index]
        rounds_done_new = rounds_done + (1 if next_agent_index == 0 else 0)

        if is_done or rounds_done_new >= wf["max_rounds"]:
            conn.execute(
                "UPDATE workflows SET status='done', result=?, current_step=?, rounds_done=?, updated_at=? WHERE id=?",
                (body.content, next_step, rounds_done_new, now_iso(), body.workflow_id)
            )
            conn.commit()
            conn.close()
            return {"status": "done", "result": body.content, "mode": "debate"}

        conn.execute(
            "UPDATE workflows SET current_step=?, rounds_done=?, updated_at=? WHERE id=?",
            (next_step, rounds_done_new, now_iso(), body.workflow_id)
        )

    else:  # pipeline
        next_step = step + 1

        if is_done or next_step >= len(agents):
            # pipeline จบ หรือผ่านทุก step
            final_status = "done"
            conn.execute(
                "UPDATE workflows SET status=?, result=?, current_step=?, updated_at=? WHERE id=?",
                (final_status, body.content, next_step, now_iso(), body.workflow_id)
            )
            conn.commit()
            conn.close()
            return {"status": "done", "result": body.content, "mode": "pipeline"}

        if body.status == "reject":
            # Reviewer ส่งกลับ Coder (step ก่อนหน้า)
            next_step = max(0, step - 1)

        conn.execute(
            "UPDATE workflows SET current_step=?, updated_at=? WHERE id=?",
            (next_step, now_iso(), body.workflow_id)
        )

    conn.commit()
    conn.close()

    # หา next agent
    final_agents = json.loads(wf["agents"])
    next_agent = final_agents[next_step % len(final_agents)]
    next_ctx = build_workflow_context(body.workflow_id, next_agent)

    return {
        "status": "running",
        "next_agent": next_agent,
        "next_step": next_step,
        "next_context": next_ctx
    }


def get_workflow(workflow_id: str) -> dict:
    conn = get_db()
    wf = conn.execute("SELECT * FROM workflows WHERE id=?", (workflow_id,)).fetchone()
    if not wf:
        conn.close()
        raise ValueError("Workflow not found")
    wf = dict(wf)
    wf["agents"] = json.loads(wf["agents"])

    turns = conn.execute(
        "SELECT * FROM workflow_turns WHERE workflow_id=? ORDER BY step ASC",
        (workflow_id,)
    ).fetchall()
    conn.close()

    return {**wf, "turns": [dict(t) for t in turns]}
