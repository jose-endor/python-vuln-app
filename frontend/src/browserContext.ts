export type WorkbenchContext = {
  hash: string;
  query: string;
  stored: string;
  formValue: string;
  origin: string;
};

export function collectWorkbenchContext(formValue: string): WorkbenchContext {
  if (typeof window === "undefined") {
    return { hash: "", query: "", stored: "", formValue, origin: "" };
  }
  return {
    hash: window.location.hash.slice(1),
    query: window.location.search,
    stored: window.localStorage.getItem("member-note") || "",
    formValue,
    origin: window.location.origin,
  };
}

export function datasetNote(id: string): string {
  if (typeof document === "undefined") return "";
  return document.getElementById(id)?.dataset?.note || "";
}
