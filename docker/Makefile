.PHONY: help up down logs clean test status health

help:
	@echo "Hermes Local Lab - Docker Compose Management"
	@echo ""
	@echo "Available commands:"
	@echo "  make up          - Start all services (docker-compose up -d)"
	@echo "  make down        - Stop all services (docker-compose down)"
	@echo "  make logs        - Show logs from all services"
	@echo "  make status      - Show service status"
	@echo "  make health      - Check health of all services"
	@echo "  make clean       - Remove all containers and volumes"
	@echo "  make test        - Run basic API tests"
	@echo "  make shell-api   - Open shell in hermes-api container"
	@echo "  make shell-n8n   - Open shell in n8n container"
	@echo ""

up:
	docker-compose up -d
	@echo "✅ Services starting. Run 'make health' to check status."

down:
	docker-compose down

logs:
	docker-compose logs -f

status:
	docker-compose ps

health:
	@echo "=== Service Health Check ===" && \
	echo "" && \
	echo "API (8000):" && \
	curl -s http://localhost:8000/api/health | jq . || echo "API not responding" && \
	echo "" && \
	echo "Web UI (8080):" && \
	curl -s http://localhost:8080/health | jq . || echo "Web UI not responding" && \
	echo "" && \
	echo "n8n (5678):" && \
	curl -s http://localhost:5678/rest/health || echo "n8n not responding" && \
	echo "" && \
	echo "PostgreSQL (5432):" && \
	docker exec hermes-n8n-db pg_isready -U n8n || echo "DB not ready"

test:
	@echo "=== Running Basic Tests ===" && \
	echo "" && \
	echo "1. Testing API Health:" && \
	curl -s http://localhost:8000/api/health | jq . && \
	echo "" && \
	echo "2. Testing Web UI:" && \
	curl -s http://localhost:8080/ | head -5

clean:
	docker-compose down -v
	@echo "All containers and volumes removed"

shell-api:
	docker exec -it hermes-api-local /bin/bash

shell-n8n:
	docker exec -it hermes-n8n /bin/bash

logs-api:
	docker-compose logs -f hermes-api-local

logs-n8n:
	docker-compose logs -f hermes-n8n
