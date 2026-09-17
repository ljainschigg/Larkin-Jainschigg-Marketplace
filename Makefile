.PHONY: help setup serve clean generate publish

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Setup Python virtual environment and install dependencies
	python3 -m venv ./.venv
	./.venv/bin/pip install -r requirements.txt
	@echo "Setup complete! Use 'make serve' to start the documentation server."

serve: ## Serve documentation locally (requires setup)
	@if [ ! -d "./.venv" ]; then \
		echo "Virtual environment not found. Running setup first..."; \
		make setup; \
	fi
	./.venv/bin/mkdocs serve

clean: ## Clean up virtual environment
	rm -rf ./.venv

generate: ## Regenerate .claude-plugin/marketplace.json from plugins/
	python3 scripts/generate-marketplace.py

publish: ## Regenerate index, commit all pending changes, and push to main (m="msg")
	./scripts/publish.sh "$(m)"