PYTHON=python3
PIP=python3 -m pip

.PHONY: up down seed test fmt report-demo

up:
	@if docker compose version >/dev/null 2>&1; then \
		docker compose -f infrastructure/docker-compose.yml up -d --build; \
	else \
		docker-compose -f infrastructure/docker-compose.yml up -d --build; \
	fi

down:
	@if docker compose version >/dev/null 2>&1; then \
		docker compose -f infrastructure/docker-compose.yml down; \
	else \
		docker-compose -f infrastructure/docker-compose.yml down; \
	fi

seed:
	$(PYTHON) backend/app/seed.py

test:
	cd backend && $(PYTHON) -m pytest

fmt:
	cd backend && ruff check app --fix && black app && isort app

report-demo:
	cd backend && $(PYTHON) -m app.scripts.generate_report
