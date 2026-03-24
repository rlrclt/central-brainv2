---
name: brain-status
description: Use when the user asks for /brain-status, wants a human-readable health/status report for Central Brain, wants to know whether the system is connected, or asks what data is present without dumping memory contents. This skill reports server status, high-level counts, and visibility into the current state without exposing raw context blocks.
---

# Brain Status

Use this skill to inspect Central Brain and report status for a human.

## Read First

Always read `references/brain-status-reference.md` first.

If the current tool session can access the project repository, optionally inspect:

1. `app/main.py`
2. `app/brain_ui.html`
3. `README.md`

If the repo is not accessible, continue using the bundled reference.

## What To Check

When possible, check these endpoints in this order:

1. `GET /`
2. `GET /brain/data`
3. `GET /sessions`
4. `GET /memory`
5. `GET /workflows`

Do not claim an endpoint was tested if the current AI tool could not actually call it.

## Required Human Report

Output a short status report in this format:

```text
Brain Status Report
- Server: connected / not connected / not tested
- Brain map data: available / unavailable / not tested
- Sessions: number or unknown
- Memory keys: number or unknown
- Workflows: number or unknown
- Notes: one short sentence
```

If the user asks for more detail, summarize high-level patterns only. Do not dump:

- `context_block`
- full memory values
- long message history
- raw internal JSON unless the user explicitly asks for it

## Rules

- Prefer direct API checks over assumptions
- If an API check cannot be run, say `not tested`
- Keep the report useful for humans, not machine logs
- Mention connectivity and counts first
- Do not expose sensitive or verbose memory contents in the default report
