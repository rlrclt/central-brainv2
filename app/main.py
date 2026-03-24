"""
Central Brain API — สมองกลางสำหรับ AI ทุกตัว
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sqlite3, json, os, hashlib
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/brain.db")
BRAIN_UI_PATH = Path(__file__).with_name("brain_ui.html")
MAX_MESSAGES_BEFORE_COMPRESS = 50   # compress เมื่อมีมากกว่านี้
KEEP_RECENT_MESSAGES = 10           # เก็บ message ล่าสุดไว้กี่อัน

app = FastAPI(title="Central Brain API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ─────────────────────────────────────────
# Database setup
# ─────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          TEXT PRIMARY KEY,
            ai_agent    TEXT NOT NULL,
            project     TEXT DEFAULT 'default',
            title       TEXT,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL,
            summary     TEXT,
            meta        TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            timestamp   TEXT NOT NULL,
            token_est   INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS memory (
            key         TEXT PRIMARY KEY,
            value       TEXT NOT NULL,
            scope       TEXT DEFAULT 'global',
            ai_agent    TEXT DEFAULT 'all',
            updated_at  TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
        CREATE INDEX IF NOT EXISTS idx_memory_scope ON memory(scope, ai_agent);
    """)
    conn.commit()
    conn.close()

init_db()

# ─────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────
class NewSession(BaseModel):
    ai_agent: str
    project: Optional[str] = "default"
    title: Optional[str] = None
    meta: Optional[dict] = {}

class AddMessage(BaseModel):
    role: str          # user / assistant / system / ai:<name>
    content: str
    session_id: str

class MemorySet(BaseModel):
    key: str
    value: str
    scope: Optional[str] = "global"
    ai_agent: Optional[str] = "all"

class CompressRequest(BaseModel):
    session_id: str
    summary: str       # ส่ง summary มาเก็บ

# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────
def now_iso():
    return datetime.utcnow().isoformat()

def estimate_tokens(text: str) -> int:
    return len(text) // 4

def auto_compress_check(session_id: str, conn):
    """ตรวจว่าต้อง compress ไหม — ถ้าใช่ ลบ message เก่าออก เหลือแค่ recent"""
    count = conn.execute(
        "SELECT COUNT(*) as c FROM messages WHERE session_id=?", (session_id,)
    ).fetchone()["c"]

    if count >= MAX_MESSAGES_BEFORE_COMPRESS:
        # เก็บ id ของ message ล่าสุด KEEP_RECENT_MESSAGES อัน
        recent_ids = [
            r["id"] for r in conn.execute(
                "SELECT id FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
                (session_id, KEEP_RECENT_MESSAGES)
            ).fetchall()
        ]
        if recent_ids:
            placeholders = ",".join("?" * len(recent_ids))
            conn.execute(
                f"DELETE FROM messages WHERE session_id=? AND id NOT IN ({placeholders})",
                [session_id] + recent_ids
            )
        conn.execute(
            "UPDATE sessions SET updated_at=?, summary=COALESCE(summary,'') || ' [auto-compressed at ' || ? || ']' WHERE id=?",
            (now_iso(), now_iso(), session_id)
        )
        conn.commit()
        return True
    return False

# ─────────────────────────────────────────
# Routes — Sessions
# ─────────────────────────────────────────
@app.post("/sessions", summary="สร้าง session ใหม่")
def create_session(body: NewSession):
    sid = hashlib.md5(f"{body.ai_agent}{now_iso()}".encode()).hexdigest()[:12]
    conn = get_db()
    conn.execute(
        "INSERT INTO sessions(id,ai_agent,project,title,created_at,updated_at,meta) VALUES(?,?,?,?,?,?,?)",
        (sid, body.ai_agent, body.project, body.title or f"Session {sid}",
         now_iso(), now_iso(), json.dumps(body.meta))
    )
    conn.commit()
    conn.close()
    return {"session_id": sid, "ai_agent": body.ai_agent, "project": body.project}

@app.get("/sessions", summary="ดู sessions ทั้งหมด")
def list_sessions(project: Optional[str] = None, ai_agent: Optional[str] = None, limit: int = 50):
    conn = get_db()
    q = "SELECT * FROM sessions WHERE 1=1"
    params = []
    if project:
        q += " AND project=?"; params.append(project)
    if ai_agent:
        q += " AND ai_agent=?"; params.append(ai_agent)
    q += " ORDER BY updated_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/sessions/{session_id}", summary="ดู session + messages")
