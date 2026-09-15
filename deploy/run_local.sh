#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=========================================================="
echo "⚡ Iniciando SurgiAuth AI (Backend FastAPI + Frontend Nuxt 4)"
echo "=========================================================="

cleanup() {
    echo ""
    echo "🛑 Deteniendo servidores..."
    kill $(jobs -p) 2>/dev/null || true
}
trap cleanup EXIT

# 1. Iniciar Backend FastAPI con uv
echo "🚀 [1/2] Iniciando Backend en http://127.0.0.1:8000..."
(cd "$DIR/backend" && uv run fastapi dev app/main.py --port 8000) &

sleep 2

# 2. Iniciar Frontend Nuxt 4 con bun
echo "🚀 [2/2] Iniciando Frontend Nuxt 4 en http://localhost:3000..."
(cd "$DIR/frontend" && bun run dev --port 3000) &

wait
