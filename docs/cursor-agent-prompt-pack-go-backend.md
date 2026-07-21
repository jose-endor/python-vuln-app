# AppSec Corpus — Cursor Agent Prompt Pack

**Purpose:** Build a realistic, intentionally vulnerable full-stack application for AppSec tool evaluation (SAST, SCA, secrets, containers, IaC).

**Architecture (this program):**
- **Backend:** 100% Go
- **Frontend:** npm (Vite + React recommended; document choice in README)
- **Future:** Other backends (PHP, Java, etc.) must implement the same OpenAPI contract

**How to use this document**
1. Copy sections into Google Docs (one doc per phase, or one doc with headings).
2. Run prompts **in order** (Prompt 0 → 10). Do not skip Prompt 1–3 (contract + matrix).
3. Each prompt ends with **Acceptance criteria** — do not proceed until met.
4. Paste the full prompt block into Cursor Agent; attach this doc or the relevant section.

**Status tracker (fill in as you go)**

| # | Prompt | Owner | Status | Notes |
|---|--------|-------|--------|-------|
| 0 | Repo charter | | ☐ | |
| 1 | Monorepo scaffold | | ☐ | |
| 2 | Domain model | | ☐ | |
| 3 | OpenAPI contract | | ☐ | |
| 4 | Go backend architecture | | ☐ | |
| 5 | Corpus matrix + noise | | ☐ | |
| 6 | npm frontend | | ☐ | |
| 7 | Docker + Compose | | ☐ | |
| 8 | Integration tests | | ☐ | |
| 9 | CI pipeline | | ☐ | |
| 10 | Porting handoff | | ☐ | |

---

## Prompt 0 — Repo charter

**Copy everything below this line into Cursor Agent:**

---

You are building an **intentionally vulnerable research application** for **AppSec tool evaluation** (SAST, SCA, secrets scanning, container scanning). It must resemble a **small but credible B2B product** (multiple modules, realistic HTTP surface, persistence, admin vs user flows), while remaining **safe for local lab use only**.

### Hard requirements
- Backend is **100% Go** (single `apps/api-go` service for now).
- Frontend is **npm-based** (Vite + React + TypeScript unless already decided).
- **OpenAPI-first:** HTTP contract lives in `spec/openapi.yaml`; Go must not invent routes outside the spec.
- **Builds without errors:** `go build`, `go test ./...`, `npm ci && npm run build` all succeed on a clean checkout.
- **Runs locally and in containers:** documented `make run` / `npm run dev` AND `docker compose up --build`.
- Design for **future backend ports** (PHP, Java, etc.) against the same OpenAPI + integration tests.

### Non-goals
- Production security, compliance certification, or multi-tenant isolation
- Real payment processing or real PII
- Hosting on the public internet without warnings

### Deliverables
1. `README.md` — setup, run locally, run in Docker, threat-model disclaimer
2. `SECURITY.md` — “intentionally vulnerable; lab use only”
3. One-paragraph **product pitch** (what the fake company/product does)

### Acceptance criteria
- [ ] README and SECURITY.md exist and are accurate
- [ ] Product domain is chosen and written down (1–2 sentences)

---

## Prompt 1 — Monorepo scaffold + engineering standards

**Prerequisites:** Prompt 0 complete.

**Copy everything below this line into Cursor Agent:**

---

Create the monorepo layout and engineering baseline. Do not implement business features yet—scaffold only.

### Directory layout
```
/spec/openapi.yaml              # placeholder; filled in Prompt 3
/corpus/matrix.yaml             # placeholder; filled in Prompt 5
/apps/api-go/                    # Go module: cmd/, internal/
/apps/web/                      # Vite + React + TypeScript
/integration/                   # API contract tests (language-neutral)
/deploy/
  Dockerfile.api
  Dockerfile.web
  docker-compose.yml
/docs/
  triggers.md                   # placeholder
  PORTING.md                    # placeholder; filled in Prompt 10
Makefile                        # top-level orchestration
```

### Go (`apps/api-go`)
- Go **1.22+**
- `cmd/server/main.go` — minimal server on `:8080` with `/healthz` returning `{"ok":true}`
- `Makefile` targets: `lint`, `test`, `build`, `run`, `ci` (lint + test + build)
- `.golangci.yml` with reasonable defaults
- `go mod init` with module path matching repo (e.g. `github.com/<org>/appsec-corpus`)

### Web (`apps/web`)
- Vite + React + TypeScript
- `package.json` scripts: `dev`, `build`, `preview`
- `.env.example` with `VITE_API_BASE_URL=http://localhost:8080`
- Placeholder page: “API health” button calling `/healthz`

