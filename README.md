# FastAPI Service Template

A production-ready template for building FastAPI microservices.

- **Runtime:** Python 3.15, FastAPI, Uvicorn
- **Data:** native SQL over async SQLAlchemy Core + asyncpg, Alembic raw-SQL migrations, PostgreSQL with native `uuid` keys (no ORM)
- **Architecture:** layered `domain → service → repository → db`, with a generic `BaseRepository` CRUD contract
- **Config:** `pydantic-settings` (12-factor, `.env` support)
- **Observability:** structured JSON logging via `structlog`, request IDs
- **Quality:** Ruff (lint + format), mypy (strict), pytest + coverage
- **Ops:** Dockerfile (multi-stage, non-root), Docker Compose, GitHub Actions CI
- **Tooling:** [uv](https://docs.astral.sh/uv/) for deps, [mise](https://mise.jdx.dev/) for tool versions & tasks

## Project layout

```
.
├── src/
│   ├── app.py               # app factory + ASGI entrypoint
│   ├── core/                # config, logging, errors, middleware, pagination, BaseRepository
│   ├── db/                  # concrete persistence infra: async engine + session
│   ├── internal/            # internal domain: metadata + health probes
│   │   ├── router.py
│   │   ├── handlers/
│   │   └── models/
│   └── items/               # example domain
│       ├── router.py        # wires paths to handlers
│       ├── handlers/        # one module per endpoint
│       ├── service.py       # business logic (thin layer over the repository)
│       ├── repository.py    # ItemRepository: native SQL + transactions
│       ├── models/          # Pydantic request/response models
│       └── dependencies.py
├── migrations/              # Alembic environment + raw-SQL versions
├── tests/                   # pytest suite (mirrors the domain layout)
├── Dockerfile / compose.yaml
└── pyproject.toml           # deps + tool config
```

**Layering rule:** `domain → service → repository → db`. Each domain lives in
its own `src/<domain>/` package: the router/handlers stay thin, the service
holds business logic and delegates persistence to a repository, and the
repository owns the hand-written SQL and its transactions. Rows are mapped
straight into Pydantic models. There is **no ORM** — see `AGENTS.md` for the
native-SQL conventions.

## Getting started

```bash
mise install        # install Python 3.15 + uv
mise run sync       # create .venv and install dependencies
cp .env.example .env
mise run db:up      # start Postgres (Docker Compose)
mise run migrate    # apply migrations
mise run dev        # http://localhost:8000/docs
```

Run the whole stack (API + Postgres) with Docker:

```bash
mise run docker:up
```

## Common tasks

| Task | Command |
| --- | --- |
| Install/refresh deps | `mise run sync` |
| Dev server | `mise run dev` |
| Lint | `mise run lint` |
| Format | `mise run format` |
| Autofix | `mise run fix` |
| Type check | `mise run typecheck` |
| Tests | `mise run test` |
| Everything | `mise run check` |
| Start/stop Postgres | `mise run db:up` / `db:down` |
| New migration | `mise run revision "add foo"` |
| Apply migrations | `mise run migrate` |

Without mise, the equivalents are `uv run <tool>` (e.g. `uv run pytest`).

## Testing

Tests run against a **real PostgreSQL database** (no SQLite). Start one first
with `mise run db:up`, then:

```bash
mise run test
```

The connection is taken from `TEST_DATABASE_URL` (default
`postgresql+asyncpg://postgres:postgres@localhost:5432/app_test`). The schema is
built by applying the Alembic migrations, so the suite also validates them.

Repositories are exercised through an `item_repository` fixture that is
parametrized over **both** the Postgres `ItemRepository` and an in-memory test
double, so a single CRUD suite holds the two implementations to the same
behaviour.

## Configuration

All settings live in `src/core/config.py` and are read from environment
variables. See `.env.example` for the full list. Key variables:

| Variable | Default | Description |
| --- | --- | --- |
| `ENVIRONMENT` | `local` | `local`, `staging`, or `production` |
| `DEBUG` | `false` | Enables SQL echo and debug mode |
| `LOG_LEVEL` | `INFO` | Root log level |
| `LOG_JSON` | `true` | JSON logs (`false` for pretty console) |
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `postgres`/`postgres`/`app` | Credentials |

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Service metadata |
| GET | `/health/live` | Liveness probe |
| GET | `/health/ready` | Readiness probe (checks DB) |
| GET/POST | `/api/v1/items` | List / create items |
| GET/PATCH/DELETE | `/api/v1/items/{id}` | Read / update / delete an item |
| GET | `/docs`, `/redoc`, `/openapi.json` | API docs |

## License

MIT
