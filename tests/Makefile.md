.PHONY: help install lint format test cov api migrate clean

help:
	@echo "install  - pip install -e .[dev]"
	@echo "lint     - ruff check"
	@echo "format   - ruff format"
	@echo "test     - pytest"
	@echo "cov      - pytest with coverage"
	@echo "api      - run FastAPI dev server"
	@echo "migrate  - apply DB migrations"
	@echo "clean    - remove caches and build artifacts"

install:
	pip install -e ".[dev]"

lint:
	ruff check src tests

format:
	ruff format src tests
	ruff check --fix src tests

test:
	pytest -q

cov:
	pytest --cov=mss --cov-report=term-missing -q

api:
	uvicorn mss.api.app:create_app --factory --reload --host 0.0.0.0 --port 8000

migrate:
	python -c "from pathlib import Path; from mss.core.migrations import migrate; print('applied', migrate(Path('mss.db')))"

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov build dist *.egg-info
	find . -name __pycache__ -type d -prune -exec rm -rf {} +