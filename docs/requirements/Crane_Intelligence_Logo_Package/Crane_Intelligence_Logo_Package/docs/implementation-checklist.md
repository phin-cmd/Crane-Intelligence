
# Implementation Checklist

- [ ] Copy `/assets` into `/public/assets` (Next.js) or your static dir.
- [ ] Include `<link rel="icon" ...>` and manifest from `code/site-head.html`.
- [ ] Import `code/brand-tokens.css` globally.
- [ ] Replace existing navbar logo with `<Logo lockup="wordmark" variant="dark" height={32} />`.
- [ ] Update PDF templates to use `horizontal` lockup at 28px height.
- [ ] Verify contrast on orange hero and charcoal headers.
- [ ] Generate 32px PNG fallbacks for legacy browsers (optional).
