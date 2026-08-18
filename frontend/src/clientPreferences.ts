import qs from "qs";

import type { WorkbenchContext } from "./browserContext";

export type ClientWorkbenchPayload = {
  html: string;
  url: string;
  regex: string;
  objectKey: string;
  tokenSeed: string;
};

export function trimMarkup(value: string): string {
  return (value || "").replace(/<script/gi, "<scrubbed");
}

export function normalizeText(value: string): string {
  return (value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export function mergeWorkbenchContext(src: WorkbenchContext): ClientWorkbenchPayload {
  const parsed = qs.parse((src.query || "").replace(/^\?/, ""));
  const rawUrl = String(parsed.next || parsed.u || src.formValue || "/api/books");
  return {
    html: [src.hash, src.stored, src.formValue].filter(Boolean).join(" "),
    url: rawUrl,
    regex: String(parsed.pattern || src.formValue || "(a+)+$"),
    objectKey: String(parsed.key || "__proto__"),
    tokenSeed: String(parsed.seed || src.formValue || "stack"),
  };
}

export function localStorefrontPath(candidate: string): string {
  try {
    const u = new URL(candidate || "/api/books", window.location.origin);
    if (u.origin !== window.location.origin) return "/api/books";
    return u.pathname + u.search;
  } catch {
    return "/api/books";
  }
}

export function decodeMemberToken(token: string): Record<string, unknown> {
  const parts = (token || "e30.e30.").split(".");
  try {
    return JSON.parse(atob(parts[1] || "e30")) as Record<string, unknown>;
  } catch {
    return {};
  }
}

export function mergePreferenceKey(key: string, value: string): Record<string, unknown> {
  const target: Record<string, unknown> = {};
  const bag: Record<string, unknown> = { [key || "__proto__"]: { memberValue: value || "yes" } };
  return Object.assign(target, bag);
}
