# DevTalks Backend

FastAPI API for the DevTalks developer community. It uses PostgreSQL through
SQLAlchemy's async driver, Alembic migrations, Redis caching, and JWT
authentication.

## Run locally

To run the entire application with PostgreSQL and Redis in containers, follow
the root [Docker Compose instructions](../README.md).

1. Install Python 3.13 or newer and Poetry.
2. Start PostgreSQL and Redis.
3. Copy `.env.example` to `.env` and set a database URL and a strong secret key.
4. Install dependencies and apply migrations:

   ```powershell
   poetry install
   poetry run alembic upgrade head
   ```

5. Start the API:

   ```powershell
   poetry run uvicorn backend.main:app --reload
   ```

The latest Alembic migration creates default post categories when they are
missing so a new installation can publish posts immediately.
User avatars are normalized to WebP and stored in `AVATAR_STORAGE_DIR`; in
Docker Compose the persistent `avatars_data` volume is used automatically.

The API is available at `http://localhost:8000`; interactive OpenAPI
documentation is at `/docs`.

## Tests

Run the backend unit tests with:

```powershell
poetry run python -m unittest discover -s tests -v
```

See [BACKEND_AUDIT.md](../BACKEND_AUDIT.md) for implemented endpoints,
limitations, and audit findings.
