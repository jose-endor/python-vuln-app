# Kiro Agent Kit (Endor Labs) — PoC

Kiro-native port of the current Endor Labs Agent Kit (12 official agents plus one local scanner)
that runs in **both** Kiro surfaces — the **IDE** (`.kiro/agents/*.md`) and the **CLI**
(`.kiro/agents/*.json`) — from a single generator.

This is a PoC. Agent *behavior* (prompts, determinism, evidence-first, `data_gaps`) comes verbatim
from upstream `endorlabs/ai-plugins`; only the host packaging and the safety/permission wiring are
re-expressed for Kiro.

## What gets generated

Running `generate.py` writes into the destination's `.kiro/`:

```
.kiro/
  endor-agent-kit-version.json  # upstream package version + exact source commit
  agents/
    <name>.md            # IDE agent: YAML frontmatter (permissions model) + prompt body
    <name>.json          # CLI agent: allowedTools + toolsSettings.shell gates + embedded hooks
    prompts/<name>.md    # shared prompt body (single source of truth; CLI loads via file://)
  hooks/
    endor-advisory-routing.json        # workspace hook (Kiro V1.0.0+ format), UserPromptSubmit advisory
    scripts/endor-suggest.sh           # dual-compatible routing script (plain-text stdout)
  steering/
    endor-agent-kit.md   # always-on advisory routing + safety contract (reliable path)
```

13 agents × 2 surfaces = 26 agent files. Both surfaces read `.kiro/agents/`; the IDE consumes
`.md`, the CLI consumes `.json`, so they coexist without collision.

## How safety is reproduced

Upstream marks each agent `readonly: true|false`. These agents are **MCP-free** — they gather
evidence by shelling out to `endorctl`/`git`/`gh`, so "read-only" cannot mean "no shell." Instead:

| profile | Kiro IDE (`permissions.rules`) | Kiro CLI (`toolsSettings.shell`) |
| --- | --- | --- |
| **read-only (10)** | no `write` tool; `filesystem deny **`; `shell allow` read lookups; `shell deny` mutations incl. `endorctl scan` | `allowedCommands` (reads) + `deniedCommands` (mutations incl. `endorctl scan`) + `autoAllowReadonly` |
| **scanner (1)** | no `write` tool; `filesystem deny **`; `shell allow` read lookups **+ `endorctl scan`**; `shell deny` all other mutations | `allowedCommands` (reads **+ `endorctl scan`**) + read MCP tools **+ `scan`/`security_review`** + `deniedCommands` (all other mutations) |
| **mutating (2)** | `write`+`shell` granted; only reads allowed; writes/pushes/PRs unlisted → Kiro default `ask` = **approval gate per action** | only reads in `allowedTools`; writes + mutating shell prompt = **approval gate** |

`sca-remediation` and `ai-sast-remediation` are the only mutating agents; every file edit / branch
push / PR / comment / ticket surfaces as a separate prompt. Secrets globs (`.env`, `secrets/**`,
`*.pem`, `id_rsa*`, `*.key`) are hard-denied even for mutating agents.

### The `scanner` profile — `endor-ez-scan`

The one-button **`endor-ez-scan`** agent is the only `scanner`-profile agent. It is the sole agent
allowed to actually run a scan (`endorctl scan` + the Endor MCP `scan`/`security_review` tools),
while every other mutation — file writes (even a result cache), package installs, git/gh writes,
PRs/comments, Endor policy — stays denied. It runs both phases in one pass:

- **Phase 2 (capability detection):** detects which scan types apply to the repo and which the
  tenant is entitled to, degrading gracefully (unlicensed/failed types become `data_gaps`, never
  a hard failure).
- **Phase 1 (broad scan):** one `scan` call with all enabled `scan_types` and
  `scan_options: { quick_scan: false, summary: false }` → full call graph = **function-level
  reachability**.

Unlike the 12 official agents, `endor-ez-scan` is a **local extension** (not in upstream
`endorlabs/ai-plugins`). Its source of truth is `recipes/endor-ez-scan-agent.md`, and it is
generated via the `profile: scanner` frontmatter key plus the `--recipes` generator flag.

## Multi-host install (`endor-ez-scan`)

`endor-ez-scan` ships to **Kiro, Cursor, and Claude Code** from the one recipe. Install user-level
(all repos) with:

```bash
bash kiro-agent-kit/install-ez-scan.sh
```

This writes:

