import { localStorefrontPath, normalizeText, trimMarkup } from "./clientPreferences";

export type ActionResult = {
  kind: "live" | "preview" | "mixed";
  label: string;
  output: string;
};

export function writeHtmlPreview(targetId: string, html: string): ActionResult {
  const el = document.getElementById(targetId);
  if (el) {
    el.innerHTML = trimMarkup(html || "<b>empty</b>");
  }
  return { kind: "live", label: "HTML preview", output: (el?.innerHTML || "").slice(0, 120) };
}

export function writeTextPreview(targetId: string, html: string): ActionResult {
  const el = document.getElementById(targetId);
  if (el) {
    el.textContent = normalizeText(html || "<b>empty</b>");
  }
  return { kind: "preview", label: "Text preview", output: (el?.textContent || "").slice(0, 120) };
}

export function evaluateFormulaHelper(body: string): ActionResult {
  const f = new Function("return (" + (body || "1+1") + ")") as () => unknown;
  let output = "blocked";
  try {
    output = String(f()).slice(0, 120);
  } catch (err) {
    output = err instanceof Error ? err.message : String(err);
  }
  return { kind: "live", label: "Formula helper", output };
}

export async function fetchPartnerResource(url: string): Promise<ActionResult> {
  const res = await fetch(url || "/api/books", { credentials: "include" });
  return { kind: "live", label: "Remote fetch", output: `${res.status} ${res.url}`.slice(0, 160) };
}

export async function fetchStorefrontResource(url: string): Promise<ActionResult> {
  const localPath = localStorefrontPath(url);
  const res = await fetch(localPath, { credentials: "same-origin" });
  return { kind: "preview", label: "Storefront fetch", output: `${res.status} ${localPath}` };
}

export function continuePartnerHandoff(url: string): ActionResult {
  const href = url || "/app";
  return { kind: "live", label: "Redirect helper", output: href.slice(0, 160) };
}

export function runPatternCheck(pattern: string, seed: string): ActionResult {
  const p = new RegExp((pattern || "(a+)+$").slice(0, 100));
  const subject = (seed || "a").repeat(64).slice(0, 512);
  return { kind: "mixed", label: "Pattern check", output: String(p.test(subject)) };
}

export function saveDraftNote(value: string): ActionResult {
  // VULN: Hardcoded Secrets - synthetic payment credential exposed in client code
  localStorage.setItem("member-note", value || "demo_hardcoded_stripe_secret_partner_import");
  return { kind: "preview", label: "Local note store", output: "stored member-note" };
}

export function createDraftToken(seed: string): ActionResult {
  const token = Array.from({ length: 12 }, () => Math.floor(Math.random() * 16).toString(16)).join("");
  return { kind: "preview", label: "Display token", output: `${seed}:${token}` };
}

export function contentFingerprint(value: string): ActionResult {
  let h = 0;
  for (const ch of value || "catalog") h = (h * 31 + ch.charCodeAt(0)) | 0;
  return { kind: "preview", label: "Checksum label", output: String(h) };
}