def get_session(session_id: str, limit_messages: int = 30):
    conn = get_db()
    session = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
    if not session:
        raise HTTPException(404, "Session not found")
    msgs = conn.execute(
        "SELECT * FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
        (session_id, limit_messages)
    ).fetchall()
    conn.close()
    return {
        "session": dict(session),
        "messages": list(reversed([dict(m) for m in msgs]))
    }

@app.delete("/sessions/{session_id}", summary="ลบ session")
def delete_session(session_id: str):
    conn = get_db()
    conn.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
    conn.execute("DELETE FROM sessions WHERE id=?", (session_id,))
    conn.commit()
    conn.close()
    return {"deleted": session_id}

# ─────────────────────────────────────────
# Routes — Messages
# ─────────────────────────────────────────
@app.post("/messages", summary="เพิ่ม message + auto-compress")
def add_message(body: AddMessage):
    conn = get_db()
    session = conn.execute("SELECT id FROM sessions WHERE id=?", (body.session_id,)).fetchone()
    if not session:
        raise HTTPException(404, "Session not found")

    token_est = estimate_tokens(body.content)
    conn.execute(
        "INSERT INTO messages(session_id,role,content,timestamp,token_est) VALUES(?,?,?,?,?)",
        (body.session_id, body.role, body.content, now_iso(), token_est)
    )
    conn.execute("UPDATE sessions SET updated_at=? WHERE id=?", (now_iso(), body.session_id))
    conn.commit()

    compressed = auto_compress_check(body.session_id, conn)
    conn.close()
    return {"saved": True, "token_est": token_est, "auto_compressed": compressed}

@app.get("/messages/{session_id}", summary="ดึง messages ของ session")
def get_messages(session_id: str, limit: int = 50):
    conn = get_db()
    msgs = conn.execute(
        "SELECT * FROM messages WHERE session_id=? ORDER BY id ASC LIMIT ?",
        (session_id, limit)
    ).fetchall()
    conn.close()
    return [dict(m) for m in msgs]

# ─────────────────────────────────────────
# Routes — Memory (key-value global/shared)
# ─────────────────────────────────────────
@app.post("/memory", summary="เซ็ต memory (key-value)")
def set_memory(body: MemorySet):
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO memory(key,value,scope,ai_agent,updated_at) VALUES(?,?,?,?,?)",
        (body.key, body.value, body.scope, body.ai_agent, now_iso())
    )
    conn.commit()
    conn.close()
    return {"set": body.key}

@app.get("/memory", summary="ดึง memory ทั้งหมด")
def get_memory(scope: Optional[str] = None, ai_agent: Optional[str] = None):
    conn = get_db()
    q = "SELECT * FROM memory WHERE 1=1"
    params = []
    if scope:
        q += " AND scope=?"; params.append(scope)
    if ai_agent:
        q += " AND (ai_agent=? OR ai_agent='all')"; params.append(ai_agent)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return {r["key"]: {"value": r["value"], "scope": r["scope"], "ai_agent": r["ai_agent"], "updated_at": r["updated_at"]} for r in rows}

@app.get("/memory/{key}", summary="ดึง memory key เดียว")
def get_memory_key(key: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM memory WHERE key=?", (key,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Key not found")
    return dict(row)

@app.delete("/memory/{key}", summary="ลบ memory key")
def delete_memory_key(key: str):
    conn = get_db()
    conn.execute("DELETE FROM memory WHERE key=?", (key,))
    conn.commit()
    conn.close()
    return {"deleted": key}

# ─────────────────────────────────────────
# Routes — Compress / Summary
# ─────────────────────────────────────────
@app.post("/compress", summary="บันทึก summary แทน messages เก่า")
def compress_session(body: CompressRequest):
    conn = get_db()
    session = conn.execute("SELECT id FROM sessions WHERE id=?", (body.session_id,)).fetchone()
    if not session:
        raise HTTPException(404, "Session not found")
    # เก็บ 10 message ล่าสุด ลบที่เหลือ แล้วบันทึก summary
    recent_ids = [
        r["id"] for r in conn.execute(
            "SELECT id FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
            (body.session_id, KEEP_RECENT_MESSAGES)
        ).fetchall()
    ]
    if recent_ids:
        placeholders = ",".join("?" * len(recent_ids))
        conn.execute(
            f"DELETE FROM messages WHERE session_id=? AND id NOT IN ({placeholders})",
            [body.session_id] + recent_ids
        )
    conn.execute(
        "UPDATE sessions SET summary=?, updated_at=? WHERE id=?",
        (body.summary, now_iso(), body.session_id)
    )
    conn.commit()
    conn.close()
    return {"compressed": True, "session_id": body.session_id}

