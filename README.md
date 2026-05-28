
## DATABASE MIGRATIONS
Para crear una nueva versión con los cambios ejecutar
uv run alembic revision --autogenerate -m "Comment"

Ejecutar los cambios en la base
uv run alembic upgrade head