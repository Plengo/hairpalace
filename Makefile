# ─────────────────────────────────────────────────────────────────────────────
# STRANDS — Developer Makefile
# Usage: make <target>
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help dev build up down logs migrate seed test lint tf-init tf-plan tf-apply

## Print this help message
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Local Development ───────────────────────────────────────────────────────

dev: ## Start all services with hot-reload (dev mode)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

build: ## Build all production images
	docker compose build --no-cache

up: ## Start all services (production mode)
	docker compose up -d

down: ## Stop and remove containers
	docker compose down

logs: ## Tail all container logs
	docker compose logs -f

# ─── Database ────────────────────────────────────────────────────────────────

migrate: ## Run Alembic migrations
	docker compose exec backend alembic upgrade head

migrate-create: ## Create a new migration: make migrate-create MSG="add products"
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed the database with sample data
	docker compose exec backend python -m app.core.seed

# ─── Quality Gates (must pass before any push) ───────────────────────────────

test: ## Run full Pytest suite (against Docker postgres strands_test DB)
	docker compose exec -e TEST_DATABASE_URL=postgresql+asyncpg://$$POSTGRES_USER:$$POSTGRES_PASSWORD@postgres:5432/strands_test backend pytest tests/ -v --cov=app --cov-report=term-missing

lint: ## Lint & format backend
	docker compose exec backend ruff check app/ tests/
	docker compose exec backend ruff format app/ tests/ --check

typecheck: ## Mypy type check
	docker compose exec backend mypy app/ --ignore-missing-imports

# ─── Infrastructure (Terraform) ──────────────────────────────────────────────

tf-init: ## Initialise Terraform
	cd infrastructure/terraform && terraform init

tf-plan: ## Terraform plan (no apply)
	cd infrastructure/terraform && terraform plan -var-file=terraform.tfvars

tf-apply: ## Terraform apply — REVIEW PLAN FIRST
	cd infrastructure/terraform && terraform apply -var-file=terraform.tfvars

tf-destroy: ## Terraform destroy — DESTRUCTIVE, confirm first
	@echo "⚠️  This will DESTROY all infrastructure. Are you sure? [yes/no]"
	@read confirm; if [ "$$confirm" != "yes" ]; then echo "Aborted."; exit 1; fi
	cd infrastructure/terraform && terraform destroy -var-file=terraform.tfvars
