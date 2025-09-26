PYTHON=python3
PIP=python3 -m pip

.PHONY: up down seed test fmt report-demo

up:
docker-compose -f infrastructure/docker-compose.yml up -d --build

down:
docker-compose -f infrastructure/docker-compose.yml down

seed:
$(PYTHON) backend/app/seed.py

test:
cd backend && $(PYTHON) -m pytest

fmt:
cd backend && ruff check app --fix && black app && isort app

report-demo:
cd backend && $(PYTHON) -m app.scripts.generate_report
