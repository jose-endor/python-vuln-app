# Stack & Spine Bookstore

Online bookstore for browsing inventory, managing member accounts, and preparing order quotes. Includes a Flask API, React storefront, and SQLite persistence (optional remote DSN).

---

## Run with Docker (recommended)

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) with Compose (`docker compose` or `docker-compose`).

From the project root:

```bash
docker compose up --build
# or:
docker-compose up --build
```

| | |
|---|---|
| **App** | [http://127.0.0.1:3333/](http://127.0.0.1:3333/) |
| **Storefront (SPA)** | [http://127.0.0.1:3333/app](http://127.0.0.1:3333/app) |
| **Default port** | `3333` (loopback only in the default compose file) |

**Stop:** `Ctrl+C`, or `docker compose down` / `docker-compose down`.

**Different port:** set `PORT` under `environment` in `docker-compose.yml` and update the `ports` mapping (for example `127.0.0.1:9000:9000` with `PORT=9000`).

### Data and seeding

SQLite lives on a named volume at `/data` (`app_state` in compose). On first start with an empty database, users and catalog are imported from `data/users.json` and `data/inventory.json`. The `./data` folder is mounted read-only so you can edit those JSON files; to re-seed, remove the volume and start again:

```bash
docker compose down -v
docker compose up --build
```

### Seed accounts

From `data/users.json`:

| Username | Password |
|----------|----------|
| admin | admin |
| jordan | sunday |
| alex | hunter2 |

---

## Run locally (venv)

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export INVENTORY_DB_PATH=./data/inventory.db   # optional; default is under project data/
python -m run
```

Open the same URLs as above. Change port with `export PORT=9000` then `python -m run`.

**Frontend rebuild:** `cd frontend && npm ci && npm run build` (output under `static/app/`).

### Optional auth process

A separate auth process is available for local multi-service setups:

```bash
python -m run_auth
```

Defaults to port `5001`.

---

## Project layout

| Path | Role |
|------|------|
| `bookstore/` | Flask application |
| `frontend/` | React storefront (Vite) |
| `data/` | Seed JSON and local SQLite path |
| `static/app/` | Built SPA assets |
| `Dockerfile` / `docker-compose.yml` | Container build and local stack |

---

## License

See repository license terms. Intended for local development and evaluation of the Stack & Spine Bookstore stack.
