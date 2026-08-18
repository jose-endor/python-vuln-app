#!/usr/bin/env bash
# Install the endor-ez-scan agent into all three host environments, user-level
# (available across every repo). Idempotent — safe to re-run after editing the recipe.
#
#   Kiro   : ~/.kiro/agents/endor-ez-scan.{md,json} + prompts/  (via generate.py, agents-only)
#   Cursor : ~/.cursor/agents/endor-ez-scan-agent.md + ~/.cursor/skills/endor-ez-scan/SKILL.md
#   Claude : ~/.claude/agents/endor-ez-scan.md                 (derived from recipe: Claude host + frontmatter)
#   Skill  : ~/endor-skills/skills/endor-ez-scan/SKILL.md      (shared source + Claude compatibility)
#
# The recipe (recipes/endor-ez-scan-agent.md) is the single source of truth for the prompt body.
set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RECIPE="$KIT_DIR/recipes/endor-ez-scan-agent.md"
SKILL_SRC="$KIT_DIR/dist/skill/endor-ez-scan/SKILL.md"

[ -f "$RECIPE" ] || { echo "missing recipe: $RECIPE" >&2; exit 1; }
[ -f "$SKILL_SRC" ] || { echo "missing skill: $SKILL_SRC" >&2; exit 1; }

echo "== Kiro (user-level ~/.kiro/agents, agents only) =="
python3 "$KIT_DIR/generate.py" --source "" --recipes "$KIT_DIR/recipes" --dest "$HOME" --agents-only

echo "== Cursor (~/.cursor/agents) =="
mkdir -p "$HOME/.cursor/agents"
# Cursor uses name/description/model/readonly frontmatter; drop the generator-only `profile` key.
grep -v '^profile:' "$RECIPE" > "$HOME/.cursor/agents/endor-ez-scan-agent.md"
# Cursor discovers user skills only from its documented skills directory.
CURSOR_SKILL="$HOME/.cursor/skills/endor-ez-scan"
mkdir -p "$CURSOR_SKILL"
cp "$SKILL_SRC" "$CURSOR_SKILL/SKILL.md"

echo "== Claude Code (~/.claude/agents, derived from recipe) =="
mkdir -p "$HOME/.claude/agents"
# Claude plugin convention (see plugins/claude/*/agents): agents use BARE names — no `endor-`
# prefix, no `-agent` suffix (e.g. repository-dependency-reviewer). So the Claude subagent is
# `ez-scan`, not `endor-ez-scan`. Remove any prior prefixed copy.
rm -f "$HOME/.claude/agents/endor-ez-scan.md"
RECIPE="$RECIPE" python3 - "$HOME/.claude/agents/ez-scan.md" <<'PY'
import os, re, sys
text = open(os.environ["RECIPE"], encoding="utf-8").read()
# split YAML frontmatter
assert text.startswith("---")
end = text.find("\n---", 3)
fm_raw, body = text[3:end], text[end+4:].lstrip("\n")
# pull description block scalar out of the recipe frontmatter
desc_lines, grab = [], False
for line in fm_raw.splitlines():
    if re.match(r"^description:\s*\|", line):
        grab = True; continue
    if grab:
        if re.match(r"^[A-Za-z0-9_]+:", line):
            break
        desc_lines.append(line.strip())
description = " ".join(d for d in desc_lines if d).strip()
# re-host the body for Claude Code
body = body.replace("Cursor Host Contract", "Claude Code Host Contract")
body = body.replace("Cursor host integration", "Claude Code host integration")
body = body.replace("Cursor file and shell tools", "Claude Code file and shell tools")
body = body.replace("Cursor performed", "Claude Code performed")
body = body.replace("Cursor plugin", "Claude Code plugin")
body = re.sub(r"\bCursor\b", "Claude Code", body)
body = re.sub(r"host=cursor", "host=claude-code", body)
# Claude subagent frontmatter: disallow file mutation tools; keep Bash + MCP for scanning.
fm = (
    "---\n"
    "name: ez-scan\n"
    "description: |\n"
    + "".join(f"  {w}\n" for w in __import__("textwrap").wrap(description, 90))
    + "disallowedTools: Write, Edit, MultiEdit, NotebookEdit\n"
    "model: sonnet\n"
    "---\n\n"
)
open(sys.argv[1], "w", encoding="utf-8").write(fm + body.rstrip() + "\n")
print("wrote", sys.argv[1])
PY

echo "== Shared support skill (~/endor-skills/skills, symlinked into ~/.claude/skills) =="
DEST_SKILL="$HOME/endor-skills/skills/endor-ez-scan"
mkdir -p "$DEST_SKILL"
cp "$SKILL_SRC" "$DEST_SKILL/SKILL.md"

echo
echo "Installed endor-ez-scan to Kiro, Cursor, Claude, and the shared skills dir."
echo "Kiro   : $HOME/.kiro/agents/endor-ez-scan.{md,json}"
echo "Cursor : $HOME/.cursor/agents/endor-ez-scan-agent.md"
echo "Cursor skill: $CURSOR_SKILL/SKILL.md"
echo "Claude : $HOME/.claude/agents/ez-scan.md"
echo "Skill  : $DEST_SKILL/SKILL.md"
