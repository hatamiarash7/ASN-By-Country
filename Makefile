SHELL := /bin/bash
.DEFAULT_GOAL := help

# --------------------------
# Variables
# --------------------------
APP_NAME := asn-by-country
IMAGE := $(APP_NAME):latest
OUTPUT_DIR := $(PWD)/output_data
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
ARGS ?=

# Colors for pretty output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# --------------------------
# Development Environment
# --------------------------

.PHONY: env
env: ## Create Python virtual environment
	@echo -e "$(BLUE)Creating virtual environment...$(RESET)"
	python3 -m venv $(VENV)
	@echo -e "$(GREEN)Virtual environment created at $(VENV)$(RESET)"

.PHONY: deps
deps: env ## Install all dependencies (production + development)
	@echo -e "$(BLUE)Installing dependencies...$(RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	@echo -e "$(GREEN)Dependencies installed$(RESET)"

.PHONY: deps-prod
deps-prod: env ## Install production dependencies only
	@echo -e "$(BLUE)Installing production dependencies...$(RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo -e "$(GREEN)Production dependencies installed$(RESET)"

.PHONY: install
install: ## Install dependencies system-wide (not recommended)
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt

# --------------------------
# Running the Application
# --------------------------

.PHONY: run
run: ## Run the application (use ARGS="IR US" to specify countries)
	@if [ ! -d "$(VENV)" ]; then $(MAKE) deps; fi
	$(PYTHON) -m src.cli $(ARGS)

# --------------------------
# Code Quality
# --------------------------

.PHONY: lint
lint: ## Run all linters
	@echo -e "$(BLUE)Running linters...$(RESET)"
	$(VENV)/bin/ruff check src tests
	$(VENV)/bin/ruff format --check src tests
	@echo -e "$(GREEN)Linting complete$(RESET)"

.PHONY: format
format: ## Format code with ruff
	@echo -e "$(BLUE)Formatting code...$(RESET)"
	$(VENV)/bin/ruff format src tests
	$(VENV)/bin/ruff check --fix src tests
	@echo -e "$(GREEN)Formatting complete$(RESET)"

.PHONY: type-check
type-check: ## Run type checking with mypy
	@echo -e "$(BLUE)Running type checker...$(RESET)"
	$(VENV)/bin/mypy src tests
	@echo -e "$(GREEN)Type checking complete$(RESET)"

.PHONY: check
check: lint type-check ## Run all code quality checks

# --------------------------
# Testing
# --------------------------

.PHONY: test
test: ## Run tests with pytest
	@echo -e "$(BLUE)Running tests...$(RESET)"
	$(PYTEST) tests/ -v

.PHONY: test-fast
test-fast: ## Run tests without coverage (faster)
	$(PYTEST) tests/ -v --no-cov

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	@echo -e "$(BLUE)Running tests with coverage...$(RESET)"
	$(PYTEST) tests/ -v \
		--cov=src \
		--cov-report=term-missing \
		--cov-report=html:coverage_html \
		--cov-report=xml:coverage.xml \
		--cov-fail-under=70

.PHONY: test-junit
test-junit: ## Run tests with JUnit XML report
	@echo -e "$(BLUE)Running tests with JUnit report...$(RESET)"
	$(PYTEST) tests/ -v \
		--junitxml=junit.xml \
		--cov=src \
		--cov-report=xml:coverage.xml

.PHONY: test-all
test-all: test-cov test-junit ## Run all test configurations
	@echo -e "$(GREEN)All test reports generated$(RESET)"

# --------------------------
# Docker
# --------------------------

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo -e "$(BLUE)Building Docker image...$(RESET)"
	docker build -t $(IMAGE) .
	@echo -e "$(GREEN)Docker image built: $(IMAGE)$(RESET)"

.PHONY: docker-run
docker-run: docker-build ## Run app in Docker (use ARGS="IR" to specify countries)
	mkdir -p $(OUTPUT_DIR)
	docker run --rm -v $(OUTPUT_DIR):/app/output_data $(IMAGE) $(ARGS)

.PHONY: docker-shell
docker-shell: docker-build ## Open shell in Docker container
	docker run --rm -it --entrypoint /bin/bash $(IMAGE)

# --------------------------
# Cleanup
# --------------------------

.PHONY: clean
clean: ## Remove output files
	rm -rf $(OUTPUT_DIR)

.PHONY: clean-build
clean-build: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

.PHONY: clean-test
clean-test: ## Remove test artifacts
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf coverage_html/ .coverage coverage.xml junit.xml

.PHONY: clean-venv
clean-venv: ## Remove virtual environment
	rm -rf $(VENV)

.PHONY: clean-all
clean-all: clean clean-build clean-test clean-venv ## Remove all generated files
	@echo -e "$(GREEN)All generated files removed$(RESET)"

# --------------------------
# CI/CD Helpers
# --------------------------

.PHONY: ci
ci: deps check test-junit ## Run all CI checks

.PHONY: ci-fast
ci-fast: deps lint test-fast ## Run quick CI checks

# --------------------------
# Help
# --------------------------

.PHONY: help
help: ## Show this help message
	@echo -e "$(BLUE)ASN-By-Country Makefile$(RESET)"
	@echo ""
	@echo "Usage: make [target] [ARGS=...]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make run ARGS=\"IR US DE\"     Run scraper for Iran, USA, Germany"
	@echo "  make test-cov                 Run tests with coverage report"
	@echo "  make docker-run ARGS=\"IR\"    Run in Docker for Iran"
# --------------------------
# Defaults
# --------------------------

.PHONY: env deps run install clean docker-build docker-run help
.DEFAULT_GOAL := help
