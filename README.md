# MAC-Bench project site

Source of the project site, to be served at https://mac-bench.github.io once published. One self-contained page.

```bash
python build.py                          # src/ + data/ -> index.html and preview/artifact.html
python build.py --sync ../MAC-benchmark  # refresh data/ticketing.json from the code repository first
```

| Path | Content |
|---|---|
| `src/body.html`, `src/styles.css`, `src/app.js` | Markup, styles, behaviour |
| `src/figs/` | Architecture figures as inline SVG |
| `src/progress.json` | The progress list. Edit this file to tick an item or mark it accepted |
| `data/ticketing.json` | The ticketing interface, exported by the code repository |
| `data/ticketing_world.json` | The dev world and sample searches |
| `data/ticketing_session.json`, `data/ticketing_after_session.json` | The two recorded sessions |
