import { useEffect, useState, type FormEvent } from "react";
import { LANGS, STRINGS, type Lang } from "./i18n";
import { Results } from "./Results";
import type { ScanResult } from "./types";

function savedLang(): Lang {
  try {
    const v = localStorage.getItem("lang");
    if (v && v in LANGS) return v as Lang;
  } catch { /* storage blocked: fall back to English */ }
  return "en";
}

export default function App() {
  const [lang, setLang] = useState<Lang>(savedLang);
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [inputKey, setInputKey] = useState(0); // bump to reset the native file input
  const [result, setResult] = useState<ScanResult | null>(null);
  const [scannedAt, setScannedAt] = useState<Date | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const t = STRINGS[lang];

  useEffect(() => {
    document.documentElement.lang = lang;
    try { localStorage.setItem("lang", lang); } catch { /* not persisted; fine */ }
  }, [lang]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true); setError(""); setResult(null);
    const body = new FormData();
    if (file) body.append("file", file); else body.append("text", text);
    try {
      const res = await fetch("/api/v1/scan", { method: "POST", body });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : `${t.failed} (${res.status})`);
      setResult(data); setScannedAt(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : t.failed);
    } finally {
      setBusy(false);
    }
  }

  function clear() {
    setText(""); setFile(null); setResult(null); setError(""); setInputKey((k) => k + 1);
  }

  return (
    <>
      <header className="letterhead">
        <div className="letterhead-inner">
          <div>
            <h1>PatraRakshak</h1>
            <p>{t.tagline} {t.disclaimer}</p>
          </div>
          <fieldset className="langs">
            <legend className="sr-only">{t.language}</legend>
            {(Object.keys(LANGS) as Lang[]).map((l) => (
              <label key={l} lang={l}>
                <input type="radio" name="lang" value={l} checked={lang === l} onChange={() => setLang(l)} />
                <span>{LANGS[l]}</span>
              </label>
            ))}
          </fieldset>
        </div>
      </header>
      <main className="layout">
        <form className="sheet sample" onSubmit={onSubmit}>
          <h2>{t.sample}</h2>
          <label htmlFor="text">{t.paste}</label>
          <textarea id="text" rows={14} value={text} disabled={!!file} onChange={(e) => setText(e.target.value)} />
          <label htmlFor="file">{t.file}</label>
          <div className="file-row">
            <input key={inputKey} id="file" type="file" accept=".txt,.pdf,.docx" className="sr-only"
                   onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
            <label htmlFor="file" className="file-button" aria-hidden="true">{t.chooseFile}</label>
            <span className="file-name">{file?.name ?? t.noFile}</span>
          </div>
          <div className="actions">
            <button type="submit" className="primary" disabled={busy || (!file && !text.trim())}>{busy ? t.scanning : t.scan}</button>
            <button type="button" onClick={clear}>{t.clear}</button>
          </div>
        </form>
        <div className="sheet report" aria-live="polite" aria-busy={busy}>
          {error && <p className="error" role="alert">{error}</p>}
          <Results result={result} scannedAt={scannedAt} lang={lang} t={t} />
        </div>
      </main>
    </>
  );
}
