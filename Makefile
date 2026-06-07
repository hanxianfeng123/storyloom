.PHONY: dev install test lint clean frontend-dev backend-dev docker-build docker-up docker-down

install:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

dev:
	@echo "Start backend:"; echo "  cd backend && uvicorn storyloom.api.app:app --reload --port 8000"
	@echo "Start frontend:"; echo "  cd frontend && npm run dev"
	@echo "Frontend at http://localhost:5173 (proxies /api to :8000)"

frontend-dev:
	cd frontend && npm run dev

backend-dev:
	cd backend && uvicorn storyloom.api.app:app --reload --port 8000

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check storyloom/ tests/

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name *.pyc -delete
