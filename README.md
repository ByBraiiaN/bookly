
Bookly
======

Brief description
-----------------
Bookly is an async backend API for managing books and users. It is built with FastAPI and uses Alembic for database schema migrations.

Technologies
------------
- Python (async)
- FastAPI
- Uvicorn (ASGI server)
- Alembic (migrations)
- SQLAlchemy or async DB toolkit (ORM)
- Redis (optional, see `src/db/redis.py`)

Quick start (local)
-------------------
1. Create and activate a virtual environment:

	 ```bash
	 python -m venv .venv
	 source .venv/bin/activate
	 ```

2. Install dependencies:

	 - With Poetry:
		 ```bash
		 poetry install
		 ```

	 - Or with pip (if you have `requirements.txt`):
		 ```bash
		 pip install -r requirements.txt
		 ```

3. Set environment variables (example):

	 - `DATABASE_URL` — database connection string
	 - Other keys from `src/config.py`

4. Run database migrations (alembic.ini is at project root):

	 ```bash
	 alembic upgrade head
	 ```

Run the app (development)
-------------------------
Start the dev server with auto-reload:

```bash
uvicorn src:app --reload --host 0.0.0.0 --port 8000
```

Alembic quick commands
----------------------
- Create a new revision (autogenerate):
	```bash
	alembic revision --autogenerate -m "describe change"
	```
- Apply migrations:
	```bash
	alembic upgrade head
	```
- Roll back one revision:
	```bash
	alembic downgrade -1
	```

Useful commands
---------------
- Start dev server: `uvicorn src:app --reload --host 0.0.0.0 --port 8000`
- Run migrations: `alembic upgrade head`
- Create migration: `alembic revision --autogenerate -m "message"`
- Run tests (if present): `pytest`

Notes
-----
- The FastAPI app instance is defined in `src` (see `src/__init__.py`).
- Alembic manages schema changes — use migrations for production updates.

