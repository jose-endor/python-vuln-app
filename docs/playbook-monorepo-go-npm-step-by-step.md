# Playbook: AppSec Corpus Monorepo (Go + npm) — Step by Step

**Use this doc in Google Docs:** copy sections into a new Doc, or upload this file to Drive and open with Google Docs.

**Goal:** Greenfield monorepo — Go API, npm UI, OpenAPI contract, Docker — **builds clean, runs locally and in containers.**

**For each step:** open a **new Cursor Agent chat** (or fresh session), paste the **Agent prompt** block, wait until acceptance checks pass, then go to the next step.

**Suggested new repo name:** `appsec-corpus` (or your choice — replace `APPSEC_CORPUS` below).

---

## Before you start (human checklist)

| Item | Your choice (fill in) |
|------|------------------------|
| GitHub org/repo | |
| Local path | e.g. `~/demo/appsec-corpus` |
| Go version | 1.22+ |
| Node version | 20 LTS |
| Product domain | Support ticketing + attachments + webhooks (default) |

---

## Step 1 — Create empty repo + Prompt 0 (charter)

### You do (terminal)
```bash
mkdir -p ~/demo/appsec-corpus && cd ~/demo/appsec-corpus
git init
```

### Agent prompt — paste into Cursor

```
Create README.md and SECURITY.md for a new monorepo named "appsec-corpus".

Purpose: intentionally vulnerable lab application for AppSec tool evaluation (SAST, SCA, secrets, containers). NOT for production or public internet without warnings.

Architecture decisions (lock these in README):
- Backend: 100% Go (apps/api-go)
- Frontend: npm Vite + React + TypeScript (apps/web)
- Contract: OpenAPI 3.1 in spec/openapi.yaml (future PHP/Java backends must match)
- Runs: local dev + Docker Compose

README must include:
- One-paragraph product description (support ticketing + attachments + webhooks)
- "Lab use only" disclaimer
- Placeholder sections: Quick start, Local dev, Docker, Corpus, Porting

SECURITY.md: clear warning about intentional vulnerabilities.

Do not scaffold code yet — only these two docs plus a minimal .gitignore (Go, node, .env).
```

### Verify
- [ ] `README.md` and `SECURITY.md` exist
- [ ] Product domain is stated

---

## Step 2 — Monorepo scaffold (Prompt 1)

### Agent prompt — paste into Cursor

```
Scaffold the monorepo layout. Everything must build on a clean machine.

Create:

/spec/openapi.yaml          # minimal placeholder with /healthz only
/corpus/matrix.yaml         # empty list: entries: []
/apps/api-go/
  cmd/server/main.go        # HTTP server :8080, GET /healthz -> {"ok":true}
  go.mod                    # module: github.com/ORG/appsec-corpus (use sensible path)
  Makefile                  # targets: lint, test, build, run, ci
  .golangci.yml
/apps/web/
  Vite + React + TypeScript
  package.json scripts: dev, build, preview
  .env.example: VITE_API_BASE_URL=http://localhost:8080
  Simple page: button fetches GET /healthz and shows result
/integration/README.md      # "tests added in step 8"
/deploy/
  Dockerfile.api            # placeholder OK for now
  Dockerfile.web
  docker-compose.yml        # api + web services
/docs/triggers.md           # placeholder
/docs/PORTING.md            # placeholder
Makefile at repo root: api, web, ci, compose-up, compose-down

Go: use chi or net/http. go test ./... must pass (even if minimal).

Acceptance:
- cd apps/api-go && make ci
- cd apps/web && npm ci && npm run build
- make run (or document cd apps/api-go && make run) then curl localhost:8080/healthz
```

### Verify (terminal)
```bash
cd apps/api-go && make ci
cd ../web && npm ci && npm run build
cd ../.. && curl -s http://localhost:8080/healthz   # after starting API
```

- [ ] Go CI passes
- [ ] Web build passes
- [ ] `/healthz` returns OK

---

## Step 3 — Product + route plan (Prompt 2)

### Agent prompt — paste into Cursor

```
Read README.md. Write product and route planning docs (no OpenAPI yet).

Create docs/PRODUCT.md:
- Actors: anonymous, user, admin, system/webhook
- Entities: User, Session, Ticket, Comment, Attachment, WebhookDelivery
- 8-10 user stories (realistic B2B support desk)

Create docs/ROUTE_PLAN.md:
- Table columns: group | method | path | auth | purpose | corpus_notes
- Minimum 18 endpoints across public, user, admin, util
- Include: auth login/logout, ticket CRUD, search, attachment upload/download, admin user list, webhook ingest + replay, healthz/readyz
- Mark at least 8 rows as "corpus candidate" (SQLi, XSS, SSRF, path traversal, cmd injection, deserialization, IDOR, secrets in logs, etc.)

Create docs/ARCHITECTURE.md:
- Package list for apps/api-go/internal/: httpapi, domain, repo, auth, integration, workers, corpus/{sources,propagation,sinks,noise}

Do not implement new handlers beyond /healthz yet.
```

