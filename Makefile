.PHONY: help install dev dev-backend dev-frontend test build docker-up docker-down tunnel clean

SHELL := /usr/bin/env bash

help:
	@echo "=========================================================="
	@echo "🩺 SurgiAuth AI — Makefile de Comandos"
	@echo "=========================================================="
	@echo "Comandos disponibles:"
	@echo "  make install        Instala dependencias de backend (uv) y frontend (bun)"
	@echo "  make dev            Inicia concurrentemente backend (:8000) y frontend (:3000)"
	@echo "  make dev-backend    Inicia sólo el backend FastAPI con uv"
	@echo "  make dev-frontend   Inicia sólo el frontend Nuxt 4 con bun"
	@echo "  make test           Ejecuta la suite de pruebas unitarias con pytest"
	@echo "  make build          Compila el frontend Nuxt 4 para producción"
	@echo "  make tunnel         Genera un enlace público HTTPS (Cloudflare / ngrok)"
	@echo "  make docker-up      Construye y levanta los contenedores Docker"
	@echo "  make docker-down    Detiene los contenedores Docker"
	@echo "  make clean          Limpia cachés de pytest, nuxt y temporales"
	@echo "=========================================================="

install:
	@echo "📦 Instalando dependencias de Backend con uv..."
	@cd backend && uv sync
	@echo "📦 Instalando dependencias de Frontend con bun..."
	@cd frontend && bun install

dev:
	@echo "🚀 Iniciando SurgiAuth AI (Backend :8000 + Frontend :3000)..."
	@trap 'kill $$(jobs -p) 2>/dev/null || true' EXIT; \
	(cd backend && uv run fastapi dev app/main.py --port 8000) & \
	sleep 2; \
	(cd frontend && bun run dev --port 3000) & \
	wait

dev-backend:
	@echo "🚀 Iniciando Backend FastAPI en http://127.0.0.1:8000..."
	@cd backend && uv run fastapi dev app/main.py --port 8000

dev-frontend:
	@echo "🚀 Iniciando Frontend Nuxt 4 en http://localhost:3000..."
	@cd frontend && bun run dev --port 3000

test:
	@echo "🧪 Ejecutando suite de pruebas automatizadas..."
	@cd backend && uv run pytest -v

build:
	@echo "🏗️ Compilando frontend Nuxt 4 con bun..."
	@cd frontend && bun run build

tunnel:
	@echo "🌐 Generando enlace público HTTPS para la evaluación..."
	@if command -v cloudflared &> /dev/null; then \
		echo "⚡ Iniciando túnel Cloudflare hacia http://localhost:3000..."; \
		cloudflared tunnel --url http://localhost:3000; \
	elif command -v ngrok &> /dev/null; then \
		echo "⚡ Iniciando túnel ngrok hacia puerto 3000..."; \
		ngrok http 3000; \
	else \
		echo "⚡ Iniciando localtunnel..."; \
		npx localtunnel --port 3000; \
	fi

docker-up:
	@echo "🐳 Levantando contenedores Docker..."
	@docker compose up --build

docker-down:
	@echo "🛑 Deteniendo contenedores Docker..."
	@docker compose down

clean:
	@echo "🧹 Limpiando cachés..."
	@rm -rf backend/.pytest_cache frontend/.nuxt frontend/.output
