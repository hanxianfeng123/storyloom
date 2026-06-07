.PHONY: dev install test lint clean

install:
	cd backend && pip install -e ".[dev]"

dev:
	cd backend && uvicorn storyloom.api.app:app --reload --port 8000

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check storyloom/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name *.pyc -delete