### Verify
- [ ] `docs/PRODUCT.md`, `docs/ROUTE_PLAN.md`, `docs/ARCHITECTURE.md` exist
- [ ] ≥18 endpoints planned

---

## Step 4 — OpenAPI contract (Prompt 3)

### Agent prompt — paste into Cursor

```
Implement spec/openapi.yaml (OpenAPI 3.1) from docs/ROUTE_PLAN.md.

Rules:
- Every operation has unique operationId (camelCase)
- components/schemas for shared models
- securitySchemes: session cookie (primary) and optional bearer
- Paths for ALL rows in ROUTE_PLAN (including /healthz, /readyz)
- For corpus-candidate routes add: x-corpus-refs: [{ cwe, mode, matrixId }] with placeholder matrixIds

Create docs/openapi-operations.md: table operationId | method | path | auth | tags

Add npm script or doc command to lint OpenAPI (redocly or spectral).

Do not change Go handlers yet except stubs if needed for compile — focus on spec accuracy.
```

### Verify
```bash
npx -y @redocly/cli lint spec/openapi.yaml
```
- [ ] OpenAPI lints clean
- [ ] Every route in ROUTE_PLAN appears in spec

---

## Step 5 — Go API implements OpenAPI (Prompt 4)

### Agent prompt — paste into Cursor

```
Implement apps/api-go to satisfy spec/openapi.yaml exactly.

Structure:
- cmd/server/main.go
- internal/httpapi/ (router, middleware: request ID, logging, recovery)
- internal/domain/
- internal/repo/ (SQLite with modernc.org/sqlite or database/sql)
- internal/auth/ (session for demo: user@lab.local / admin@lab.local — document in README)
- internal/integration/ (outbound HTTP client)
- internal/workers/ (simple ticket export or webhook retry worker)
- internal/corpus/{sources,propagation,sinks,noise}/ — empty packages OK

Requirements:
- Migrations + seed data (2 users, few tickets)
- /readyz checks DB
- JSON errors: { "error", "requestId" }
- NO routes outside OpenAPI
- go test ./... passes; make ci passes

Update README: env vars, make run, default ports.
```

### Verify
```bash
cd apps/api-go && make ci && make run
# another terminal:
curl -s http://localhost:8080/healthz
curl -s http://localhost:8080/readyz
# exercise login + list tickets per README
```
- [ ] All tests pass
- [ ] Happy-path flows work for main product routes (not corpus yet)

---

## Step 6 — Corpus matrix + vulnerable flows (Prompt 5)

### Agent prompt — paste into Cursor

```
Populate corpus/matrix.yaml and wire corpus handlers in Go.

Matrix: 25-35 entries. Each entry:
  id, cwe, title, mode (actual|mitigated|ambiguous), severity, operationIds[], story, data_flow (3+ file paths for actuals), mitigated_pair (when applicable)

Target mix: ~30% actual, ~60% mitigated/noise, ~10% ambiguous.

Implement in internal/corpus/ with realistic multi-file flows for:
SQLi, XSS (reflected), command injection, path traversal, SSRF, XXE, insecure deserialization (yaml/json), weak crypto, IDOR, missing auth, open redirect, sensitive data in logs, hardcoded-ish demo secrets (fake values only).

Register routes already in OpenAPI x-corpus-refs. Comment each sink: // corpus:id=... mode=... cwe=...

Create docs/triggers.md with curl for each matrix id (benign always; evil payloads behind CORPUS_EVIL=1 env).

README: CORPUS_EVIL warning.
```

### Verify
```bash
# With API running:
grep -c "^- id:" corpus/matrix.yaml   # expect 25+
# Run 3-5 curls from docs/triggers.md
```
- [ ] matrix.yaml populated
- [ ] triggers.md works for sample actual + mitigated pairs

---

## Step 7 — React UI (Prompt 6)

### Agent prompt — paste into Cursor

```
Build apps/web (Vite + React + TS) against the running Go API.

Pages:
- Login (demo credentials from README)
- Ticket list, create, detail
- Attachment upload if API supports it
- Admin page (users or webhook replay)
- Corpus Lab page: list from corpus/matrix.yaml or static JSON export

Use VITE_API_BASE_URL. Handle 401 redirect to login.

npm run build must pass. Match existing app styling: simple, professional, not flashy.

Update README: cd apps/web && npm run dev
```

### Verify
```bash
cd apps/web && npm ci && npm run build && npm run dev
# Browser: login, create/view ticket, open Corpus Lab
```
- [ ] Build passes
- [ ] End-to-end UI + API works locally

---

## Step 8 — Docker Compose (Prompt 7)

### Agent prompt — paste into Cursor

```
Production-like containers:

deploy/Dockerfile.api — multi-stage, non-root user, HEALTHCHECK /healthz
deploy/Dockerfile.web — build Vite, serve with nginx, proxy /api to api service OR document CORS + absolute API URL

deploy/docker-compose.yml:
  services: api (8080), web (3000 or 80)
  optional profile postgres: db + api env DATABASE_URL

Root Makefile: compose-up, compose-down

README section "Run with Docker" with exact commands and URLs.
```

