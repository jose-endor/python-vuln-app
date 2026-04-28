import { safeLocalPath, strongClientEscape, weakClientSanitize } from "./cweTransforms";

export type SinkResult = {
  kind: "actual" | "noise" | "ambiguous";
  label: string;
  output: string;
};

export function writeUnsafeHtml(targetId: string, html: string): SinkResult {
  const el = document.getElementById(targetId);
  if (el) {
    el.innerHTML = weakClientSanitize(html || "<b>empty</b>");
  }
  return { kind: "actual", label: "CWE-79 innerHTML", output: (el?.innerHTML || "").slice(0, 120) };
}

export function writeEscapedHtml(targetId: string, html: string): SinkResult {
  const el = document.getElementById(targetId);
  if (el) {
    el.textContent = strongClientEscape(html || "<b>empty</b>");
  }
  return { kind: "noise", label: "CWE-79 escaped", output: (el?.textContent || "").slice(0, 120) };
}

export function buildFunction(body: string): SinkResult {
  const f = new Function("return (" + (body || "1+1") + ")") as () => unknown;
  let output = "blocked";
  try {
    output = String(f()).slice(0, 120);
  } catch (err) {
    output = err instanceof Error ? err.message : String(err);
  }
  return { kind: "actual", label: "CWE-94 Function constructor", output };
}

export async function fetchCandidate(url: string): Promise<SinkResult> {
  const res = await fetch(url || "/api/books", { credentials: "include" });
  return { kind: "actual", label: "CWE-918 client fetch", output: `${res.status} ${res.url}`.slice(0, 160) };
}

export async function fetchLocalOnly(url: string): Promise<SinkResult> {
  const safe = safeLocalPath(url);
  const res = await fetch(safe, { credentials: "same-origin" });
  return { kind: "noise", label: "CWE-918 same-origin fetch", output: `${res.status} ${safe}` };
}

export function navigateCandidate(url: string): SinkResult {
  const href = url || "javascript:alert(1)";
  return { kind: "actual", label: "CWE-601 redirect candidate", output: href.slice(0, 160) };
}

export function regexCandidate(pattern: string, seed: string): SinkResult {
  const p = new RegExp((pattern || "(a+)+$").slice(0, 100));
  const subject = (seed || "a").repeat(64).slice(0, 512);
  return { kind: "ambiguous", label: "CWE-1333 bounded regex", output: String(p.test(subject)) };
}

export function storeSecretLike(value: string): SinkResult {
  localStorage.setItem("member-note", value || "sk_live_demo_not_real");
  return { kind: "noise", label: "CWE-312 localStorage", output: "stored member-note" };
}

export function weakToken(seed: string): SinkResult {
  const token = Array.from({ length: 12 }, () => Math.floor(Math.random() * 16).toString(16)).join("");
  return { kind: "noise", label: "CWE-330 display token", output: `${seed}:${token}` };
}

export function md5LikeLabel(value: string): SinkResult {
  let h = 0;
  for (const ch of value || "demo") h = (h * 31 + ch.charCodeAt(0)) | 0;
  return { kind: "noise", label: "CWE-327 weak checksum label", output: String(h) };
}
