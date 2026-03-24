---
name: brain-start
description: Use when the user asks for /brain-start, asks an AI to onboard into Central Brain, or wants the agent to learn the required workflow and operating rules before working. This skill teaches the agent what files to read first, how Central Brain works, and the minimum process for reading context and writing results back.
---

# Brain Start

Use this skill as the first step before an AI starts work in this repository or connects to Central Brain.

## Read First

Read these files in order:

1. `README.md`
2. `app/main.py`
3. `brain_hub.py`
4. `codex_integration.py`
5. `.github/copilot-instructions.md`

If the task involves multi-agent orchestration, also read `app/workflow.py`.

## What This System Is

Central Brain is a shared memory and session API for AI agents. It stores:

- sessions
- messages
- shared memory
- workflow state

The API server runs on `http://localhost:7799`.

## Required Operating Flow

Before answering as an AI agent:

1. Create or reuse a session
2. Save the user message into Central Brain
3. Read `/context/{session_id}`
4. Use that context in the system prompt
5. After answering, save the assistant reply back into Central Brain

For Codex-style agents, use `codex_integration.py` as the default implementation.

## Rules

- Do not ignore prior context if a session already exists
- Prefer continuing existing work over starting from zero
- If context is missing, say so clearly
- Do not claim Central Brain sync is active unless the session read/write steps actually ran
- When changing API behavior, keep docs and setup files in sync

## Quick Command Pattern

Prepare a turn:

```bash
python3 codex_integration.py --project default --prompt "USER_REQUEST"
```

Save the final reply:

```bash
python3 codex_integration.py --session-id SESSION_ID --reply "FINAL_ANSWER"
```

## Reference

For a concise operating checklist and file map, read `references/brain-start-reference.md`.