### Verify
```bash
docker compose -f deploy/docker-compose.yml up --build -d
curl -s http://localhost:8080/healthz
# open web URL in browser, login, one ticket action
docker compose -f deploy/docker-compose.yml down
```
- [ ] Compose up succeeds
- [ ] UI works against containerized API

---

## Step 9 — Integration tests (Prompt 8)

### Agent prompt — paste into Cursor

```
Add integration/ tests (pytest + requests recommended).

- Load spec/openapi.yaml (PyYAML)
- For each operationId in a curated list (all non-corpus + subset of corpus benign), call API with valid payloads
- Base URL from env INTEGRATION_BASE_URL default http://localhost:8080
- docker-compose profile: run tests after compose up in CI

Skip evil corpus tests unless CORPUS_EVIL=1.

integration/README.md with run instructions.
```

### Verify
```bash
export INTEGRATION_BASE_URL=http://localhost:8080
cd integration && pip install -r requirements.txt && pytest -q
```
- [ ] Tests pass against local or compose API

---

## Step 10 — CI (Prompt 9)

### Agent prompt — paste into Cursor

```
Add .github/workflows/ci.yml:

Jobs: go-lint-test-build, web-build, openapi-lint, docker-build, integration (compose + pytest)

Add CONTRIBUTING.md: how to add a corpus row (matrix + handler + trigger curl + test operationId).

Add CI badge line to README (optional).
```

### Verify
- [ ] Push to GitHub and confirm Actions green (or run act locally if you use it)

---

## Step 11 — Porting doc (Prompt 10)

### Agent prompt — paste into Cursor

```
Write docs/PORTING.md for future PHP/Java backends:

1. Implement spec/openapi.yaml exactly
2. Map corpus/matrix.yaml rows to language-specific paths (same operationIds)
3. integration/ must pass unchanged
4. Suggested folder layouts for PHP (Slim/Laravel) and Java (Spring)
5. Versioning policy for OpenAPI changes

Finalize docs/triggers.md and link from README.
```

### Verify
- [ ] PORTING.md is complete
- [ ] README links all docs

---

## Step 12 — Final smoke (human or agent)

### Agent prompt — paste into Cursor

```
Run full smoke and fix anything broken:

1. cd apps/api-go && make ci
2. cd apps/web && npm ci && npm run build
3. npx @redocly/cli lint spec/openapi.yaml
4. docker compose -f deploy/docker-compose.yml up --build -d
5. integration tests against compose
6. docker compose down

Output SMOKE_REPORT.md with commands run and pass/fail. Fix failures.
```

### Verify
- [ ] SMOKE_REPORT.md all pass
- [ ] Ready to clone on another machine

---

# Quick reference — copy one-liners for new agent

| Step | One-line instruction |
|------|----------------------|
| 1 | Charter README + SECURITY only |
| 2 | Scaffold Go healthz + Vite web + compose skeleton |
| 3 | PRODUCT + ROUTE_PLAN + ARCHITECTURE docs |
| 4 | Full openapi.yaml from route plan |
| 5 | Go API implements OpenAPI + SQLite + auth |
| 6 | corpus/matrix.yaml + multi-file vuln flows |
| 7 | React UI for tickets + corpus lab |
| 8 | Dockerfiles + compose production-like |
| 9 | pytest integration by operationId |
| 10 | GitHub Actions CI |
| 11 | PORTING.md for other languages |
| 12 | Full smoke SMOKE_REPORT.md |

---

# Appendix — Single mega-prompt (autonomous build)

Paste only if you want one agent to run all steps with checkpoints:

```
Build greenfield monorepo "appsec-corpus" from scratch:

Go API (apps/api-go), Vite React web (apps/web), OpenAPI 3.1 (spec/openapi.yaml), corpus (corpus/matrix.yaml), integration tests, Docker Compose, GitHub CI.

Domain: support ticketing + attachments + webhooks. Intentionally vulnerable corpus (~30% actual / 60% mitigated / 10% ambiguous), multi-file flows for major CWEs.

Execute steps 1-12 from the playbook in order. After each step, run acceptance commands and fix before continuing.

Hard gates: go test ./..., npm run build, openapi lint, docker compose up, integration pytest pass.

Document CORPUS_EVIL=1 for local attack curls only. SECURITY.md lab-only warning.
```

---

# Appendix — Google Docs formatting tips

1. Paste this file into a blank Google Doc.
2. Apply **Title** to the main heading; **Heading 1** to each "Step N"; **Heading 2** to "Agent prompt" / "Verify".
3. Insert **Table of contents** (Insert → Table of contents).
4. Duplicate the "Before you start" table on page 1 for tracking.
5. For each Cursor session: copy only **one** "Agent prompt" box + say "repo path is …" and which step number.

---

*Playbook v1.0 — optimized for copy-paste into other Cursor/agent chats.*
