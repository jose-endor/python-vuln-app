#!/usr/bin/env bash
# endor_agent_kit_managed=true (ported to Kiro)
# Advisory routing: reads the user prompt (stdin JSON or $KIRO_* env), prints a
# plain-text suggestion of which Endor agent to use. Never blocks (always exit 0).
if ! command -v python3 >/dev/null 2>&1; then exit 0; fi
payload="$(cat 2>/dev/null)"
HOOK_PAYLOAD="$payload" python3 - "$@" <<'PY' || true
import json, os, re, sys
raw = os.environ.get("HOOK_PAYLOAD", "")
try:
    payload = json.loads(raw) if raw.strip().startswith("{") else {}
except Exception:
    payload = {}
prompt = str(
    payload.get("prompt") or payload.get("user_prompt") or payload.get("message")
    or os.environ.get("KIRO_USER_PROMPT") or raw or ""
).lower()
if not prompt or "endor_agent_kit_managed" in prompt:
    raise SystemExit(0)
routes = []
if re.search(r"\b(cve-\d{4}-\d+|ghsa-[a-z0-9-]+|vulnerab|advisory)\b", prompt):
    routes.append("endor-vulnerability-explainer for a CVE/GHSA, or endor-dependency-reviewer for package applicability.")
if re.search(r"\b(package|dependency|library|module)\b", prompt) and re.search(r"\b(safe|risk|install|add|upgrade|version)\b", prompt):
    routes.append("endor-dependency-reviewer for package decisions, package risk, or repository dependency review.")
if re.search(r"\b(endorctl|scan|host-check|mcp|namespace|auth|token|setup|onboard|error|failed|failure)\b", prompt):
    routes.append("endor-troubleshooting for Endor errors/setup; endor-configuration-automation for GitHub onboarding coverage.")
if re.search(r"\b(findings?|severity|filter|dismissed|reachable|epss|kev)\b", prompt):
    routes.append("endor-findings-browser to browse/filter existing findings without a new scan.")
if re.search(r"\b(remediat|fix|patch|upgrade path)\b", prompt):
    routes.append("endor-remediation-planning (preview, read-only) or endor-sca-remediation (gated fix + PR).")
if re.search(r"\b(ci/cd|cicd|github actions?|workflow|branch protection|supply chain|posture)\b", prompt):
    routes.append("endor-cicd-posture for posture; endor-configuration-automation for onboarding evidence.")
if routes:
    print("Endor Agent Kit advisory routing:")
    for r in dict.fromkeys(routes):
        print(f"- {r}")
PY
exit 0
