# Stack & Spine Bookstore (research)

**This repository is a deliberately vulnerable test application** built for **application security (AppSec)** tooling: static analysis, SCA, secret scanning, container policy checks, and related demos. It **must not** be exposed to the internet, used for real data, or treated as a secure baseline. Intentional weaknesses include insecure code paths, dependency choices, and configuration (including Docker and compose).

---

## Run with Docker (recommended)

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) with **Compose** available as either `docker compose` (plugin) or `docker-compose` (standalone).

From the project root:

```bash
docker compose up --build
# or, if the plugin is not available:
docker-compose up --build
```

- **App URL:** [http://127.0.0.1:3333/](http://127.0.0.1:3333/) (only listens on the loopback interface in the default compose file).
- **Storefront (SPA):** [http://127.0.0.1:3333/app](http://127.0.0.1:3333/app)
- **Stop:** `Ctrl+C` in the foreground terminal, or in another shell: `docker compose down` / `docker-compose down`.
- **Use another port:** set `PORT` in `docker-compose.yml` under `environment` and change the `ports` mapping (for example `127.0.0.1:9000:9000` with `PORT=9000`).

**First run / data:** The container keeps SQLite on a **named volume** at `/data` (`app_state` in compose). Seeded **users and catalog** come from `data/users.json` and `data/inventory.json` on first import when the database is empty. The `./data` folder is mounted read-only into the app so you can edit those JSON files; to **re-seed** from them, remove the named volume and start again, for example:

```bash
docker compose down -v
docker compose up --build
```

**Default test accounts** (from `data/users.json`): **admin** / **admin**, **jordan** / **sunday**, **alex** / **hunter2**.

---

## Run without Docker (local venv)

Useful for quick iteration and for tooling that scans a plain checkout — **SAST / SCA** use your manifests and source; **container scanners** use `Dockerfile` / compose regardless of how you run Python.

```bash
cd python-vuln-app
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export INVENTORY_DB_PATH=./data/inventory.db   # optional; default is under project data/
python -m run
```

Then open the same URLs as above. **Change port:** `export PORT=9000` then `python -m run`.

**Frontend:** To rebuild the React app: `cd frontend && npm ci && npm run build` (output goes under `static/app/`).

---

## License / intent

Use only in isolated environments for security **research and product evaluation**. This is not a production application.
