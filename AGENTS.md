# Repository Guidelines

## Project Structure & Module Organization
`app/main.py` contains the FastAPI server and SQLite-backed session, message, and memory endpoints. `app/workflow.py` adds workflow/debate logic on the same `data/brain.db` database. Root-level scripts such as `brain_hub.py`, `claude_integration.py`, `gpt_integration.py`, `multi_ai.py`, and `workflow_example.py` are client and usage examples. Setup and troubleshooting docs live in `README.md`, `QUICK_START.md`, `START_HERE.md`, and `TESTING_CHECKLIST.md`.

## Build, Test, and Development Commands
Install dependencies with `pip3 install -r requirements.txt`. Start the API locally with `bash start.sh`; it runs `uvicorn app.main:app --host 0.0.0.0 --port 7799 --reload`. Run `python3 test_setup.py` for a quick import/config check. Run `python3 test_full.py` for the broader suite; start the server first if you want endpoint checks to pass. Use `curl http://localhost:7799/` to confirm the health check is up.

## Coding Style & Naming Conventions
Follow the existing Python style: 4-space indentation, `snake_case` for functions and variables, `PascalCase` for classes, and concise module-level docstrings. Keep API route handlers and Pydantic models explicit rather than clever. This repo does not include Ruff, Black, or Flake8 config, so match the surrounding file style and keep imports straightforward and grouped logically.

## Testing Guidelines
Tests are script-based, not `pytest`-based. Add coverage by extending `test_setup.py` for import/config validation and `test_full.py` for integration checks against the local server. Prefer small, deterministic checks that work without external API keys; reserve provider-specific validation for the example integration scripts. Name new test helpers clearly, for example `test_memory_roundtrip()`.

## Commit & Pull Request Guidelines
Git history is not available in this workspace snapshot, so no repository-specific commit convention could be verified. Use short imperative subjects such as `Add workflow health-check test` and keep commits focused. PRs should describe behavior changes, list commands run, mention any `.env` or API-key assumptions, and include request/response examples or screenshots when API docs or UI-visible output change.

## Security & Configuration Tips
Copy `.env.example` to `.env` and never commit real keys. Treat `data/brain.db` as local state, not source. If you change ports, URLs, or agent settings, update both `config.py` and the setup docs.
