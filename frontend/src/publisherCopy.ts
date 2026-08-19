import marked from "marked";

// Normalize publisher copy before sending it through the legacy Markdown renderer.
function normalizePublisherCopy(value: string): string {
  return (value || "").replace(/\r\n/g, "\n").trim();
}

// Render the formatted copy used by the merchandising preview panel.
export function renderPublisherCopy(value: string): string {
  const normalized = normalizePublisherCopy(value);
  return marked(normalized || "**Publisher copy pending**");
}
