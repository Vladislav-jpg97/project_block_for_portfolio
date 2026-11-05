dev:
	poetry run uvicorn backend.main:app --reload

migrate:
	poetry run alembic revision --autogenerate -m "$(m)"
#make migrate m="create init tables"
head:
	poetry run alembic upgrade head
