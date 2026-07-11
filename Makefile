# FootPass — operator commands. Run `make help` for the list.
COMPOSE := docker compose
COMPOSE_DEV := docker compose -f docker-compose.yml -f docker-compose.dev.yml

.DEFAULT_GOAL := help

.PHONY: help install setup start stop restart logs status test lint format backup camera-test gpu-check update dev build

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## First-time install on this machine (ZimaBoard/Debian/Ubuntu)
	sudo bash scripts/install-zimaboard.sh

setup: ## Copy .env.example -> .env if missing, create data dir
	@test -f .env || (cp .env.example .env && echo "Created .env — edit it and set POSTGRES_PASSWORD + FOOTPASS_SECRET_KEY")
	@mkdir -p data && echo "data/ ready"

build: ## Build all images
	$(COMPOSE) build

start: ## Start the stack (production)
	$(COMPOSE) up -d

dev: ## Start the stack (development, API published on :8000)
	$(COMPOSE_DEV) up -d --build

stop: ## Stop the stack
	$(COMPOSE) down

restart: ## Restart the stack
	$(COMPOSE) restart

logs: ## Follow logs for all services
	$(COMPOSE) logs -f --tail=100

status: ## Show container status
	$(COMPOSE) ps

test: ## Run the backend test suite in a container
	$(COMPOSE) run --rm footpass-api pytest -q

lint: ## Lint backend (ruff)
	$(COMPOSE) run --rm footpass-api ruff check .

format: ## Format backend (ruff format)
	$(COMPOSE) run --rm footpass-api ruff format .

backup: ## Run a NAS/local backup now (Phase 4)
	bash scripts/backup-now.sh

camera-test: ## Detect connected USB cameras
	bash scripts/detect-camera.sh

gpu-check: ## Report NVIDIA GPU status (if present)
	bash scripts/detect-gpu.sh

update: ## Pull latest images and rebuild
	$(COMPOSE) pull && $(COMPOSE) up -d --build
