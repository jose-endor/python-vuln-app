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

Use this when you want to hack on the code without rebuilding the image.

```bash
cd python-vuln-app
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export INVENTORY_DB_PATH=./data/inventory.db   # optional; default is under project data/
python -m run
```

Then open the same URLs as above. On **very new** Python versions, if a binary wheel is missing (for example for some database drivers), the app is written to work with **SQLite** as in the default `requirements.txt` flow. **Change port:** `export PORT=9000` then `python -m run`.

**Frontend:** The repo ships prebuilt static assets. To rebuild the React app yourself: `cd frontend && npm ci && npm run build` (output goes under `static/app/`, as used by the Flask app).

---

## Endor Labs (Python venv + call graph)

**What the message means:** If Endor cannot create a Python **virtualenv** for this package, **call graph** generation is skipped and you may see a generic *please create the venv before running a scan* line. The **real** reason is usually a few lines **above** in the same scan log—look for phrases like **`failed to create virtual environment`**, **`unable to install dependencies`**, **wrong Python / missing `poetry` on PATH**, **packaging layout** errors, etc. That line drives the one-line fix (toolchain version, missing tool, or bad manifest merge).

**This repo’s layout:** The **only** pip install manifest for the application is **`requirements.txt`**. Supplemental SCA “noise” lives under **`sca-corpus/`** and **`docker/sca-legacy`** (not extra root `requirements-*.txt` files) so scans do not merge impossible pins into one venv. **`.endorctl/scanprofile.yaml`** sets `ENDOR_SCAN_PYTHON_REQUIREMENTS=requirements.txt` for the same reason. This project is **pip + `requirements.txt`** (not Poetry); there is no `pyproject.toml` with `tool.poetry`—do not require `poetry` on the runner for this app.

**Runner / local `endorctl` checklist:** Use **Python 3.7+** (`python3 --version`); on the machine where the scan runs, **pip** must be able to install from `requirements.txt`. If you pre-create a venv in the project root, Endor can often reuse it:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Then re-run the scan for the project/branch. If the error persists, copy the **exact** `failed to create virtual environment: ...` (or `unable to install dependencies ...`) line from the log for diagnosis. For cloud scans, you can also set **`ENDOR_SCAN_PYTHON_REQUIREMENTS=requirements.txt`** on the project **Scan profile** in the Endor UI. More detail: [Python scanning](https://docs.endorlabs.com/scan/sca/python/).

---

## License / intent

Use only in isolated environments for security **research and product evaluation**. This is not a production application.
