# Brain Status Reference

This file is bundled with the installed skill and should be used even if the full project repository is not mounted into the current AI session.

## Purpose

`brain-status` is for checking whether Central Brain appears reachable and summarizing its current state for a human.

## Primary Endpoints

- `GET /`
  - health check
  - expected shape: `status` plus high-level stats
- `GET /brain/data`
  - returns graph-ready summary data
  - includes counts for sessions, memory keys, workflows, agents, and projects
- `GET /sessions`
  - list sessions
- `GET /memory`
  - list memory keys and metadata
- `GET /workflows`
  - list workflow objects

## Recommended Status Logic

If direct API access is possible:

1. call `GET /`
2. if it succeeds, mark server as `connected`
3. call `GET /brain/data`
4. extract only high-level counts
5. optionally confirm sessions, memory, or workflows through their dedicated endpoints

If direct API access is not possible:

- say `not tested`
- do not pretend connectivity is known
- provide only static guidance from this reference

## Default Human Output

```text
Brain Status Report
- Server: connected
- Brain map data: available
- Sessions: 12
- Memory keys: 8
- Workflows: 2
- Notes: Health and brain summary endpoints responded successfully.
```

## Guardrails

- Do not print `context_block` in the default report
- Do not print raw memory values in the default report
- Do not dump large JSON unless the user explicitly asks for raw output
- Prefer counts, availability, and short descriptions
