# MAC-Bench project site

Source of the project site, to be served at https://mac-bench.github.io once published. One self-contained page.

```bash
python build.py                          # src/ + data/ -> index.html and preview/artifact.html
python build.py --sync ../MAC-benchmark  # refresh data/ from the code repository's build/ first
python tools/export_shopping.py ../MAC-benchmark  # refresh purchase task settings and regenerate run logs
```

| Path | Content |
|---|---|
| `src/body.html`, `src/styles.css`, `src/app.js` | Markup, styles, behaviour |
| `src/scenarios.py`, `src/scenarios.css` | Scenario introductions, workflow diagrams, and the types of task with the task that stands for each: its steps, right outcome and the careless agent it fails. The build checks that every family has a type and every representative belongs to its type |
| `src/multiagent.py`, `src/multiagent.css` | The Multi-agent page: the three conditions, the contract of each role, and the tasks of the set ma1 from `data/ma1.json` |
| `src/insurance.html`, `src/claims.js` | The Insurance page and what fills it from `data/insurance.json` |
| `src/shopping.html`, `src/shopping.py`, `src/shopping.js` | The Shopping purchase page, with task settings and expandable run logs |
| `data/shopping.json`, `data/shopping_runs.json` | Purchase fixtures, interface examples and replay-verified logs from the reference and each family's careless agent |
| `src/figs/` | Architecture figures as inline SVG |
| `src/progress.json` | The progress list. Edit this file to tick an item or mark it accepted |
| `data/ticketing.json` | The ticketing interface, exported by the code repository |
| `data/ticketing_world.json` | The dev world and sample searches |
| `data/ticketing_session.json`, `data/ticketing_after_session.json` | The two recorded sessions |
| `data/ticketing_tasks.json` | The development tasks with role cards and reference score cards |
| `data/insurance.json` | The claims scenario: seats, actions, rules, modules, checks, and every task with its scripted runs. Written by `tools/export_claims.py` |
| `data/ma1.json` | The multi-agent set ma1: every task's seats, private facts, dependencies, ways it fails and admission in brief. Written by `tools/export_ma.py` |
