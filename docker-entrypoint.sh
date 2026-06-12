#!/bin/bash
set -e

echo "🚀 Starting Escalas application..."

# Initialize database if it doesn't exist
if [ ! -f "/app-data/escalas.db" ]; then
    echo "📊 Initializing database..."
    python -c "from app.database import init_db; init_db()"
fi

echo "✅ Starting uvicorn server..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Made with Bob
