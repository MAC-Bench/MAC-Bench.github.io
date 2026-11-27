#!/usr/bin/env python
"""Assemble the site from src/ and data/.

    python build.py            # writes index.html (GitHub Pages) and preview/artifact.html

index.html is one self-contained file: styles, script and data are inlined, so it opens
from disk as well. The files in data/ are copies of what the code repository's export tools
write under build/; refresh them with `python build.py --sync ../MAC-benchmark`.
"""
import json
import pathlib
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

from src.scenarios import render as render_scenario
from src.shopping import render as render_shopping

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "src"
FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800"
         "&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap")
TITLE = "MAC-Bench"
DESCRIPTION = ("A benchmark for language-model agents that act for different people and have to "
               "coordinate: flight ticketing, auto-insurance claims and online shopping.")
VOID = {"meta", "link", "br", "hr", "img", "input", "line", "rect", "path", "circle"}


def embed(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append((tag, self.getpos()))
        else:
            self.stack.pop()


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--sync":
        code = pathlib.Path(sys.argv[2]) / "build"
        shutil.copy(code / "interface" / "ticketing.json", HERE / "data" / "ticketing.json")
        shutil.copy(code / "world" / "ticketing_dev.json", HERE / "data" / "ticketing_world.json")
        shutil.copy(code / "demo" / "ticketing_session.json", HERE / "data" / "ticketing_session.json")
        shutil.copy(code / "demo" / "ticketing_after_session.json", HERE / "data" / "ticketing_after_session.json")
        shutil.copy(code / "tasks" / "ticketing_dev.json", HERE / "data" / "ticketing_tasks.json")
        shutil.copy(code / "claims" / "insurance_dev.json", HERE / "data" / "insurance.json")
    ticketing = json.loads((HERE / "data" / "ticketing.json").read_text(encoding="utf-8"))
    world = json.loads((HERE / "data" / "ticketing_world.json").read_text(encoding="utf-8"))
    session = [json.loads((HERE / "data" / name).read_text(encoding="utf-8"))
               for name in ("ticketing_session.json", "ticketing_after_session.json")]
    progress = json.loads((SRC / "progress.json").read_text(encoding="utf-8"))
    css = "\n".join((SRC / name).read_text(encoding="utf-8") for name in ("styles.css", "scenarios.css"))
    js = (SRC / "app.js").read_text(encoding="utf-8")
    world_js = (SRC / "world.js").read_text(encoding="utf-8")
    session_js = (SRC / "session.js").read_text(encoding="utf-8")
    tasks_js = (SRC / "tasks.js").read_text(encoding="utf-8")
    tasks = json.loads((HERE / "data" / "ticketing_tasks.json").read_text(encoding="utf-8"))
    claims_js = (SRC / "claims.js").read_text(encoding="utf-8")
    claims = json.loads((HERE / "data" / "insurance.json").read_text(encoding="utf-8"))
    shopping_js = (SRC / "shopping.js").read_text(encoding="utf-8")
    shopping = json.loads((HERE / "data" / "shopping.json").read_text(encoding="utf-8"))
    shopping_runs = json.loads((HERE / "data" / "shopping_runs.json").read_text(encoding="utf-8"))
    assert set(shopping_runs) == {task["task_id"] for task in shopping["tasks"]}
    assert all(set(runs) == {"reference", "careless"} for runs in shopping_runs.values())
    body = (SRC / "body.html").read_text(encoding="utf-8")
    assert "<!--VIEW_INSURANCE-->" in body
    body = body.replace("<!--VIEW_INSURANCE-->", (SRC / "insurance.html").read_text(encoding="utf-8").strip())
    assert "<!--VIEW_SHOPPING-->" in body
    body = body.replace("<!--VIEW_SHOPPING-->", render_shopping((SRC / "shopping.html").read_text(encoding="utf-8").strip(), shopping))
    for view, catalog, interface in (("ticketing", tasks, ticketing), ("insurance", claims, claims),
                                     ("shopping", shopping, shopping)):
        marker = f"<!--SCENARIO_{view.upper()}-->"
        assert marker in body, marker
        recorded_tickets = session[1]["tickets"] if view == "ticketing" else ()
        body = body.replace(marker, render_scenario(view, catalog, interface, recorded_tickets))
    for marker, name in (("<!--FIG_LAYERS-->", "fig_layers.html"), ("<!--FIG_RUNTIME-->", "fig_runtime.html"),
                         ("<!--FIG_CLAIMS_PARTIES-->", "fig_claims_parties.html"), ("<!--FIG_CLAIMS_PIPELINE-->", "fig_claims_pipeline.html")):
        fig = (SRC / "figs" / name).read_text(encoding="utf-8").strip()
        ET.fromstring(fig[fig.index("<svg"):fig.index("</svg>") + 6].replace("<svg ", "<svg xmlns='http://www.w3.org/2000/svg' ", 1))
        assert marker in body, marker
        body = body.replace(marker, fig)

    statuses = {i["status"] for g in progress["groups"] for i in g["items"]}
    assert statuses <= {"done", "next", "planned"}, statuses
    ids = [i["id"] for g in progress["groups"] for i in g["items"]]
    assert len(ids) == len(set(ids)), "duplicate progress ids"

    tail = (f'<script type="application/json" id="data-ticketing">{embed(ticketing)}</script>\n'
            f'<script type="application/json" id="data-progress">{embed(progress)}</script>\n'
            f'<script type="application/json" id="data-world">{embed(world)}</script>\n'
            f'<script type="application/json" id="data-tasks">{embed(tasks)}</script>\n'
            f'<script type="application/json" id="data-session">{embed(session)}</script>\n'
            f'<script type="application/json" id="data-claims">{embed(claims)}</script>\n'
            f'<script type="application/json" id="data-shopping-runs">{embed(shopping_runs)}</script>\n'
            f"<script>\n{js}\n</script>\n<script>\n{world_js}\n</script>\n<script>\n{session_js}\n</script>\n<script>\n{tasks_js}\n</script>\n"
            f"<script>\n{claims_js}\n</script>\n<script>\n{shopping_js}\n</script>\n")
    head_common = f'<link rel="stylesheet" href="{FONTS}">\n<style>\n{css}\n</style>\n'

    page = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            f"<title>{TITLE}</title>\n<meta name=\"description\" content=\"{DESCRIPTION}\">\n"
            "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">\n"
            "<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>\n"
            f"{head_common}</head>\n<body>\n{body}\n{tail}</body>\n</html>\n")
    fragment = (f"<title>{TITLE}</title>\n<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n"
                f"{head_common}{body}\n{tail}")

    check = Balance()
    check.feed(body)
    assert not check.errors and not check.stack, (check.errors[:3], check.stack)
    ids = re.findall(r'\sid="([^"{}+]+)"', body)
    assert len(ids) == len(set(ids)), [x for x in ids if ids.count(x) > 1]
    for needed in re.findall(r"byId\('([^']+)'\)", js + world_js + session_js + tasks_js + claims_js + shopping_js):
        assert needed in ids or needed.startswith(("tk-fill", "tk-form", "tk-out")), needed

    (HERE / "index.html").write_text(page, encoding="utf-8")
    (HERE / "preview").mkdir(exist_ok=True)
    (HERE / "preview" / "artifact.html").write_text(fragment, encoding="utf-8")
    done = sum(i["status"] == "done" for g in progress["groups"] for i in g["items"])
    print(f"index.html {len(page.encode('utf-8'))} bytes; {len(ticketing['actions'])} actions; "
          f"{len(world['flights'])} flights; {len(claims['tasks'])} claims tasks; {len(shopping_runs)} shopping tasks with logs; "
          f"{done} of {len([i for g in progress['groups'] for i in g['items']])} items done")


if __name__ == "__main__":
    main()
