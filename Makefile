.PHONY: up down test load health

up:
	docker compose up --build

down:
	docker compose down

test:
	cd backend && pytest app/tests

health:
	curl http://localhost:8000/health

load:
	python scripts/load_test.py --users 50 --messages 500 --room demo
