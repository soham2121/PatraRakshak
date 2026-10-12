import { useState, type FormEvent } from "react";
import { Results } from "./Results";
import type { ScanResult } from "./types";

export default function App() {
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [inputKey, setInputKey] = useState(0); // bump to reset the native file input
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true); setError(""); setResult(null);
    const body = new FormData();
    if (file) body.append("file", file); else body.append("text", text);
    try {
      const res = await fetch("/api/v1/scan", { method: "POST", body });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : `Scan failed (${res.status}).`);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan failed.");
    } finally {
      setBusy(false);
    }
  }

  function clear() {
    setText(""); setFile(null); setResult(null); setError(""); setInputKey((k) => k + 1);
  }

  return (
    <main>
      <h1>PatraRakshak</h1>
      <p>Flags passages that look like prompt-injection attempts. It is a detector, not a guarantee.</p>
      <form onSubmit={onSubmit}>
        <label htmlFor="text">Paste text</label>
        <textarea id="text" rows={10} value={text} disabled={!!file} onChange={(e) => setText(e.target.value)} />
        <label htmlFor="file">or upload a .txt, .pdf or .docx file (max 5 MB)</label>
        <input key={inputKey} id="file" type="file" accept=".txt,.pdf,.docx"
               onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <button type="submit" disabled={busy || (!file && !text.trim())}>{busy ? "Scanning…" : "Scan"}</button>
        <button type="button" onClick={clear}>Clear</button>
      </form>
      <div aria-live="polite">
        {error && <p role="alert">{error}</p>}
        {result && <Results result={result} />}
      </div>
    </main>
  );
}