### Root
- Root `Makefile`: `make api`, `make web`, `make ci`, `make compose-up`
- `.gitignore` for Go, node, env files
- `.nvmrc` or `engines` in package.json (Node 20 LTS)

### Acceptance criteria
- [ ] `cd apps/api-go && make ci` passes
- [ ] `cd apps/web && npm ci && npm run build` passes
- [ ] `curl http://localhost:8080/healthz` works after `make run` (api)
- [ ] No secrets or real credentials in repo

---

## Prompt 2 — Realistic product domain + route plan

**Prerequisites:** Prompt 1 complete.

**Copy everything below this line into Cursor Agent:**

---

Choose **one** product domain and document it. Then produce a **route plan** (not full OpenAPI yet) that will become the OpenAPI in Prompt 3.

### Recommended domain (pick one)
- **Support ticketing + attachments + webhooks** (recommended), OR
- B2B inventory + supplier integrations, OR
- Document intake / OCR pipeline (simulated)

### Complexity targets (realistic app, not a toy)
- **10–25 route groups** across: public, authenticated user, admin, internal/util
- **Persistence:** SQLite default; Postgres via compose profile `db=postgres`
- **Cross-cutting:** config from env, structured logging (slog), request ID middleware, graceful shutdown
- **Async realism:** at least one of: in-process worker queue, scheduled cleanup job, or “outbox” table processed on interval—enough to create multi-hop flows for scanners

### Deliverables
1. `docs/PRODUCT.md` — actors (user, admin, system), core entities, 5–10 user stories
2. `docs/ROUTE_PLAN.md` — table: `group`, `method`, `path`, `auth`, `purpose`, `notes for corpus`
3. List of **packages** under `apps/api-go/internal/` you will create (httpapi, domain, repo, workers, integration, etc.)

### Acceptance criteria
- [ ] PRODUCT.md and ROUTE_PLAN.md exist
- [ ] Route plan has ≥15 distinct endpoints planned
- [ ] At least 3 flows are described as multi-step (e.g. upload → scan → notify)

---

## Prompt 3 — OpenAPI contract (portability anchor)

**Prerequisites:** Prompt 2 complete.

**Copy everything below this line into Cursor Agent:**

---

Author **`spec/openapi.yaml`** (OpenAPI 3.1) from `docs/ROUTE_PLAN.md`. This file is the **single HTTP contract** for all current and future backends.

### Rules
- Every operation has a unique, stable **`operationId`** (camelCase, e.g. `createTicket`, `adminReplayWebhook`).
- Use shared **components/schemas** for User, Session, Ticket, Attachment, WebhookEvent, Error.
- Define **securitySchemes**: session cookie and/or Bearer token—document which routes use which.
- Add extension on corpus-related operations:  
  `x-corpus-refs: [{ cwe: "CWE-89", mode: "actual", matrixId: "sql-search-01" }]`
- Include `/healthz` and `/readyz` (readyz may check DB connectivity).

### Deliverables
- `spec/openapi.yaml` — complete enough to generate stubs
- `docs/openapi-operations.md` — index table: operationId → path → auth → corpus refs (if any)

### Acceptance criteria
- [ ] OpenAPI validates (document command: e.g. `npx @redocly/cli lint spec/openapi.yaml`)
- [ ] No operation without `operationId`
- [ ] README links to OpenAPI as the contract for future PHP/Java ports

---

## Prompt 4 — Go backend architecture (implement OpenAPI)

**Prerequisites:** Prompt 3 complete.

**Copy everything below this line into Cursor Agent:**

---

Implement the Go API in `apps/api-go/` to satisfy **`spec/openapi.yaml` exactly**. Use production-like layering.

### Structure
```
apps/api-go/
  cmd/server/main.go
  internal/httpapi/       # chi or std mux; middleware; handlers
  internal/domain/      # use cases
  internal/repo/        # SQLite (modernc.org/sqlite or similar)
  internal/integration/ # outbound HTTP, webhooks
  internal/workers/     # background processing
  internal/auth/        # session/JWT as per OpenAPI
```

### Implementation rules
- Handlers are thin; business logic in `domain/`.
- **Do not add routes** not in OpenAPI.
- Migrations: embed SQL or use goose/golang-migrate; seed demo users/tickets.
- Return consistent JSON errors `{ "error": "...", "requestId": "..." }`.

### Corpus prep (structure only in this prompt)
- Create packages: `internal/corpus/sources`, `internal/corpus/propagation`, `internal/corpus/sinks`, `internal/corpus/noise`
- Wire corpus routes from OpenAPI `x-corpus-refs` to handlers (stubs OK if matrix not done yet)

