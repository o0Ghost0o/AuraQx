#!/usr/bin/env bash
# Genera un enlace público HTTPS para el agente funcional requerido por el Hackathon

echo "=========================================================="
echo "🌐 Generando Enlace Público para SurgiAuth AI"
echo "=========================================================="

if command -v cloudflared &> /dev/null; then
    echo "⚡ Iniciando túnel rápido Cloudflare hacia http://localhost:3000..."
    cloudflared tunnel --url http://localhost:3000
elif command -v ngrok &> /dev/null; then
    echo "⚡ Iniciando túnel ngrok hacia puerto 3000..."
    ngrok http 3000
else
    echo "ℹ️ Ni cloudflared ni ngrok están instalados."
    echo "Puedes instalar cloudflared con: brew install cloudflared"
    echo "O usar npx: npx localtunnel --port 3000"
    npx localtunnel --port 3000
fi
