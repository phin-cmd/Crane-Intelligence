# Crane Intelligence — Brand & Logo Handoff
_Last updated: 2025-09-08_

This package contains the core brand assets and implementation guides to match the Bloomberg-terminal aesthetic used across the app and PDF reports.

## Contents
- `assets/` SVGs (wordmarks, lockups, monogram, favicon, manifest)
- `code/brand-tokens.css` CSS variables + base classes
- `code/Logo.tsx` React component (Next.js friendly)
- `code/site-head.html` Snippet for favicons/manifest
- `docs/logo-usage.md` Usage rules & do/don’t
- `docs/implementation-checklist.md` Step-by-step integration

## Color Tokens
- Background: `#121212`
- Panel: `#161616`
- Grid line: `#2A2A2A`
- Text: `#EAEAEA`
- Muted: `#B0B0B0`
- Accent (yellow): `#FFD600`
- Accent (amber): `#FF9800`
- Up: `#00FF85`
- Down: `#FF3B3B`

## Typography
Use **Inter**, **Roboto Condensed**, or **IBM Plex Sans**. Headers bold; small caps for section titles; data text 12–14px.

## Logo Files
- Wordmarks: `CI_wordmark_terminal_light.svg` (for dark BG), `CI_wordmark_terminal_dark.svg` (for light BG)
- Lockups: `CI_lockup_horizontal.svg`, `CI_lockup_vertical.svg`
- Marks: `CI_monogram_ci.svg`, `CI_mark_boom.svg`
- Favicon: `favicon.svg`

## Minimum Sizes
- Wordmark: ≥ 24px height
- Lockup: ≥ 28px height
- Favicon: 16–64px (SVG scales)

## Clearspace
Leave at least the height of the vertical yellow bar as padding around the mark/wordmark.

## Backgrounds
- Use LIGHT wordmark on charcoal/black backgrounds.
- Use DARK wordmark on white/light backgrounds.
- Avoid gradients behind the logo.

## Reports
Top-left placement, 24–28px height, no shadows. Use monochrome versions for print/export.

---

### Frontend Integration (Quick Start)
1. Copy `assets/` to your `/public/assets/` folder (Next.js).
2. Import `brand-tokens.css` globally (e.g., in `_app.tsx` or `layout.tsx`).
3. Add `site-head.html` tags to your `<Head>` component.
4. Use `<Logo lockup="wordmark" variant="dark" />` for the website header.
5. Use `<Logo lockup="horizontal" variant="dark" />` for PDFs/report covers.

### PDF/Reports
Use the lockup on the cover page and the plain wordmark within headers. Stick to the token colors and small caps section headings for the “terminal” feel.
