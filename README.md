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

   The first time the app starts, it **seeds** a demo inventory (realistic mix of ~18 titles) into an empty database. If you still see the old two-row sample, stop the app, delete the SQLite file, and start again to pick up the new catalog and schema.

3. **Start the app** (listens on **127.0.0.1:3333** unless `PORT` is set)

   ```bash
   python -m run
   ```

4. **Open the UI:** [http://127.0.0.1:3333/](http://127.0.0.1:3333/) for the legacy Jinja home page, or the **React 17 + TypeScript** app at [http://127.0.0.1:3333/app](http://127.0.0.1:3333/app) (build with `cd frontend && npm ci && npm run build` before running, or use Docker, which bakes the SPA in). The SPA supports **register / login** against the database (passwords stored **in cleartext** on purpose). Seeded users: `admin` / `admin` and `demo` / `demo`. Other one‑click examples: `/sca` and `/sast/…`.

5. **Stop** with `Ctrl+C`.

**Change port:** `export PORT=9000` (then re‑run `python -m run`).

---

## Docker (full stack: app + PostgreSQL, “terrible on purpose”)

**Requires [Docker](https://docs.docker.com/get-docker/) and Compose** on your machine. From the project root:

```bash
docker compose up --build
```

**What you get (local only):**

| What | URL / port | Notes |
|------|------------|--------|
| Bookstore web UI + JSON API + `/app` SPA | **http://127.0.0.1:3333/** | Same routes as the venv run; **`DATABASE_URL`** points at the Postgres service. |
| Auth-only process (second container) | **http://127.0.0.1:5001/** | `auth-service` — `AUTH_SERVICE_MODE=1`, shared DB. |
| Optional nginx edge | **http://127.0.0.1:8080/** | Forwards to the monolith; another image to scan. |
| PostgreSQL | **127.0.0.1:5432** | **Weak, static password**; **5432 on the host** on purpose. Seeds `books` and `users` on first start. |
| `psycopg2-binary` | (library) | In the image for the DB driver; in `requirements.txt` for venv parity. |

**CRUD in Docker:** `GET /api/books` (search; still the **SQLi-relevant** string-built `WHERE` for vendors), `POST /api/books` (vulnerable string-built `INSERT`), and **`GET /api/books/<id>`** for a **parameterized** read of one row (more like a “real” REST read path). The UI loads the catalog from `GET /api/books` as before.

**Image / compose are intentionally bad** for AppSec and compliance demos: app runs as **root**, **Postgres is exposed to the host**, **plaintext creds in `environment:`** (and extra fake API keys), `seccomp:unconfined`, `cap_add`, `extra_hosts`, no app `HEALTHCHECK`, `chmod 777` in the Dockerfile, `apt` without `clean`, legacy `requirements-sca-legacy.txt` in the image, build args that look like tokens, and more. Read the comments in `Dockerfile` and `docker-compose.yml` before changing anything.

### Microservices-style services (more processes & manifests for tooling)

The stack is still one codebase, but you can point scanners at **several** listen addresses:

| What | Port (host) | Notes |
|------|-------------|--------|
| **API + labs + book CRUD + session auth** (monolith) | `3333` | `GET/POST` books, SCA/SAST, `/app` SPA, `/api/auth/*` on the same process. `BIND_ALL=1` in compose for `0.0.0.0` inside the container. |
| **Auth-only** “microservice” (same image, `AUTH_SERVICE_MODE=1`) | `5001` | Only auth routes + `GET /health`, `GET /readyz` — extra dependency graph, SBOM, and DAST target without shipping the whole lab surface. `python -m run_auth` |
| **Postgres** | `5432` | Shared by both app processes; `users` and `books` tables, seed data on init. |
| **Optional edge** (nginx → monolith) | `8080` | `edge-nginx` proxies to the monolith; extra container image, volume‑mounted `deploy/nginx-insecure-research.conf`. |

The `Dockerfile` is **multi‑stage** (Node **18** builds the Vite 2 + React 17 + TypeScript 4.9 app into `static/app/`, then the Python image copies it). User CRUD‑ish flows include: **register**, **list users** (`GET /api/users?…` — SQLi‑ready `LIKE` builder), and **`GET /api/exposed/users`** when `ALLOW_EXPOSED_USERS=1` (dumps creds for abuse‑case tools).

**Kubernetes:** multi‑file example manifests live under `k8s/`: `00-research-namespace.yaml` first, then ConfigMap, Secrets, Postgres, **bookstore** Deployment/Service, **auth** Deployment/Service, and an **Ingress** with research‑only annotations. A deliberately extreme one‑file sample remains as `k8s/deployment-insecure.yaml` for policy demos. **Do not** apply any of this to a real cluster without isolating a lab namespace.

**Apply (lab only):** `kubectl apply -f k8s/00-research-namespace.yaml` then `kubectl apply -f k8s/research-*.yaml` — set the `image:` in `k8s/research-bookstore-deployment.yaml` and `k8s/research-auth-deployment.yaml` to an image you built and loaded into the cluster.

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

## 2) SAST — 10+ “hard” issues (multi‑source, propagation, indirect sinks)

Many findings are **CWE**‑shaped. Flows on purpose cross **`sources` → `propagation` / `sync` → `sinks`**, and several routes merge **more than one** of `{query, JSON, headers, raw body, cookies}` so shallow single‑file regex engines miss the sink.

| # | Theme / CWE (typical) | Why it is “harder” | Entry point (examples) |
|---|------------------------|--------------------|------------------------|
| 1 | Merged `eval` (CWE‑95) | `strip_noise` on one operand + ordered merge of `p1`…`p3` | `GET /sast/merged_eval?p1=&p2=&p3=` |
| 2 | Pickle / merged b64 (CWE‑502) | two base64 halves concatenated pre‑`loads` | `GET /sast/merged_pickle?a=&b=` |
| 3 | `marshal` loads (CWE‑502) | `interleave` reorders two halves of one blob | `GET /sast/merged_marshal?a&b&order=` |
| 4 | `subprocess` + shell (CWE‑78) | JSON `a` / `b` joined at the sink (no route‑local quote) | `POST /sast/merged_subprocess` body `{"a":…,"b":…}` |
| 5 | Path / LFI (CWE‑22) | `tuple_join` of `a`,`b` plus a third `ext` segment | `GET /sast/lfi?a=&b=&ext=` |
| 6 | Open redirect (CWE‑601) | `a` + `b` merged, passed to `redirect` | `GET /sast/redirect?a=&b=` |
| 7 | SSTI / Jinja (CWE‑1336) | `a` + `b` + `c` merged before `from_string` | `POST /sast/merged_jinja` |
| 8 | `lxml` on raw XML (CWE‑91 / 611 class) | POST body only | `POST /sast/lxml` |
| 9 | `xml.etree` parse (stdlib) | same story, different module path | `POST /sast/stdlib_xml` |
| 10 | SSRF, triple URL (CWE‑918) | `s` + `h` + `p` reassembled in one sink that calls `requests` | `GET /sast/triple_url?s=&h=&p=` |
| 11 | SSRF, `httpx` + `asyncio.run` (CWE‑918) | **different** HTTP stack and async entry | `GET /sast/aio_merged?a&b` |
| 12 | SSRF, `urllib.request` (CWE‑918) | stdlib client, merged URL | `GET /sast/urllib_merged?a&b` |
| 13 | Log injection / secrets in logs (CWE‑532) | password field sent to a logger with `%r` | `POST /sast/cred_log` JSON `{"u":…,"p":…}` |
| 14 | `getattr(__builtins__, …)` (CWE‑95 class) | indirect dynamic call | `GET /sast/builtin?n=…&c=…` |
| 15 | `importlib` + tainted `module:attr` (CWE‑95 / 20) | dotted string split in sink | `GET /sast/import_dotted?d=…` |
| 16 | Charset + merge (CWE‑20 chain) | base64 → `charset_normalizer` after merge (SCA+SAST) | `GET /sast/charset_chain?b64=…` |

**Discoverability index:** `GET /sast/index` (JSON list of the routes above).

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
| 14 | Optional **third** service image (nginx) | `edge-nginx` in `docker-compose.yml` |
| 15 | Volume‑mount of permissive `nginx` config on edge | `deploy/nginx-insecure-research.conf` |

(Use your vendor’s “policy / benchmark” name when you file tickets — the exact rule IDs differ.)

---

## License / intent

Use only for **security research** and product evaluation. Add a `LICENSE` file (for example MIT) if you need a formal license line.
