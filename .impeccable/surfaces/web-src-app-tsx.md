---
version: 1
slug: "web-src-app-tsx"
primary_target: "web/src/App.tsx"
related_targets: ["web/src/Results.tsx"]
---

# Scan screen

Scope: the single scan screen of the web UI (paste or upload, then read the report). Mode: Operate.
Audience: demo evaluators reading the verdict at a glance. Task: submit text or a file, read verdict, score vs threshold, flagged passages, export.
Constraints: UI shows only what the API returns; scores to 4 decimals; EN / मराठी / हिंदी UI toggle; native controls, keyboard usable; print-friendly.

## Direction contract

THESIS: The scan result reads like a diagnostic lab report: your value, the reference limit, and an H flag. Refuses the security-dashboard default (dark, shields, badges, cards).
OWN-WORLD: White report forms on pale teal-grey ground (#eef4f4), teal letterhead band (#0e5c63), ink #1d2328, flag red #c62828 only for out-of-range values. Mukta (Latin + Devanagari). Ruled tables with small uppercase teal column heads, tabular numerals, hairline rules.
STORY: The evaluator sees the verdict word, then the row that justifies it (score above the reference limit, flagged H), then the exact passages. They trust it because the threshold is printed beside the value.
FIRST VIEWPORT: Teal letterhead bar: name left, language switch right. Two columns 5:7. Left: sample form (textarea, file input, Run scan, Clear). Right: Screening report: header with model and date, large verdict, result table (Test / Value / Reference / Flag), flagged passage table, Download / Print. Empty report form shows before the first scan.
FORM: Pathology lab report, my rank 1 of 7 (pick card, chosen by user). seed:34fc9b29dec6cbf1
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