# ─────────────────────────────────────────
# Routes — Context (สำหรับ AI ดึงไปใช้เลย)
# ─────────────────────────────────────────
@app.get("/context/{session_id}", summary="ดึง context พร้อมใช้งานสำหรับ AI")
def get_context(session_id: str, include_memory: bool = True):
    """ดึง session summary + recent messages + global memory รวมกัน พร้อม inject ใน prompt"""
    conn = get_db()
    session = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
    if not session:
        raise HTTPException(404, "Session not found")

    session = dict(session)
    msgs = conn.execute(
        "SELECT role, content, timestamp FROM messages WHERE session_id=? ORDER BY id ASC LIMIT 30",
        (session_id,)
    ).fetchall()

    memory = {}
    if include_memory:
        mem_rows = conn.execute(
            "SELECT key, value FROM memory WHERE ai_agent=? OR ai_agent='all'",
            (session["ai_agent"],)
        ).fetchall()
        memory = {r["key"]: r["value"] for r in mem_rows}

    conn.close()

    context_text = ""
    if session.get("summary"):
        context_text += f"[SUMMARY OF PAST CONVERSATION]\n{session['summary']}\n\n"
    if memory:
        context_text += "[SHARED MEMORY]\n"
        for k, v in memory.items():
            context_text += f"  {k}: {v}\n"
        context_text += "\n"
    if msgs:
        context_text += "[RECENT MESSAGES]\n"
        for m in msgs:
            context_text += f"  [{m['role']}]: {m['content']}\n"

    return {
        "session_id": session_id,
        "ai_agent": session["ai_agent"],
        "project": session["project"],
        "context_block": context_text.strip(),
        "summary": session.get("summary"),
        "memory": memory,
        "messages": [dict(m) for m in msgs]
    }

# ─────────────────────────────────────────
# Routes — Workflow (Debate & Pipeline)
# ─────────────────────────────────────────
from app.workflow import (
    WorkflowCreate, TurnInput,
    create_workflow, submit_turn, get_workflow, detect_mode
)

@app.post("/workflow", summary="สร้าง workflow ใหม่ (debate หรือ pipeline)")
def start_workflow(body: WorkflowCreate):
    try:
        return create_workflow(body)
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/workflow/turn", summary="ส่ง output ของ agent เพื่อไปยัง step ถัดไป")
def workflow_turn(body: TurnInput):
    try:
        return submit_turn(body)
    except ValueError as e:
        raise HTTPException(404, str(e))

@app.get("/workflow/{workflow_id}", summary="ดู workflow + turns ทั้งหมด")
def view_workflow(workflow_id: str):
    try:
        return get_workflow(workflow_id)
    except ValueError as e:
        raise HTTPException(404, str(e))

@app.get("/workflow/{workflow_id}/context/{agent}", summary="ดึง context พร้อม system prompt สำหรับ agent")
def workflow_context(workflow_id: str, agent: str):
    from app.workflow import build_workflow_context
    ctx = build_workflow_context(workflow_id, agent)
    if not ctx:
        raise HTTPException(404, "Workflow not found")
    return ctx

@app.get("/workflows", summary="ดู workflows ทั้งหมด")
def list_workflows(project: Optional[str] = None, status: Optional[str] = None, limit: int = 20):
    conn = get_db()
    q = "SELECT * FROM workflows WHERE 1=1"
    params = []
    if project:
        q += " AND project=?"; params.append(project)
    if status:
        q += " AND status=?"; params.append(status)
    q += " ORDER BY created_at DESC LIMIT ?"; params.append(limit)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["agents"] = json.loads(d["agents"])
        result.append(d)
    return result


