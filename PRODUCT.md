# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Primary: evaluators of a project demo (judges, professors, reviewers). They watch someone paste text or upload a document and need to read the verdict, and why, at a glance.

## Product Purpose
PatraRakshak scans pasted text and TXT/PDF/DOCX files for prompt-injection passages and shows which passages were flagged and how strongly. It is a detector, not a guarantee. Success: a viewer understands the verdict, the score against the threshold, and the flagged passages without explanation from the presenter.

## Positioning
The shipped model (muril-v1) handles English plus Marathi and Hindi, so it does not false-flag ordinary Marathi/Hindi forms the way an English-only model does. Results are tied to real, measured numbers (see README and MODEL_CARD.md).

## Operating Context
Runs locally: FastAPI serves the built React app and `POST /api/v1/scan` from one port. Nothing logs or stores submitted text. Scans take a few hundred milliseconds to a few seconds on CPU.

## Capabilities and Constraints
- Input: pasted text, or one .txt/.pdf/.docx file up to 5 MB. Only the first 100,000 characters are scanned.
- Output: label (benign/suspicious), max score, threshold, model version, chunks scanned, signals (e.g. invisible Unicode characters), flagged segments with score and PDF page.
- The UI must not invent explanations beyond what the API returns.
- Report download (JSON) and print.
- UI language: English, Marathi and Hindi (toggle). Translations need review by a native speaker.

## Brand Commitments
Name: PatraRakshak. Keep the line "It is a detector, not a guarantee." No logo or palette exists.

## Evidence on Hand
Measured results in README.md, MODEL_CARD.md and `reports/`. Test fixture `tests/fixtures/sample.pdf` (flagged on page 2). No testimonials or users; do not fabricate any.

## Product Principles
- Honest: show the score and threshold, never overstate certainty.
- Legible at a glance for a demo audience.
- Show the evidence: flagged passages, not just a verdict.
- Private by default: nothing stored.

## Accessibility & Inclusion
All controls native and labelled; keyboard usable (TESTING.md Task 7). Devanagari text must render correctly.
