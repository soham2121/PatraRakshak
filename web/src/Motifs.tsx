// Decorative Maharashtra / India motifs. Purely visual: hidden from screen readers.

/** Saffron swallowtail Bhagwa flag on a pole; the cloth waves via CSS. */
export function BhagwaFlag({ className = "" }: { className?: string }) {
  return (
    <svg className={`bhagwa ${className}`} viewBox="0 0 40 44" width="34" height="38" aria-hidden="true" focusable="false">
      <line x1="4" y1="4" x2="4" y2="43" stroke="#6b4423" strokeWidth="2.5" strokeLinecap="round" />
      <circle cx="4" cy="3.5" r="2.6" fill="#d4a017" />
      <path className="bhagwa-cloth" d="M5 6 L37 12.5 L16 18 L37 24 L5 29 Z" fill="var(--accent)" />
    </svg>
  );
}

/** 24-spoke Ashoka Chakra, used as the loading spinner while a scan runs. */
export function Chakra() {
  return (
    <svg className="chakra" viewBox="-12 -12 24 24" width="18" height="18" aria-hidden="true" focusable="false">
      <circle r="10.5" fill="none" stroke="currentColor" strokeWidth="1.6" />
      <circle r="2" fill="currentColor" />
      {Array.from({ length: 24 }, (_, i) => (
        <line key={i} x1="0" y1="0" x2="0" y2="-10" stroke="currentColor" strokeWidth="0.8" transform={`rotate(${i * 15})`} />
      ))}
    </svg>
  );
}
