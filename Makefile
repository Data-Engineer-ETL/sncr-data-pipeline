.PHONY: help install dev up down logs test clean extract api shell

# Variables
DOCKER_COMPOSE = docker-compose
PYTHON = python
PIP = pip

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	$(PIP) install -r requirements.txt

dev: ## Install development dependencies
	$(PIP) install -r requirements.txt
	$(PYTHON) -m playwright install chromium

up: ## Start all services with docker-compose
	$(DOCKER_COMPOSE) up -d

down: ## Stop all services
	$(DOCKER_COMPOSE) down

logs: ## Show logs from all services
	$(DOCKER_COMPOSE) logs -f

api: ## Start only the API service
	$(DOCKER_COMPOSE) up -d postgres api

extract: ## Run ETL extraction
	$(DOCKER_COMPOSE) --profile etl up etl

test: ## Run tests
	pytest tests/ -v

clean: ## Remove all containers, volumes, and generated files
	$(DOCKER_COMPOSE) down -v
	rm -rf logs/* checkpoints/* data/* __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

shell: ## Open a shell in the API container
	$(DOCKER_COMPOSE) exec api /bin/bash

psql: ## Connect to PostgreSQL
	$(DOCKER_COMPOSE) exec postgres psql -U sncr_user -d sncr_db

build: ## Rebuild Docker images
	$(DOCKER_COMPOSE) build --no-cache

restart: ## Restart all services
	$(DOCKER_COMPOSE) restart

ps: ## Show running containers
	$(DOCKER_COMPOSE) ps

stats: ## Show database statistics
	curl http://localhost:8000/stats

health: ## Check API health
	curl http://localhost:8000/health

setup: ## Initial setup (copy .env, build, migrate)
	cp .env.example .env
	$(DOCKER_COMPOSE) build
	$(DOCKER_COMPOSE) up -d postgres
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 5
	$(DOCKER_COMPOSE) exec -T postgres psql -U sncr_user -d sncr_db -f /docker-entrypoint-initdb.d/01-schema.sql
	@echo "Setup complete! Run 'make up' to start services."
