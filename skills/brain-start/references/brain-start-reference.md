# Brain Start Reference

## Core Files

- `README.md`: project overview and startup steps
- `app/main.py`: REST API, DB schema, context route, health route
- `brain_hub.py`: example client flow for AI agents
- `codex_integration.py`: Codex-focused session/context/reply workflow
- `app/workflow.py`: debate and pipeline coordination
- `.github/copilot-instructions.md`: condensed operating notes

## Central Brain Endpoints

- `POST /sessions`: create a session
- `POST /messages`: save a user or assistant message
- `GET /context/{session_id}`: fetch the assembled prompt context
- `POST /memory`: save shared memory
- `GET /memory`: inspect memory keys
- `GET /brain`: visualization UI
- `GET /brain/data`: graph data for the UI

## Minimum Agent Workflow

1. Start or reuse a session
2. Save the incoming user request
3. Read current context
4. Generate the answer using that context
5. Save the answer back

## Codex Example

```bash
python3 codex_integration.py --project demo --prompt "ช่วยสรุประบบนี้"
python3 codex_integration.py --session-id SESSION_ID --reply "คำตอบจาก Codex"
```

## Guardrails

- Do not claim memory recall if context was not fetched
- Do not overwrite or invent session IDs
- If the server is down, say that Central Brain is unavailable and continue transparently
