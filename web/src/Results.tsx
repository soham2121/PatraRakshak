import type { Lang, Strings } from "./i18n";
import type { ScanResult } from "./types";

const LOCALE: Record<Lang, string> = { en: "en-IN", mr: "mr-IN", hi: "hi-IN" };

function Flag({ on, t }: { on: boolean; t: Strings }) {
  return on ? <abbr className="flag" title={t.high}>H</abbr> : null;
}

type Props = { result: ScanResult | null; scannedAt: Date | null; lang: Lang; t: Strings };

export function Results({ result, scannedAt, lang, t }: Props) {
  function download() {
    if (!result) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(result, null, 2)], { type: "application/json" }));
    Object.assign(document.createElement("a"), { href: url, download: "patrarakshak-report.json" }).click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  }
  const flagged = result?.label === "suspicious";
  const invisible = !!result?.signals.includes("invisible_characters");
  const dash = "—";
  return (
    <section key={scannedAt?.getTime()} className={result ? "filled" : "blank"}>
      <div className="report-head">
        <h2>{t.report}</h2>
        <p>
          {t.model} {result?.model_version ?? dash}
          {scannedAt && <> · {scannedAt.toLocaleString(LOCALE[lang], { dateStyle: "medium", timeStyle: "short" })}</>}
          {result?.source.name && <> · {result.source.name}</>}
        </p>
      </div>
      {result ? (
        <>
          <p className={`verdict ${flagged ? "is-flagged" : "is-clear"}`}>{flagged ? t.suspicious : t.benign}</p>
          <p className="verdict-note">{flagged ? t.above : t.within}</p>
        </>
      ) : (
        <p className="empty">{t.empty}</p>
      )}
      <table className="results">
        <thead>
          <tr><th scope="col">{t.test}</th><th scope="col">{t.value}</th><th scope="col">{t.reference}</th><th scope="col">{t.flag}</th></tr>
        </thead>
        <tbody>
          <tr className={flagged ? "out" : undefined}>
            <th scope="row">{t.score}</th>
            <td>{result ? result.score.toFixed(4) : dash}</td>
            <td>{result ? `< ${result.threshold.toFixed(4)}` : dash}</td>
            <td><Flag on={flagged} t={t} /></td>
          </tr>
          <tr className={invisible ? "out" : undefined}>
            <th scope="row">{t.invisible}</th>
            <td>{result ? (invisible ? t.detected : t.none) : dash}</td>
            <td>{t.none}</td>
            <td><Flag on={invisible} t={t} /></td>
          </tr>
          <tr>
            <th scope="row">{t.chunks}</th>
            <td>{result ? result.chunks_scanned : dash}</td><td>{dash}</td><td />
          </tr>
          <tr>
            <th scope="row">{t.chars}</th>
            <td>{result ? result.source.chars.toLocaleString("en-IN") : dash}</td><td>{dash}</td><td />
          </tr>
        </tbody>
      </table>
      {result?.truncated && <p className="note">{t.truncated}</p>}
      {invisible && <p className="note">{t.invisibleNote}</p>}
      {result && (
        <>
          <h3>{t.passages}</h3>
          {result.segments.length > 0 ? (
            <>
              <table className="passages">
                <thead>
                  <tr>
                    <th scope="col">{t.passage}</th>
                    {result.source.kind === "pdf" && <th scope="col">{t.page}</th>}
                    <th scope="col">{t.scoreCol}</th><th scope="col">{t.flag}</th>
                  </tr>
                </thead>
                <tbody>
                  {result.segments.map((s) => (
                    <tr key={s.start}>
                      <td><blockquote>{s.text}</blockquote></td>
                      {result.source.kind === "pdf" && <td>{s.page}</td>}
                      <td>{s.score.toFixed(4)}</td>
                      <td><Flag on t={t} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="note">{t.overlap}</p>
            </>
          ) : (
            <p className="note">{t.noPassages}</p>
          )}
          <div className="actions no-print">
            <button type="button" onClick={download}>{t.download}</button>
            <button type="button" onClick={() => window.print()}>{t.print}</button>
          </div>
        </>
      )}
      <p className="disclaimer">PatraRakshak · {t.disclaimer}</p>
    </section>
  );
}
