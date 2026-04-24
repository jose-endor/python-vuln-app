# Python Vulnerable Bookstore (Research Only)

**Run only on your machine (for example `http://127.0.0.1:3333`) inside a throwaway venv or container.** This app is intentionally unsafe for **stress‑testing SCA, SAST, secret scanners, and container compliance tools**.

---

## Quick start (3 steps)

1. **Create a virtual environment and install dependencies**

   ```bash
   cd python-vuln-app
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   On **CPython 3.14+**, `psycopg2-binary` is omitted from the resolver (no wheel yet), so a **local** venv only talks to **SQLite** — that is enough for the app. Use **Docker** if you want the **PostgreSQL** stack on your machine.

2. **(Optional) Put the SQLite file where you like**

   ```bash
   export INVENTORY_DB_PATH=./data/inventory.db
   ```

   On first start with an empty database, the app **imports** rows from `data/inventory.json` and `data/users.json`. If you have an old SQLite file, remove it to re-seed, or run against Postgres in Docker.

3. **Start the app** (listens on **127.0.0.1:3333** unless `PORT` is set)

   ```bash
   python -m run
   ```

4. **Open the shop:** the floor display at [http://127.0.0.1:3333/](http://127.0.0.1:3333/) and the member view at [http://127.0.0.1:3333/app](http://127.0.0.1:3333/app) (Vite 2 + React 17 + TS; build with `cd frontend && npm ci && npm run build` locally, or use Docker, which bakes the SPA in). Seeded logins are loaded from **`data/users.json`** (defaults: **admin** / **admin**, **jordan** / **sunday**, **alex** / **hunter2**). The catalog seed comes from **`data/inventory.json`**; both are read into the DB on **first** init when the DB is empty. (For evaluators: static analysis–heavy and dependency demo routes are still in the **backend** — e.g. `/v1/ops/…` (legacy back-office) and `/sca/…` — the storefront UIs are plain bookstore copy.)

5. **Stop** with `Ctrl+C`.

**Change port:** `export PORT=9000` (then re‑run `python -m run`).

**SCA / CI (`npm`, reachability):** The committed `frontend/package-lock.json` must list **`https://registry.npmjs.org/`** in `resolved` fields, not a corporate or vendor proxy (proxy URLs in the lock will often trigger **`npm ERR! 401`** in clean sandboxes). The repo includes **`frontend/.npmrc`** and a root **`.npmrc`** pinning the public registry. A root **`package.json` / `package-lock.json`** pair exists only as metadata (no root JS deps); the installable app is under **`frontend/`** (`npm ci` + `npm run build` there). If your machine rewrote the lock, run: `cd frontend && rm -rf node_modules package-lock.json && npm install` and commit the new lock.

---

## Docker (full stack: app + PostgreSQL, “terrible on purpose”)