| Host | Path | Format |
| --- | --- | --- |
| Kiro | `~/.kiro/agents/endor-ez-scan.{md,json}` + `prompts/` | generated (IDE md + CLI json), agents-only |
| Cursor | `~/.cursor/agents/endor-ez-scan-agent.md` | recipe (generator-only `profile:` key stripped) |
| Cursor skill | `~/.cursor/skills/endor-ez-scan/SKILL.md` | documented user-level Cursor skill location |
| Claude Code | `~/.claude/agents/ez-scan.md` | derived from recipe: Claude host, bare name per Claude plugin convention, `disallowedTools: Write, Edit, MultiEdit, NotebookEdit` |
| Shared skill source | `~/endor-skills/skills/endor-ez-scan/SKILL.md` | shared copy and Claude compatibility source |

The prompt body is derived from the single recipe for every host, so behavior can't drift between
environments. Re-run the installer after editing `recipes/endor-ez-scan-agent.md`.

## Install

**Workspace (self-contained, committable — what this PoC generates):** already in `./.kiro/`.
Open this folder in Kiro; trust the workspace when prompted. Agents appear in the selector.

**User-level (available across all your repos):** re-generate targeting your home dir:

```bash
python3 kiro-agent-kit/generate.py \
  --source ~/demo/_ref/ai-plugins \
  --recipes kiro-agent-kit/recipes \
  --dest ~ \
  --agents-only
# writes ~/.kiro/agents/... (agents are global; hooks remain workspace-only in Kiro)
```

**Prerequisite (the evidence layer):** the Endor MCP server + authed `endorctl`. MCP config already
lives at `~/.kiro/settings/mcp.json`. Mutating agents that open PRs also need `gh auth status` OK.

## Re-generating on upstream bumps

```bash
cd ~/demo/_ref/ai-plugins && git pull        # refresh upstream
python3 kiro-agent-kit/generate.py \
  --source ~/demo/_ref/ai-plugins \
  --recipes kiro-agent-kit/recipes \
  --dest .
bash kiro-agent-kit/validate.sh
```

Do not hand-edit files under `.kiro/agents/` — they are generated. Change `generate.py` (profiles,
body rewrites) instead, or the upstream recipe.

The generator reads the installable Cursor package at
`plugins/cursor/endor-labs-agent-kit/agents/`, removes stale generated workflows after upstream
renames, and records the package version and Git commit in `.kiro/endor-agent-kit-version.json`.

Generator flags:

- `--source ""` — skip upstream ai-plugins agents (generate from `--recipes` only).
- `--recipes <dir>` — also (or only) generate from local recipe `.md` files (e.g. `recipes/`),
  same Cursor agent format. Profile is chosen by a `profile: readonly|scanner|mutating` frontmatter
  key, falling back to the `readonly:` flag.
- `--agents-only` — write just agent files (skip the workspace hook + steering); used for the
  user-level `--dest ~` install.

## Validate

```bash
bash kiro-agent-kit/validate.sh
```

Checks: JSON lint on all CLI agents + the hook, bash syntax on the hook script, frontmatter delimiters
on IDE agents, and body-port cleanliness (no stray "Cursor").

## Known assumptions & caveats (PoC)

- **Model id:** omitted by default → Kiro uses its default model. Pin with `--model claude-sonnet-4`
  only if that id is valid in your Kiro build.
- **IDE advisory hooks:** Kiro IDE only injects command-hook STDOUT into context on `SessionStart` /
  `UserPromptSubmit`; `PostFileSave` / `PreToolUse` STDOUT is ignored. So the manifest-edit and
  dep-install advisories from the Cursor plugin are carried by the **always-on steering file**
  (`.kiro/steering/endor-agent-kit.md`) instead — the reliable path. The `UserPromptSubmit` hook is
  a best-effort bonus.
- **Hook format:** Kiro V1.0.0+ uses `.kiro/hooks/*.json` with `{version, hooks:[...]}` (PascalCase
  triggers, action types `command`/`agent`). The legacy single-object `.kiro.hook` (`when`/`then`)
  schema is NOT used here — a `.kiro.hook` extension triggers the old parser and errors with
  "invalid data structure: Required". One workspace hook file applies to all agents in both surfaces,
  so agent configs carry no embedded `hooks`. The ported script prints plain text (not the Cursor
  `hookSpecificOutput` JSON) and never blocks (always exits 0).
- **Shell gate patterns** are broad-but-careful. Validate on real runs: confirm read-only agents
  cannot mutate and mutating agents prompt before each write/push/PR before trusting in a demo.
- **Not officially supported.** endorlabs/ai-plugins ships no Kiro package; you own this port and any
  drift when upstream changes.
