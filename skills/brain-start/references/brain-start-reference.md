# Brain Start Reference

This file is bundled with the installed skill and should be readable even when the full project repo is not mounted into the AI session.

## System Summary

Central Brain is a local shared-memory backend for AI agents. It runs as a FastAPI server on `http://localhost:7799` and stores state in SQLite. Its main purpose is to let multiple AI tools share:

- sessions
- conversation history
- memory key-value pairs
- workflow state

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

## Context Behavior

The most important route is `GET /context/{session_id}`.

That endpoint returns a `context_block` assembled from:

- session summary
- shared memory
- recent messages

The intended AI pattern is:

1. create or reuse a session
2. save the incoming user message
3. fetch `context_block`
4. inject that context into the system prompt
5. generate the reply
6. save the final assistant reply

If an AI tool skips step 3, it should not claim to be synced with Central Brain memory.

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

## Repo Access Fallback

If the AI session cannot read the project repo directly:

- use this bundled reference file as the baseline
- explain that the repository files were not directly inspected
- avoid pretending that local scripts or API calls were executed unless they really were

If the repo is available, read:

1. `README.md`
2. `app/main.py`
3. `brain_hub.py`
4. `codex_integration.py`
5. `.github/copilot-instructions.md`

## Human Status Report

After this skill is activated, the AI should report status to the human immediately in a short form.

Required fields:

- `Skill reference`: whether this bundled reference was read
- `Repo access`: whether the actual project repo could be inspected
- `Central Brain check`: `connected`, `not connected`, or `not tested`
- `Notes`: one short sentence only

Template:

```text
Brain Start Status
- Skill reference: read
- Repo access: available
- Central Brain check: not tested
- Notes: Bundled reference loaded; project files were available; no live API check was run yet.
```

Do not include `context_block`, memory values, message contents, or any large dump in this report.

## Guardrails

- Do not claim memory recall if context was not fetched
- Do not overwrite or invent session IDs
- If the server is down, say that Central Brain is unavailable and continue transparently