### Acceptance criteria
- [ ] `go test ./...` passes
- [ ] `make -C apps/api-go ci` passes
- [ ] Every OpenAPI path returns documented status codes for **happy-path** requests
- [ ] `/healthz` and `/readyz` work
- [ ] README: how to run API locally with env vars

---

## Prompt 5 — Corpus matrix + intentional findings

**Prerequisites:** Prompt 4 complete (handlers exist).

**Copy everything below this line into Cursor Agent:**

---

Populate **`corpus/matrix.yaml`** and implement corpus flows in Go with realistic multi-file data paths.

### Matrix schema (each row)
```yaml
- id: sql-search-01
  cwe: CWE-89
  title: SQL injection in ticket search
  mode: actual          # actual | mitigated | ambiguous
  severity: critical    # for documentation only
  operationIds: [searchTickets]
  story: "Attacker injects SQL via search query parameter."
  data_flow:
    - internal/corpus/sources/http_query.go
    - internal/corpus/propagation/query_builder.go
    - internal/corpus/sinks/sql_exec.go
  mitigated_pair: sql-search-01-safe
  scanner_notes: "Parameterized query in mitigated variant."
```

### Coverage targets (initial MVP)
- **25–40 rows** total spanning OWASP-style categories
- Mix: **~30% actual**, **~60% mitigated/noise**, **~10% ambiguous** (tunable)
- Each **actual** should use **≥3 files** in `data_flow` where credible
- Categories to include (examples): SQLi, XSS (reflected/stored), command injection, path traversal, SSRF, XXE, insecure deserialization, weak crypto, IDOR, missing auth, sensitive logs, open redirect, mass assignment

### Noise realism (`internal/corpus/noise/`)
- Dead branches, unreachable code, env-gated routes
- “Almost safe” wrappers that still confuse tools
- Pairs: actual vs mitigated side-by-side

### Deliverables
- `corpus/matrix.yaml`
- `docs/triggers.md` — **curl** example per `id` (benign + optional evil behind `CORPUS_EVIL=1`)
- Comments in code: `// corpus:id=sql-search-01 mode=actual cwe=CWE-89`

### Acceptance criteria
- [ ] Every `actual` row has working handler + curl in triggers.md
- [ ] Every `actual` with `mitigated_pair` has a working safer variant
- [ ] Matrix `operationIds` all exist in OpenAPI

---

## Prompt 6 — npm frontend (credible UI)

**Prerequisites:** Prompt 4–5 in progress or complete.

**Copy everything below this line into Cursor Agent:**

---

Build the React UI in `apps/web/` that exercises the API like a real product.

### Pages (minimum)
- Login (demo credentials documented in README)
- Ticket list + detail + create
- Attachment upload UI (if in OpenAPI)
- Admin: users or webhook replay (if in OpenAPI)
- Link or section to **Corpus lab** (lists corpus endpoints from matrix or static config)

### Standards
- API client: fetch or axios; base URL from `import.meta.env.VITE_API_BASE_URL`
- TypeScript types optional (openapi-typescript from spec is a plus)
- Minimal client-side XSS sinks **only if** required for evaluation; prefer server-side corpus
- Accessible, clean layout; no design system required

### Acceptance criteria
- [ ] `npm ci && npm run build` passes
- [ ] UI works against local API (`make run` + `npm run dev`)
- [ ] Login + one ticket flow works end-to-end
- [ ] README documents web env vars

---

## Prompt 7 — Docker + Docker Compose

**Prerequisites:** Prompts 4 and 6 complete.

**Copy everything below this line into Cursor Agent:**

---

Containerize API and web; provide one-command stack startup.

### Files
- `deploy/Dockerfile.api` — multi-stage, non-root user, `HEALTHCHECK` on `/healthz`
- `deploy/Dockerfile.web` — build static assets, serve with nginx
- `deploy/docker-compose.yml` — services: `api`, `web`; optional `postgres` profile
- Root `Makefile` target: `compose-up`, `compose-down`

### Environment
- Document all env vars in README
- `apps/api-go` listens on `8080` inside container; web proxies or points to API URL

### Acceptance criteria
- [ ] `docker compose -f deploy/docker-compose.yml up --build` succeeds
- [ ] `curl http://localhost:<api-port>/healthz` OK
- [ ] Browser can load web UI and complete login + one API-backed action
- [ ] Images run as non-root where feasible

---

## Prompt 8 — Integration tests (portability gate)

**Prerequisites:** Prompts 3, 4, 7 complete.

