import React, { useState } from "react";

import { collectBrowserSources, sourceFromDataset } from "./cweSources";
import { mergeClientSources, prototypeMerge, weakJwtDecode } from "./cweTransforms";
import {
  buildFunction,
  fetchCandidate,
  fetchLocalOnly,
  md5LikeLabel,
  navigateCandidate,
  regexCandidate,
  storeSecretLike,
  weakToken,
  writeEscapedHtml,
  writeUnsafeHtml,
  type SinkResult,
} from "./cweSinks";

function showResult(r: SinkResult): string {
  return `${r.kind}:${r.label}: ${r.output}`;
}

export const CweLab: React.FC = () => {
  const [input, setInput] = useState("<img src=x onerror=alert(1)> u /api/books");
  const [result, setResult] = useState("");

  const runBrowserChain = async (mode: string) => {
    const src = collectBrowserSources(input + " " + sourceFromDataset("cwe-dataset-source"));
    const payload = mergeClientSources(src);
    try {
      if (mode === "html") setResult(showResult(writeUnsafeHtml("cwe-output", payload.html)));
      else if (mode === "safe-html") setResult(showResult(writeEscapedHtml("cwe-output", payload.html)));
      else if (mode === "function") setResult(showResult(buildFunction(payload.tokenSeed)));
      else if (mode === "fetch") setResult(showResult(await fetchCandidate(payload.url)));
      else if (mode === "safe-fetch") setResult(showResult(await fetchLocalOnly(payload.url)));
      else if (mode === "redirect") setResult(showResult(navigateCandidate(payload.url)));
      else if (mode === "regex") setResult(showResult(regexCandidate(payload.regex, payload.tokenSeed)));
      else if (mode === "store") setResult(showResult(storeSecretLike(payload.html)));
      else if (mode === "token") setResult(showResult(weakToken(payload.tokenSeed)));
      else if (mode === "hash") setResult(showResult(md5LikeLabel(payload.html)));
      else if (mode === "jwt") setResult(`noise:CWE-347 unsigned parse: ${JSON.stringify(weakJwtDecode(input)).slice(0, 120)}`);
      else if (mode === "pollute") setResult(`actual:CWE-915 merge: ${JSON.stringify(prototypeMerge(payload.objectKey, input))}`);
    } catch (err) {
      setResult(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <section className="panel cwe-panel" aria-label="Client CWE lab">
      <h2>CWE client lab</h2>
      <p className="small muted">
        Browser-side SAST corpus: source collection, propagation, and sinks are split across TypeScript modules.
      </p>
      <div id="cwe-dataset-source" data-note="dataset-note" hidden />
      <div className="form">
        <input className="inline" value={input} onChange={(e) => setInput(e.target.value)} />
        <div className="button-row">
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("html")}>
            Unsafe HTML
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("safe-html")}>
            Escaped HTML
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("function")}>
            Function
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("fetch")}>
            Fetch
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("safe-fetch")}>
            Safe fetch
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("regex")}>
            Regex
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("store")}>
            Store
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("pollute")}>
            Merge key
          </button>
        </div>
      </div>
      <div id="cwe-output" className="cwe-output" />
      {result && <p className="small muted">{result}</p>}
    </section>
  );
};
