SHELL := /bin/bash

APP_NAME := asn-by-country
IMAGE := $(APP_NAME):latest
OUTPUT_DIR := $(PWD)/output_data
ARGS ?=


# --------------------------
# Local Python Targets
# --------------------------

env: ## Create Python virtual environment
	python3 -m venv env

deps: env ## Install dependencies in virtual environment
	env/bin/pip install --upgrade pip
	env/bin/pip install -r requirements.txt

run: clean deps ## Run app locally using virtual environment
	env/bin/python main.py $(ARGS)

install: ## Install dependencies system-wide
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt


# --------------------------
# Docker Targets
# --------------------------

docker-build: ## Build Docker image
	docker build -t $(IMAGE) .

docker-run: docker-build ## Run app in Docker with host output folder
	mkdir -p $(OUTPUT_DIR)
	docker run --rm -v $(OUTPUT_DIR):/app/output_data $(IMAGE) $(ARGS)



# --------------------------
# Cleanup
# --------------------------

clean: ## Remove output folder
	rm -rf $(OUTPUT_DIR)

# --------------------------
# Help
# --------------------------

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --------------------------
# Defaults
# --------------------------

.PHONY: env deps run install clean docker-build docker-run help
.DEFAULT_GOAL := help
