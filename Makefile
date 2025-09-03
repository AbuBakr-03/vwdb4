# Makefile for Watchtower V2 Docker Operations

.PHONY: help build build-prod up down logs shell clean test lint format

# Configuration
IMAGE_NAME = watchtower
REGISTRY = zaidkaraymeh
TAG = latest
COMPOSE_FILE = docker-compose.yml
COMPOSE_PROD_FILE = docker-compose.prod.yml

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker image for development
	docker build -t $(IMAGE_NAME):$(TAG) .

build-prod: ## Build production Docker image
	docker build --target production -t $(IMAGE_NAME):$(TAG) .

up: ## Start development environment
	docker-compose -f $(COMPOSE_FILE) up -d

up-prod: ## Start production environment
	docker-compose -f $(COMPOSE_PROD_FILE) up -d

down: ## Stop development environment
	docker-compose -f $(COMPOSE_FILE) down

down-prod: ## Stop production environment
	docker-compose -f $(COMPOSE_PROD_FILE) down

logs: ## Show development logs
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-prod: ## Show production logs
	docker-compose -f $(COMPOSE_PROD_FILE) logs -f

shell: ## Open shell in development container
	docker-compose -f $(COMPOSE_FILE) exec web bash

shell-prod: ## Open shell in production container
	docker-compose -f $(COMPOSE_PROD_FILE) exec web bash

clean: ## Remove all containers, images, and volumes
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -f

clean-prod: ## Remove production containers, images, and volumes
	docker-compose -f $(COMPOSE_PROD_FILE) down -v --rmi all

test: ## Run tests in container
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py test

migrate: ## Run database migrations
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py migrate

migrate-prod: ## Run production database migrations
	docker-compose -f $(COMPOSE_PROD_FILE) exec web python manage.py migrate

collectstatic: ## Collect static files
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py collectstatic --noinput

collectstatic-prod: ## Collect production static files
	docker-compose -f $(COMPOSE_PROD_FILE) exec web python manage.py collectstatic --noinput

create-superuser: ## Create Django superuser
	docker-compose -f $(COMPOSE_FILE) exec web python manage.py createsuperuser

# Registry operations
login: ## Login to Docker registry
	docker login $(REGISTRY)

push: ## Push image to registry
	docker tag $(IMAGE_NAME):$(TAG) $(REGISTRY)/$(IMAGE_NAME):$(TAG)
	docker push $(REGISTRY)/$(IMAGE_NAME):$(TAG)

push-latest: ## Push latest tag to registry
	docker tag $(IMAGE_NAME):$(TAG) $(REGISTRY)/$(IMAGE_NAME):latest
	docker push $(REGISTRY)/$(IMAGE_NAME):latest

pull: ## Pull image from registry
	docker pull $(REGISTRY)/$(IMAGE_NAME):$(TAG)

# Development helpers
restart: down up ## Restart development environment

restart-prod: down-prod up-prod ## Restart production environment

status: ## Show container status
	docker-compose -f $(COMPOSE_FILE) ps

status-prod: ## Show production container status
	docker-compose -f $(COMPOSE_PROD_FILE) ps

# Database operations
db-backup: ## Backup database
	docker-compose -f $(COMPOSE_FILE) exec db pg_dump -U postgres watchtower > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore: ## Restore database (usage: make db-restore FILE=backup.sql)
	docker-compose -f $(COMPOSE_FILE) exec -T db psql -U postgres watchtower < $(FILE)

# SSL certificate generation (for development)
ssl-certs: ## Generate self-signed SSL certificates for development
	mkdir -p nginx/ssl
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout nginx/ssl/key.pem \
		-out nginx/ssl/cert.pem \
		-subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Health check
health: ## Check application health
	curl -f http://localhost:8000/health/ || echo "Health check failed"

# Default target
.DEFAULT_GOAL := help 