**Copy everything below this line into Cursor Agent:**

---

Add **`integration/`** black-box tests that certify API behavior by **`operationId`**, not language.

### Approach
- Python + pytest + requests **or** Go test in separate module—pick one and document
- Load OpenAPI; map `operationId` → method + path
- **Default suite:** benign payloads only; assert status codes and minimal JSON shape
- **Optional:** `CORPUS_EVIL=1` enables attack-ish payloads; skip in CI by default

### Deliverables
- `integration/README.md` — how to run against local API or compose stack
- CI job runs integration after `compose-up`

### Acceptance criteria
- [ ] Integration tests pass against `docker compose` stack
- [ ] Failures print `operationId` and request details
- [ ] At least one test per major OpenAPI tag/group

---

## Prompt 9 — CI pipeline (definition of done)

**Prerequisites:** Prompts 1–8 substantially complete.

**Copy everything below this line into Cursor Agent:**

---

Add GitHub Actions (or GitLab CI) workflow `.github/workflows/ci.yml`:

### Jobs
1. **go** — lint, test, build (`apps/api-go`)
2. **web** — `npm ci`, `npm run build` (`apps/web`)
3. **openapi** — lint `spec/openapi.yaml`
4. **docker** — build images (no push required)
5. **integration** — compose up, run integration tests, compose down

### Repo hygiene
- Dependabot or renovate optional
- No committed `.env` secrets

### Acceptance criteria
- [ ] CI green on default branch
- [ ] README badge or “CI status” section
- [ ] CONTRIBUTING.md: how to add a new corpus row + test

---

## Prompt 10 — Porting handoff (future PHP/Java backends)

**Prerequisites:** Prompts 3, 5, 8 complete.

**Copy everything below this line into Cursor Agent:**

---

Write **`docs/PORTING.md`** for teams implementing another backend.

### Must include
1. **Contract:** implement `spec/openapi.yaml` exactly; no extra operations
2. **Matrix:** implement rows in `corpus/matrix.yaml`; preserve `id`, `mode`, `operationIds`, `data_flow` package naming convention
3. **Tests:** `integration/` must pass unchanged against new backend
4. **Suggested layout** for PHP/Laravel, Java/Spring (directory mirrors)
5. **Deliberate deviations** section (should be empty initially)

### Acceptance criteria
- [ ] PORTING.md is actionable without reading Go source
- [ ] Lists commands to run integration tests against alternate backend URL

---

## Appendix A — Master meta-prompt (single paste for autonomous agent)

Use when you want one long-running agent session with checkpoints:

---

Build an AppSec evaluation corpus monorepo:

1. Go-only backend (`apps/api-go`), npm frontend (`apps/web`), OpenAPI-first (`spec/openapi.yaml`), corpus matrix (`corpus/matrix.yaml`).
2. Realistic domain: support ticketing + attachments + webhooks.
3. Intentionally vulnerable patterns (~30% actual / ~60% mitigated / ~10% ambiguous) with multi-file flows (≥3 files) for major CWE themes.
4. Must compile and test clean; run locally and via Docker Compose.
5. Integration tests keyed by `operationId`; CI enforces all of the above.
6. Document porting for future non-Go backends in `docs/PORTING.md`.

Execute in order: scaffold → domain/route plan → OpenAPI → Go implementation → corpus → UI → Docker → integration → CI → PORTING.md.

After each phase, stop and verify acceptance criteria before continuing. Do not skip OpenAPI before implementing handlers.

---

## Appendix B — Google Docs import tips

1. **File → Import** upload this `.md` file, or paste sections into a new Doc.
2. Use **Heading 1** for “Prompt N”, **Heading 2** for “Acceptance criteria”.
3. Add a **Table of contents** (Insert → Table of contents).
4. Duplicate the **Status tracker** table to the top of your Doc.
5. For each Cursor session: copy **one prompt block** + attach `spec/openapi.yaml` once it exists.

## Appendix C — Optional follow-up prompts (scale)

| Prompt | Purpose |
|--------|---------|
| C1 — Corpus generator | Script from `matrix.yaml` → Go handler stubs |
| C2 — SCA surface | Add `go.sum` + npm lock with documented vulnerable deps for demos |
| C3 — Secrets fixtures | Fake tokens in testdata; ensure secret scanners fire |
| C4 — IaC | Terraform/k8s manifests with intentional misconfigs |
| C5 — AI SAST rerun | Run Endor with `--ai-sast-analysis=agent-fallback` after corpus stable |

---

*Document version: 1.0 — Go backend + npm UI, OpenAPI-first, multi-backend porting.*
