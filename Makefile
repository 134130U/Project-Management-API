run:
	docker compose up --build

test:
	pytest

down:
	docker compose down