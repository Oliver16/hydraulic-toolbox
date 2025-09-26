PYTHON=python3
PIP=python3 -m pip

.PHONY: up down seed test fmt report-demo

up:
	@if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then \
		docker compose -f infrastructure/docker-compose.yml up -d --build; \
	elif command -v docker-compose >/dev/null 2>&1; then \
		docker-compose -f infrastructure/docker-compose.yml up -d --build; \
	else \
	    printf 'Error: Neither "docker compose" nor "docker-compose" is available. Please install Docker Compose.\n' >&2; \
	    exit 1; \
	fi

down:
	@if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then \
		docker compose -f infrastructure/docker-compose.yml down; \
	elif command -v docker-compose >/dev/null 2>&1; then \
		docker-compose -f infrastructure/docker-compose.yml down; \
	else \
	    printf 'Error: Neither "docker compose" nor "docker-compose" is available. Please install Docker Compose.\n' >&2; \
	    exit 1; \
	fi

seed:
	$(PYTHON) backend/app/seed.py

test:
	cd backend && $(PYTHON) -m pytest

fmt:
	cd backend && ruff check app --fix && black app && isort app

report-demo:
	cd backend && $(PYTHON) -m app.scripts.generate_report
