import type { ScanResult } from "./types";

export function Results({ result }: { result: ScanResult }) {
  function download() {
    const url = URL.createObjectURL(new Blob([JSON.stringify(result, null, 2)], { type: "application/json" }));
    Object.assign(document.createElement("a"), { href: url, download: "patrarakshak-report.json" }).click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  }
  return (
    <section>
      <h2>{result.label === "suspicious" ? "Suspicious content found" : "Nothing flagged"}</h2>
      <p>
        Score {result.score.toFixed(4)} (flag threshold {result.threshold.toFixed(4)}) · model {result.model_version} ·{" "}
        {result.chunks_scanned} chunks scanned
        {result.truncated && " · only the first 100,000 characters were scanned"}
      </p>
      {result.signals.includes("invisible_characters") && (
        <p>This text contains invisible Unicode characters, a common way to hide instructions.</p>
      )}
      {result.segments.length > 0 && <h3>Flagged passages (overlapping chunks are shown separately)</h3>}
      <ol>
        {result.segments.map((s) => (
          <li key={s.start}>
            <blockquote>{s.text}</blockquote>
            <small>score {s.score.toFixed(4)}{s.page !== null && ` · page ${s.page}`}</small>
          </li>
        ))}
      </ol>
      <button type="button" onClick={download}>Download report (JSON)</button>{" "}
      <button type="button" onClick={() => window.print()}>Print</button>
    </section>
  );
}
