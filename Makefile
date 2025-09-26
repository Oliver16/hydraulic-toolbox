PYTHON=python3
PIP=python3 -m pip

DOCKER_COMPOSE_DETECT=\
    if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then \
        printf '%s' 'docker compose'; \
    elif command -v docker-compose >/dev/null 2>&1; then \
        printf '%s' 'docker-compose'; \
    else \
        printf '%s' ''; \
    fi

.PHONY: up down seed test fmt report-demo

up:
	@cmd="$$( $(DOCKER_COMPOSE_DETECT) )"; \
	if [ -z "$$cmd" ]; then \
	    printf 'Error: Neither "docker compose" nor "docker-compose" is available. Please install Docker Compose.\n' >&2; \
	    exit 1; \
	fi; \
	$$cmd -f infrastructure/docker-compose.yml up -d --build

down:
	@cmd="$$( $(DOCKER_COMPOSE_DETECT) )"; \
	if [ -z "$$cmd" ]; then \
	    printf 'Error: Neither "docker compose" nor "docker-compose" is available. Please install Docker Compose.\n' >&2; \
	    exit 1; \
	fi; \
	$$cmd -f infrastructure/docker-compose.yml down

seed:
	$(PYTHON) backend/app/seed.py

test:
	cd backend && $(PYTHON) -m pytest

fmt:
	cd backend && ruff check app --fix && black app && isort app

report-demo:
	cd backend && $(PYTHON) -m app.scripts.generate_report
