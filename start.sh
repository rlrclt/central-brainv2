#!/bin/bash
# ─────────────────────────────────────────
# Central Brain API — Start Script
# ─────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧠 Starting Central Brain API..."

# ติดตั้ง dependencies ถ้ายังไม่มี
if ! python3 -c "import fastapi" &>/dev/null; then
    echo "📦 Installing dependencies..."
    python3 -m pip install -r requirements.txt
fi

# รัน server
echo "✅ Running at http://localhost:7799"
echo "📖 Docs at  http://localhost:7799/docs"
echo ""
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 7799
