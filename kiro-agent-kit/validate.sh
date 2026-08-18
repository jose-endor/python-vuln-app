#!/usr/bin/env bash
# Validate the generated Kiro Agent Kit output. Run from the repo root.
set -u
KIRO="${1:-.kiro}"
fail=0

echo "=== inventory ==="
md=$(ls "$KIRO"/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
js=$(ls "$KIRO"/agents/*.json 2>/dev/null | wc -l | tr -d ' ')
bd=$(ls "$KIRO"/agents/prompts/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "IDE .md=$md  CLI .json=$js  bodies=$bd"
[ "$md" = "$js" ] && [ "$md" = "$bd" ] || { echo "MISMATCH in surface counts"; fail=1; }

echo "=== upstream provenance ==="
provenance="$KIRO/endor-agent-kit-version.json"
python3 -m json.tool "$provenance" >/dev/null 2>&1 \
  || { echo "INVALID or missing Agent Kit provenance"; fail=1; }
if [ -f "$provenance" ]; then
  # The generated inventory must match the upstream package plus any explicit local recipes.
  expected=$(python3 -c "import json,sys;p=json.load(open(sys.argv[1]));print(p['upstream_agent_count'] + p['local_recipe_count'])" "$provenance")
  [ "$md" = "$expected" ] || { echo "INVENTORY does not match provenance: expected=$expected actual=$md"; fail=1; }
  python3 -c "import json,re,sys;p=json.load(open(sys.argv[1]));assert p['package_version'] not in ('unknown','local-only');assert re.fullmatch(r'[0-9a-f]{40}', p['source_commit'])" "$provenance" \
    || { echo "INVALID upstream version or source commit"; fail=1; }
fi

echo "=== CLI json lint ==="
for f in "$KIRO"/agents/*.json; do
  python3 -m json.tool "$f" >/dev/null 2>&1 || { echo "INVALID JSON: $f"; fail=1; }
done

echo "=== hook json lint ==="
python3 -m json.tool "$KIRO"/hooks/endor-advisory-routing.json >/dev/null 2>&1 \
  || { echo "INVALID hook json"; fail=1; }

echo "=== MCP command ==="
# Current Agent Kit setup guidance uses the npm-distributed endorctl MCP entry point.
python3 -c "import json,sys;m=json.load(open(sys.argv[1]))['mcpServers']['endor-cli-tools'];assert m['command']=='npx';assert m['args']==['-y','endorctl','ai-tools','mcp-server']" "$KIRO/settings/mcp.json" \
  || { echo "STALE Endor MCP command"; fail=1; }

echo "=== hook script bash syntax ==="
bash -n "$KIRO"/hooks/scripts/endor-suggest.sh || { echo "hook script syntax error"; fail=1; }

echo "=== IDE frontmatter delimiters ==="
for f in "$KIRO"/agents/*.md; do
  head -1 "$f" | grep -q '^---$' || { echo "missing frontmatter: $f"; fail=1; }
done

echo "=== host cleanliness (no stray 'Cursor' / 'Claude Code' host mentions) ==="
# Check the WHOLE agents surface (IDE .md, CLI .json descriptions, and shared prompt bodies),
# not just prompts/ — descriptions are host-specific and leaked "for Cursor" historically.
# "Claude Code" (host phrase) must not appear either; "CLAUDE.md" (a filename convention the
# agents must not create) is allowed, and does not match the "claude code" phrase.
if grep -rilq "cursor" "$KIRO"/agents/ 2>/dev/null; then
  echo "stray Cursor references:"; grep -ril "cursor" "$KIRO"/agents/; fail=1
fi
if grep -rilq "claude code" "$KIRO"/agents/ 2>/dev/null; then
  echo "stray 'Claude Code' host references:"; grep -ril "claude code" "$KIRO"/agents/; fail=1
fi

echo "=== prompt file:// targets resolve ==="
for f in "$KIRO"/agents/*.json; do
  p=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['prompt'])" "$f" | sed 's#^file://##')
  # resolve relative to the json's dir
  d=$(dirname "$f"); [ -f "$d/$p" ] || { echo "missing prompt body for $f -> $p"; fail=1; }
done

[ $fail -eq 0 ] && echo "ALL CHECKS PASSED ✓" || { echo "VALIDATION FAILED"; exit 1; }
