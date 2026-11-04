---
name: PatraRakshak
description: Prompt-injection scanner whose result reads like a diagnostic lab report.
colors:
  teal: "#0e5c63"
  teal-deep: "#0a464c"
  teal-wash: "#e3eeee"
  ground: "#eef4f4"
  paper: "#ffffff"
  ink: "#1d2328"
  ink-soft: "#4d5a63"
  rule: "#cfdcdd"
  flag: "#c62828"
  flag-wash: "#fbeaea"
  clear: "#1f6b45"
typography:
  verdict:
    fontFamily: "Mukta, system-ui, sans-serif"
    fontSize: "clamp(2.2rem, 4vw, 3rem)"
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "-0.02em"
  brand:
    fontFamily: "Mukta, system-ui, sans-serif"
    fontSize: "1.6rem"
    fontWeight: 800
    lineHeight: 1.1
  heading:
    fontFamily: "Mukta, system-ui, sans-serif"
    fontSize: "1.3rem"
    fontWeight: 800
    lineHeight: 1.2
  body:
    fontFamily: "Mukta, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.55
  column-head:
    fontFamily: "Mukta, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    letterSpacing: "0.06em"
  note:
    fontFamily: "Mukta, system-ui, sans-serif"
    fontSize: "0.85rem"
    fontWeight: 400
rounded:
  sm: "3px"
  md: "4px"
  lg: "6px"
spacing:
  sm: "12px"
  md: "24px"
  lg: "32px"
  xl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.teal}"
    textColor: "{colors.paper}"
    rounded: "{rounded.md}"
    padding: "10px 28px"
  button-primary-hover:
    backgroundColor: "{colors.teal-deep}"
  button-secondary:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.teal}"
    rounded: "{rounded.md}"
    padding: "10px 20px"
  button-secondary-hover:
    backgroundColor: "{colors.teal-wash}"
  sheet:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.md}"
    padding: "28px 32px"
  flag-h:
    textColor: "{colors.flag}"
    rounded: "{rounded.sm}"
---

# Design System: PatraRakshak

## Overview

The scan result is a diagnostic lab report: the measured value, the reference limit beside it, and an **H** flag when the value is out of range. It refuses the security-dashboard default (dark grounds, shields, glowing badges). A demo audience reads the verdict word first, then the row that justifies it, then the exact passages. Light, white paper forms on a pale teal-grey ground; the light theme suits a projector or a lit room.

## Colors

### Primary
- **Letterhead Teal** (`teal`): the letterhead band, primary button, report rules, column heads. **Teal Deep** for hover.

### Neutral
- **Ground** behind the sheets, **Paper** for sheets, **Ink** for text, **Ink Soft** for notes and meta, **Rule** for hairlines, **Teal Wash** for hover and disabled fields.

### Named Rules
- **The Out-of-Range Rule.** **Flag Red** (`flag`) appears only on a value above its reference limit, its H flag, the flagged passage underline, and the Suspicious verdict. Never decoration.
- **Clear Green** (`clear`) is used only for the Not flagged verdict.

## Typography

Mukta (Ek Type) for everything, because it covers Latin and Devanagari in one family; self-hosted via `@fontsource/mukta` (400, 600, 800). Numerals in tables are tabular.

### Hierarchy
- **Verdict**: 800, up to 3rem, the largest thing on screen.
- **Heading**: 800, 1.3rem, sheet titles over a 2px teal rule.
- **Body**: 17px / 1.55.
- **Column head**: 600, 0.75rem, uppercase, tracked, teal. In Marathi and Hindi tracking is 0 and size 0.85rem (tracking breaks Devanagari shaping).
- **Note**: 0.85rem, Ink Soft.

## Layout

Max width 1440px. Desktop: two columns 5:7 (sample form, report), 32px gap, 48px side padding; the sample form is sticky. Under 960px: one column, 16px gutter. Print hides the letterhead tagline, language switch, sample form and action buttons.

## Elevation & Depth

Sheets sit on the ground with a hairline border plus a soft two-layer shadow (`0 1px 2px #0e5c6314, 0 8px 24px -12px #0e5c6326`). Nothing else is elevated.

## Shapes

Small radii only: 3px (H flag), 4px (sheets, buttons, inputs), 6px (language switch). Tables are open: hairline row rules, no cell borders.

## Components

### Buttons
Primary is solid teal, secondary is teal outline on paper. Disabled at 45% opacity.

### Inputs / Fields
Textarea on a near-white field with a teal-grey border; disabled (when a file is chosen) on Teal Wash. The file input is visually hidden behind a translated outline button plus the file name.

### Navigation
The letterhead holds the name, tagline and an EN / मराठी / हिंदी segmented switch built from native radio inputs; the checked option is white on teal.

### Report tables
Test / Value / Reference / Flag. Out-of-range values turn red and bold; the Flag cell shows a boxed red **H** (`<abbr title="High">`). Flagged passages get a red underline and a Page column for PDFs.

### Motion
One moment: when a result lands, the verdict and each table row print in left to right (clip-path, 460ms, ease-out-expo, 50ms stagger). Off under reduced motion.

## Do's and Don'ts

### Do:
- Print the threshold beside every score, to 4 decimals.
- Show only what the API returns.
- Keep red for out-of-range values.

### Don't:
- Don't add shields, padlocks, or dark security-console styling.
- Don't add cards inside the sheets.
- Don't use letter-spacing on Devanagari text.
