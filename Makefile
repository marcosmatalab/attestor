# `make check` runs exactly the gates CI runs, in the same order. If it passes here
# it passes there; that is the only reason this file exists.

.DEFAULT_GOAL := help
PYTHON ?= python

.PHONY: help install check lint format typecheck deadcode test demo ledger web clean

help:  ## Show this help
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "};{printf "  %-12s %s\n", $$1, $$2}'

install:  ## Install the package with its dev tooling, plus the frontend
	$(PYTHON) -m pip install -e ".[dev]"
	cd web && npm ci

lint:  ## Ruff lint
	ruff check .

format:  ## Ruff format check (includes Python blocks inside Markdown)
	ruff format --check .

typecheck:  ## mypy, strict
	mypy src/attestor

deadcode:  ## Vulture
	vulture src tests --min-confidence 80

test:  ## Pytest, with the coverage threshold
	pytest

check: lint format typecheck deadcode test  ## Every gate CI runs, in CI's order

demo:  ## Run the whole pipeline end to end (no keys, no network)
	attestor demo

ledger:  ## Verify the committed example ledger offline
	attestor ledger verify examples/ledger

web:  ## Frontend gates: lint, typecheck, build, vitest
	cd web && npm run lint && npm run typecheck && npm run build && npm test

clean:  ## Remove caches and build output
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage dist build web/.next web/out