@app.get("/brain/data", summary="ข้อมูลสรุปสำหรับหน้า Brain Map")
def brain_map_data():
    conn = get_db()

    sessions = [dict(r) for r in conn.execute(
        """
        SELECT s.*,
               COUNT(m.id) AS message_count
        FROM sessions s
        LEFT JOIN messages m ON m.session_id = s.id
        GROUP BY s.id
        ORDER BY s.updated_at DESC
        LIMIT 120
        """
    ).fetchall()]
    memory_rows = [dict(r) for r in conn.execute(
        "SELECT * FROM memory ORDER BY updated_at DESC LIMIT 120"
    ).fetchall()]
    workflow_rows = [dict(r) for r in conn.execute(
        "SELECT * FROM workflows ORDER BY updated_at DESC LIMIT 60"
    ).fetchall()]
    conn.close()

    agent_counts = {}
    project_counts = {}
    for session in sessions:
        agent_counts[session["ai_agent"]] = agent_counts.get(session["ai_agent"], 0) + 1
        project_counts[session["project"]] = project_counts.get(session["project"], 0) + 1

    nodes = [{
        "id": "brain-core",
        "type": "core",
        "label": "Central Brain",
        "size": 34,
        "details": {
            "sessions": len(sessions),
            "memory_keys": len(memory_rows),
            "workflows": len(workflow_rows),
        },
    }]
    edges = []

    for agent, count in sorted(agent_counts.items()):
        agent_id = f"agent:{agent}"
        nodes.append({
            "id": agent_id,
            "type": "agent",
            "label": agent,
            "size": min(12 + count * 2, 28),
            "details": {"sessions": count},
        })
        edges.append({"source": "brain-core", "target": agent_id, "kind": "agent"})

    for session in sessions:
        session_id = f"session:{session['id']}"
        preview = (session.get("summary") or session.get("title") or "")[:180]
        nodes.append({
            "id": session_id,
            "type": "session",
            "label": session["title"] or session["id"],
            "size": min(10 + session["message_count"] // 2, 20),
            "details": {
                "session_id": session["id"],
                "ai_agent": session["ai_agent"],
                "project": session["project"],
                "messages": session["message_count"],
                "updated_at": session["updated_at"],
                "preview": preview,
            },
        })
        edges.append({
            "source": f"agent:{session['ai_agent']}",
            "target": session_id,
            "kind": "session",
        })

    for item in memory_rows:
        mem_id = f"memory:{item['key']}"
        nodes.append({
            "id": mem_id,
            "type": "memory",
            "label": item["key"],
            "size": 10,
            "details": {
                "value": str(item["value"])[:220],
                "scope": item["scope"],
                "ai_agent": item["ai_agent"],
                "updated_at": item["updated_at"],
            },
        })
        target_agent = "brain-core" if item["ai_agent"] == "all" else f"agent:{item['ai_agent']}"
        edges.append({"source": mem_id, "target": target_agent, "kind": "memory"})

    for workflow in workflow_rows:
        workflow_id = f"workflow:{workflow['id']}"
        agents = json.loads(workflow["agents"])
        nodes.append({
            "id": workflow_id,
            "type": "workflow",
            "label": workflow["task"][:36] or workflow["id"],
            "size": 12,
            "details": {
                "workflow_id": workflow["id"],
                "mode": workflow["mode"],
                "status": workflow["status"],
                "agents": agents,
                "task": workflow["task"][:220],
                "updated_at": workflow["updated_at"],
            },
        })
        edges.append({"source": "brain-core", "target": workflow_id, "kind": "workflow"})

    return {
        "stats": {
            "sessions": len(sessions),
            "memory_keys": len(memory_rows),
            "workflows": len(workflow_rows),
            "agents": len(agent_counts),
            "projects": len(project_counts),
        },
        "nodes": nodes,
        "edges": edges,
    }


@app.get("/brain", response_class=HTMLResponse, summary="หน้าแสดงภาพสมองกลาง")
def brain_map_page():
    return BRAIN_UI_PATH.read_text(encoding="utf-8")

# ─────────────────────────────────────────
# Health check
# ─────────────────────────────────────────
@app.get("/", summary="Health check")
def root():
    conn = get_db()
    sessions = conn.execute("SELECT COUNT(*) as c FROM sessions").fetchone()["c"]
    messages = conn.execute("SELECT COUNT(*) as c FROM messages").fetchone()["c"]
    memory   = conn.execute("SELECT COUNT(*) as c FROM memory").fetchone()["c"]
    conn.close()
    return {
        "status": "ok",
        "stats": {"sessions": sessions, "messages": messages, "memory_keys": memory}
    }