**Requires [Docker](https://docs.docker.com/get-docker/) and Compose** on your machine. From the project root:

```bash
docker compose up --build
```

**What you get (local only):**

| What | URL / port | Notes |
|------|------------|--------|
| **One** app process (web + API + lab routes + `/app` SPA) | **http://127.0.0.1:3333/** | **`DATABASE_URL`** → Postgres; **`./data` mounted read-only** so you can edit `data/inventory.json` and `data/users.json` and wipe the DB to re-seed. |
| PostgreSQL | **127.0.0.1:5432** | **Weak, static password**; **5432 on the host** on purpose. |
| `psycopg2-binary` | (library) | In the image for the DB driver. |
| Optional: second auth-only process | (manual) | `python -m run_auth` on **5001** with `AUTH_SERVICE_MODE=1` — not started by `docker compose` by default. |
| Optional: nginx | `deploy/nginx-insecure-research.conf` | **Not** used in compose; add your own service if you want a front proxy. |

**CRUD in Docker:** `GET /api/books` (search; still the **SQLi-relevant** string-built `WHERE` for vendors), `POST /api/books` (vulnerable string-built `INSERT`), and **`GET /api/books/<id>`** for a **parameterized** read of one row (more like a “real” REST read path). The UI loads the catalog from `GET /api/books` as before.

**Image / compose are intentionally bad** for AppSec and compliance demos: app runs as **root**, **Postgres is exposed to the host**, **plaintext creds in `environment:`** (and extra fake API keys), `seccomp:unconfined`, `cap_add`, `extra_hosts`, no app `HEALTHCHECK`, `chmod 777` in the Dockerfile, `apt` without `clean`, legacy `requirements-sca-legacy.txt` in the image, build args that look like tokens, and more. Read the comments in `Dockerfile` and `docker-compose.yml` before changing anything.

### Docker layout: monolith + Postgres (compose)

- **`docker compose up --build`:** `postgres` + one **`vulnerable-bookstore`** container. No extra auth or nginx services.
- **Seed data:** `data/inventory.json` and `data/users.json` (three accounts including **admin** / **admin**). Edit those files, reset the database volume, and start again to pick up a new first-run seed.
- **`Dockerfile` multi‑stage:** Node **18** builds the Vite 2 + React 17 + TypeScript storefront into `static/app/`, then the Python image copies it.
- **Evaluators only:** HTTP APIs that are not part of the normal shopping flow (`GET /api/users?…`, `/api/exposed/users` with env flag, back-office/legacy at `/v1/ops/…`, SCA at `/sca/…`) are unchanged; they are not linked from the shop UIs.
- **Optional:** run **`python -m run_auth`** locally for a tiny `AUTH_SERVICE_MODE=1` listen on `5001` (same codepath, not part of compose by default).
- **Kubernetes** (`k8s/research-*.yaml`): one **bookstore** deployment + Postgres + single-host ingress (auth-only manifests removed to match compose). A deliberately bad one‑file sample is still `k8s/deployment-insecure.yaml`. **Do not** apply in production clusters.

**Apply (lab only):** `kubectl apply -f k8s/00-research-namespace.yaml` and `kubectl apply -f k8s/research-*.yaml` — set `image:` in `k8s/research-bookstore-deployment.yaml` to a built image.

---

## 1) SCA — 10+ reachable dependency call sites (SBOM / reachability)

Each row is a **different package** with an **intentionally dated** line in `requirements.txt` (or `requirements-sca-legacy.txt` in Docker). The code **imports and calls** the library in `bookstore/sinks/sca_stubs.py` and exposes it from **`GET /sca/run?k=…`**.

| # | `k` (for `/sca/run?k=`) | Package (examples) | Notes |
|---|------------------------|--------------------|--------|
| 1 | `urllib3` | urllib3 | `PoolManager().request` |
| 2 | `requests` | requests | `requests.get` |
| 3 | `certifi` | certifi | `certifi.where` |
| 4 | `idna` | idna | `idna.encode` |
| 5 | `charset_normalizer` | charset-normalizer | `from_bytes` (alias `charset_normalizer`) |
| 6 | `pyyaml` | PyYAML | `yaml.safe_load` |
| 7 | `pillow` | Pillow | `PIL.Image.open` |
| 8 | `lxml` | lxml | `lxml.etree.fromstring` |
| 9 | `markdown` | Python‑Markdown | `markdown.markdown` |
| 10 | `ecdsa` | ecdsa | signing key / curve (see stub) |
| 11 | `cryptography_fernet` | cryptography | `Fernet` (also wired from `bookstore/sinks/crypto_sink.py`) |
| 12 | `paramiko` | paramiko | host key / RSA (SSH stack) |
| 13 | `redis` | redis | `from_url` client pool (no local Redis required for a graph hit) |
| 14 | `pycryptodomex` | pycryptodomex | `ARC4` |
| 15 | `jose` | python‑jose | unverified header parse (JWT) |
| 16 | `httpx` | httpx | `AsyncClient` + `asyncio.run` (async HTTP different from `requests` graph) |
| 17 | `protobuf` | protobuf | `empty_pb2.Empty` `Serialize` / `Parse` |
| 18 | `ujson` | ujson | C JSON encode/decode |
| 19 | `werkzeug` | Werkzeug | `gen_salt` |
| 20 | `jinja2` | Jinja2 | small template (escape on) |
| 21 | `itsdangerous` | itsdangerous | `URLSafeSerializer` |
| 22 | `click` | click | `click.unstyle(click.style(…))` |
| 23 | `blinker` | blinker | `blinker.signal` |
| 24 | `flask_markupsafe` | Flask, MarkupSafe | version / Markup (both appear in the graph) |

**Discovery:** `GET /sca` returns the list of `k` values. Many handlers accept a query like `u=` (URL), `b64=`, `md=`, `t=`, or `json=`; see the handler map in `bookstore/routes/sca_demos.py`. **You should expect CVEs / advisories to vary** by the exact version your resolver installs; compare **host venv** vs **Docker** legacy file.

**Also in the app (used on non‑`/sca` paths):** **Flask**, **Werkzeug**, **Jinja2**, **PyYAML** (`unsafe_load` in `bookstore/sinks/yaml_sink.py` — SAST as well as SCA), **Pillow** (`read_cover_meta`), **lxml** / **markdown** in labs and `/util/bridge`, **cryptography** and **ecdsa** on `/util/*` curve/seal examples.

---

## 2) Challenging static analysis — 10+ “hard” issues (multi‑source, propagation, indirect sinks)

Many findings are **CWE**‑shaped. Flows on purpose cross **`sources` → `propagation` / `sync` → `sinks`**, and several routes merge **more than one** of `{query, JSON, headers, raw body, cookies}` so shallow single‑file regex engines miss the sink.

| # | Theme / CWE (typical) | Why it is “harder” | Entry point (examples) |
|---|------------------------|--------------------|------------------------|
| 1 | Merged `eval` (CWE‑95) | `strip_noise` on one operand + ordered merge of `p1`…`p3` | `GET /v1/ops/finance_preview?p1=&p2=&p3=` |
| 2 | Pickle / merged b64 (CWE‑502) | two base64 halves concatenated pre‑`loads` | `GET /v1/ops/restore_b64?a=&b=` |
| 3 | `marshal` loads (CWE‑502) | `interleave` reorders two halves of one blob | `GET /v1/ops/restore_marshal?a&b&order=` |
| 4 | `subprocess` + shell (CWE‑78) | JSON `a` / `b` joined at the sink (no route‑local quote) | `POST /v1/ops/receipt_echo` body `{"a":…,"b":…}` |
| 5 | Path / LFI (CWE‑22) | `tuple_join` of `a`,`b` plus a third `ext` segment | `GET /v1/ops/shelf_excerpt?a=&b=&ext=` |
| 6 | Open redirect (CWE‑601) | `a` + `b` merged, passed to `redirect` | `GET /v1/ops/vendor_redirect?a=&b=` |
| 7 | SSTI / Jinja (CWE‑1336) | `a` + `b` + `c` merged before `from_string` | `POST /v1/ops/jacket_preview` |
| 8 | `lxml` on raw XML (CWE‑91 / 611 class) | POST body only | `POST /v1/ops/ingest_xml_lxml` |
| 9 | `xml.etree` parse (stdlib) | same story, different module path | `POST /v1/ops/ingest_xml_stdlib` |
| 10 | SSRF, triple URL (CWE‑918) | `s` + `h` + `p` reassembled in one sink that calls `requests` | `GET /v1/ops/vendor_status?s=&h=&p=` |
| 11 | SSRF, `httpx` + `asyncio.run` (CWE‑918) | **different** HTTP stack and async entry | `GET /v1/ops/vendor_status_aio?a&b` |
| 12 | SSRF, `urllib.request` (CWE‑918) | stdlib client, merged URL | `GET /v1/ops/vendor_status_urllib?a&b` |
| 13 | Log injection / secrets in logs (CWE‑532) | password field sent to a logger with `%r` | `POST /v1/ops/login_diagnostics` JSON `{"u":…,"p":…}` |
| 14 | `getattr(__builtins__, …)` (CWE‑95 class) | indirect dynamic call | `GET /v1/ops/builtin_lookup?n=…&c=…` |
| 15 | `importlib` + tainted `module:attr` (CWE‑95 / 20) | dotted string split in sink | `GET /v1/ops/module_dotted?d=…` |
| 16 | Charset + merge (CWE‑20 chain) | base64 → `charset_normalizer` after merge (SCA+SAST) | `GET /v1/ops/encoding_sanity?b64=…` |

**Discoverability index:** `GET /v1/ops/capabilities` (JSON list of the `v1/ops` routes above; implementation: `bookstore/routes/ops_diagnostics.py`, `bookstore/sinks/legacy_batch_bridge.py`).

**“Classic” flows (still in the app, multi‑file):** SQLite injection (`/api/books` — `search_pipeline` → `db_sink`), command execution (`/util/backup` → `shell_sink`), SSRF v1 (`/util/fetch` + `url_pipeline` → `http_client_sink`), SSTI admin (`/admin/preview` → `jinja_sink`), reflected XSS (`/echo` — `|safe` in a template string), `yaml.unsafe_load` on `/admin/ingest` (`yaml_sink`), ReDoS (`/lab/redos` through `regex_chain` → `regex_sink`), and indirect `/util/bridge?kind=…` (`dispatch_merge` → `markdown` / lxml `fragment`).

---

## 3) Container / image / compose — 10+ intentional misconfigurations

What to point CIS / Trivy / KSPM / kube‑linters at in **this** repo (details also in file comments):

| # | What scanners flag | Where |
|---|----------------------|--------|
| 1 | `USER` not dropped to a non‑privileged uid | `Dockerfile` (implicit root + compose `user: 0:0`) |
| 2 | “Secrets” in `ENV` / `ARG` | `ARG INSECURE_BUILD_ARG`, `EXTRA_BAD_TOKEN`, `LEAKED_BUILD_ENV` |
| 3 | `FLASK_DEBUG=1` in a shipped image | `ENV` in `Dockerfile` and compose `environment` |
| 4 | PIP / layer hygiene (`PIP_NO_CACHE_DIR=0`, `COPY` plus Node `npm ci` in another stage) | `Dockerfile` (multi-stage) |
| 5 | Stale / fat base (`python:…-slim` without an explicit hardening / refresh pass) | `FROM` line |
| 6 | `apt` install with **no** `apt-get clean` / `rm` of `lists` | `RUN apt-get` block |
| 7 | Over‑broad `chmod` (`777`) on a persistent directory | `chmod 777` on `/data` and `/tmp/sandbox` |
| 8 | Extra packages in runtime (curl) | `apt-get install` |
| 9 | No `HEALTHCHECK` | (deliberately omitted) |
| 10 | `seccomp:unconfined` and extra `cap_add` in compose | `docker-compose.yml` `security_opt`, `cap_add` |
| 11 | `extra_hosts` (suspicious override pattern) | `extra_hosts` |
| 12 | Plaintext env blocks for service keys in compose | `API_KEY_CART=…` |
| 13 | Very high ulimits (DoS / blast‑radius in some baselines) | `ulimits.nproc` |
| 14 | Optional unmounted nginx recipe (not in compose) | `deploy/nginx-insecure-research.conf` |
| 15 | `docker compose` **bind‑mounts** `./data` into the app | Lets you change JSON seed files in place (still need empty DB to reapply seed) |

(Use your vendor’s “policy / benchmark” name when you file tickets — the exact rule IDs differ.)

---

## License / intent

Use only for **security research** and product evaluation. Add a `LICENSE` file (for example MIT) if you need a formal license line.
