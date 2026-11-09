# shahinfar.me

Personal portfolio and résumé site for Ehsan Shahinfar — a static site with no build step.

- `index.html` — English content
- `de/index.html` — German content (keep in sync with the English page)
- `styles.css` — styling (light/dark themes, responsive, print-friendly)
- `script.js` — theme toggle and navigation highlighting

## Preview locally

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

## Deploy

The site is ready for GitHub Pages: in the repository settings, set Pages to deploy from the
default branch (root folder). `CNAME` points the site at `shahinfar.me`.
