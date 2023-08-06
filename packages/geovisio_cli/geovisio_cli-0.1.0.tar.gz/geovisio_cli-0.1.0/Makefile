.DEFAULT_GOAL := help

.PHONY: docs test type-check fmt ci

test: ## Run tests
	pytest

type-check: ## Check all python types
	mypy geovisio_cli/

fmt: ## Format code
	black --fast .

ci: type-check fmt test ## Run all check like the ci

docs:  ## Generates documentation from Typer embedded docs
	python -m typer_cli ./geovisio_cli/main.py utils docs --name geovisio --output USAGE.md

help: ## Print this help message
	@grep -E '^[a-zA-Z_-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
