# Copilot Instructions for Central Brain API

## 🎯 Project Purpose

Central Brain is a shared memory service for multi-AI workflows. It provides a REST API that allows different AI agents to:
- Share conversation history via sessions
- Access global and scoped memory (key-value store)
- Automatically compress old messages to save tokens
- Coordinate workflows (debate mode, pipeline mode)

It runs as a FastAPI server on port 7799 with a SQLite database.

## 🚀 Running the Project

### Starting the Server
```bash
bash start.sh
```
This installs dependencies (if needed) and runs: `uvicorn app.main:app --host 0.0.0.0 --port 7799 --reload`

**Docs:** http://localhost:7799/docs (auto-generated Swagger UI)

### Testing with Example Code
```bash
python3 example_usage.py
```
This demonstrates the client-side API pattern: create session → get context → save messages.

## 🏗️ Architecture

### Core Components

**app/main.py** — REST API server
- **Sessions**: Isolated conversation contexts for each AI agent (`/sessions`, `/messages`)
- **Memory**: Shared key-value store across all agents (`/memory`, with scope + ai_agent filtering)
- **Auto-compression**: When messages exceed `MAX_MESSAGES_BEFORE_COMPRESS`, old messages are deleted and a summary is appended to the session
- Context Block: `/context/{session_id}` returns all memory + recent messages formatted for injection into AI prompts

**app/workflow.py** — Multi-agent orchestration (not yet integrated into main.py)
- Supports "debate mode" (multi-round discussion), "pipeline mode" (sequential execution), and "auto" (chooses based on task)
- Stores workflows and turns in separate DB tables

**data/brain.db** — SQLite with 3 tables:
- `sessions`: id, ai_agent, project, title, created_at, updated_at, summary, meta
- `messages`: id, session_id, role, content, timestamp, token_est
- `memory`: key, value, scope, ai_agent, updated_at

### Configuration Constants (app/main.py)
```python
MAX_MESSAGES_BEFORE_COMPRESS = 50   # Auto-compress when message count exceeds this
KEEP_RECENT_MESSAGES = 10           # How many recent messages to retain after compression
```

## 🔌 Key API Patterns

### Standard Workflow (all integrations follow this)
1. **Create session:** `POST /sessions` → get `session_id`
2. **Before calling AI:** `GET /context/{session_id}` → inject context into system prompt
3. **After AI responds:** `POST /messages` (save user message, then AI response)

### Memory Scope & Filtering
- `scope="global"` (default) — visible to all sessions
- `scope="project"` — visible within same project
- `ai_agent="all"` (default) — applicable to any agent; or specify single agent name
- Query with `/memory?scope=X&ai_agent=Y` to filter

### Auto-Compression Behavior
- When `POST /messages` triggers a compression, the response includes `"auto_compressed": true`
- Old messages are deleted; session.summary is appended with timestamp
- Recent messages (count = `KEEP_RECENT_MESSAGES`) are always retained

## 📝 Code Conventions

### Database Interaction
- Always get a fresh connection: `conn = get_db()`
- Always close: `conn.close()`
- Use `conn.row_factory = sqlite3.Row` (already set in `get_db()`) to access columns by name
- Timestamps are ISO format: `datetime.utcnow().isoformat()`

### Adding New Endpoints
- Use Pydantic models for request bodies (see `AddMessage`, `MemorySet`, `NewSession`)
- Include FastAPI route decorators with `summary=""` for Swagger docs
- Follow error pattern: `raise HTTPException(404, "reason")` for client errors
- Commit transactions explicitly: `conn.commit()`

### Message Roles
- Standard: `"user"`, `"assistant"`, `"system"`
- Custom: `"ai:<agent_name>"` (e.g., `"ai:claude"`, `"ai:gpt4"`)

## 🔧 Common Modifications

### Adjust Auto-Compression Threshold
Edit `MAX_MESSAGES_BEFORE_COMPRESS` and `KEEP_RECENT_MESSAGES` in `app/main.py` (top of file). These are not database migrations — just config constants. No database changes needed.

### Add a New Endpoint
1. Define Pydantic model
2. Add function with `@app.post/get/etc()` decorator
3. Use `get_db()` for queries
4. Return dict or list (FastAPI auto-serializes)

### Token Estimation
The `estimate_tokens()` function uses simple approximation: `len(text) // 4`. This is intentionally rough for speed. Fine-tune if needed for specific use cases.

## 🚨 Important Notes

- **No Authentication** — CORS is wide open (`allow_origins=["*"]`). Use only in trusted environments or add authentication middleware.
- **SQLite Limitations** — SQLite is single-writer. Under very high concurrency, add a queue (Redis, RabbitMQ) in front.
- **DB Path** — Hardcoded to `../data/brain.db` relative to `app/main.py`. Make sure `data/` directory is writable.
- **Workflow Mode** — `app/workflow.py` exists but is not integrated into main.py routes yet. Currently for reference only.
