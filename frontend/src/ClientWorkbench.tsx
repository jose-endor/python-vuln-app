import React, { useState } from "react";

import { collectWorkbenchContext, datasetNote } from "./browserContext";
import { decodeMemberToken, mergePreferenceKey, mergeWorkbenchContext } from "./clientPreferences";
import { renderPublisherCopy } from "./publisherCopy";
import {
  contentFingerprint,
  continuePartnerHandoff,
  createDraftToken,
  evaluateFormulaHelper,
  fetchPartnerResource,
  fetchStorefrontResource,
  runPatternCheck,
  saveDraftNote,
  writeHtmlPreview,
  writeTextPreview,
  type ActionResult,
} from "./workbenchActions";

function showResult(r: ActionResult): string {
  return `${r.kind}:${r.label}: ${r.output}`;
}

export const ClientWorkbench: React.FC = () => {
  const [input, setInput] = useState("<b>Member preview</b> /api/books");
  const [result, setResult] = useState("");

  const runBrowserChain = async (mode: string) => {
    const src = collectWorkbenchContext(input + " " + datasetNote("workbench-dataset-source"));
    const payload = mergeWorkbenchContext(src);
    try {
      if (mode === "html") setResult(showResult(writeHtmlPreview("workbench-output", payload.html)));
      else if (mode === "publisher-copy") {
        setResult(showResult(writeHtmlPreview("workbench-output", renderPublisherCopy(payload.html))));
      }
      else if (mode === "text") setResult(showResult(writeTextPreview("workbench-output", payload.html)));
      else if (mode === "formula") setResult(showResult(evaluateFormulaHelper(payload.tokenSeed)));
      else if (mode === "partner-fetch") setResult(showResult(await fetchPartnerResource(payload.url)));
      else if (mode === "storefront-fetch") setResult(showResult(await fetchStorefrontResource(payload.url)));
      else if (mode === "handoff") setResult(showResult(continuePartnerHandoff(payload.url)));
      else if (mode === "pattern") setResult(showResult(runPatternCheck(payload.regex, payload.tokenSeed)));
      else if (mode === "store") setResult(showResult(saveDraftNote(payload.html)));
      else if (mode === "token") setResult(showResult(createDraftToken(payload.tokenSeed)));
      else if (mode === "fingerprint") setResult(showResult(contentFingerprint(payload.html)));
      else if (mode === "member-token") {
        setResult(`preview:member token: ${JSON.stringify(decodeMemberToken(input)).slice(0, 120)}`);
      }
      else if (mode === "preference") {
        setResult(`live:merge: ${JSON.stringify(mergePreferenceKey(payload.objectKey, input))}`);
      }
    } catch (err) {
      setResult(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <section className="panel workbench-panel" aria-label="Partner operations">
      <h2>Partner operations</h2>
      <p className="small muted">
        Preview publisher content and review partner storefront settings.
      </p>
      <div id="workbench-dataset-source" data-note="dataset-note" hidden />
      <div className="form">
        <input className="inline" value={input} onChange={(e) => setInput(e.target.value)} />
        <div className="button-row">
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("html")}>
            HTML preview
          </button>
          <button
            type="button"
            className="btn-ghost small-btn"
            onClick={() => void runBrowserChain("publisher-copy")}
          >
            Publisher copy
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("text")}>
            Text preview
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("formula")}>
            Formula helper
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("partner-fetch")}>
            Remote fetch
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("storefront-fetch")}>
            Storefront fetch
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("pattern")}>
            Pattern check
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("store")}>
            Local note
          </button>
          <button type="button" className="btn-ghost small-btn" onClick={() => void runBrowserChain("preference")}>
            Preference key
          </button>
        </div>
      </div>
      <div id="workbench-output" className="workbench-output" />
      {result && <p className="small muted">{result}</p>}
    </section>
  );
};
