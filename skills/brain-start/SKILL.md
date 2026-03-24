---
name: brain-start
description: Use when the user asks for /brain-start, asks an AI to onboard into Central Brain, or wants the agent to learn the required workflow and operating rules before working. This skill teaches the agent what files to read first, how Central Brain works, and the minimum process for reading context and writing results back.
---

# Brain Start

Use this skill as the first step before an AI starts work in this repository or connects to Central Brain.

## Read First

Always read `references/brain-start-reference.md` first. Treat that file as the bundled source of truth for this skill.

Then, if the current tool session has access to the project repository, read these files in order:

1. `README.md`
2. `app/main.py`
3. `brain_hub.py`
4. `codex_integration.py`
5. `.github/copilot-instructions.md`

If the task involves multi-agent orchestration and the repo is accessible, also read `app/workflow.py`.

If those project files are not available in the current session, continue using the bundled reference file instead of blocking.

## What This System Is

Central Brain is a shared memory and session API for AI agents. It stores:

- sessions
- messages
- shared memory
- workflow state

The API server runs on `http://localhost:7799`.

## Required Human Report

Immediately after activating this skill, output a short human-readable status report before doing any other task work.

That report must include:

1. whether the bundled skill reference was read
2. whether the project repository files were accessible
3. whether Central Brain connectivity was actually tested
4. whether Central Brain is connected, not connected, or not tested

Do not print memory contents, context contents, or any large internal dump from Central Brain in this report.

Use this format:

```text
Brain Start Status
- Skill reference: read / not read
- Repo access: available / unavailable
- Central Brain check: connected / not connected / not tested
- Notes: one short sentence
```

If connectivity was not tested, say `not tested` instead of pretending it is connected.

## Required Operating Flow

Before answering as an AI agent:

1. Create or reuse a session
2. Save the user message into Central Brain
3. Read `/context/{session_id}`
4. Use that context in the system prompt
5. After answering, save the assistant reply back into Central Brain

For Codex-style agents, use `codex_integration.py` as the default implementation.

If the current AI tool cannot call local scripts directly, still follow the same logical flow and report clearly which Central Brain steps were actually executed versus assumed.

## Rules

- Do not ignore prior context if a session already exists
- Prefer continuing existing work over starting from zero
- If context is missing, say so clearly
- Always emit the Brain Start Status report first for the human
- Do not claim Central Brain sync is active unless the session read/write steps actually ran
- Do not assume the project repository is mounted just because this skill is installed
- Do not dump memory values or context blocks in the status report
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
