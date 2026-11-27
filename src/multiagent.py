"""The Multi-agent page: one protocol for both scenarios, and the fifteen tasks of the set ma1.

Everything about a task comes from data/ma1.json, written by the code repository's tools/export_ma.py
from the task files and their admission evidence. What is written here by hand: the page's words, one
line per task for the picker, and plain names for the counterfactuals the admission played.
"""
import re
from html import escape

from src.scenarios import icon

CODE = "https://github.com/MAC-Bench/MAC-benchmark/blob/main/"

LINES = {
    "tk-ma-01": "Each traveller's budget and needs are their own; each authorises their own share.",
    "tk-ma-02": "Two routes, and a window for landing together that only the travellers know.",
    "tk-ma-03": "One seat is left at the low fare; only the budgets say who needs it.",
    "tk-ma-04": "Daniel cannot pay the fare alone; only Maya knows she would chip in.",
    "tk-ma-05": "The airline cancels: one wants a new flight, the other the full refund.",
    "tk-ma-06": "Daniel says Maya agrees to cancel. She does not.",
    "tk-ma-07": "Maya must fly a day later; Daniel's ticket must stay as it is.",
    "ic-ma-01": "B claims from both insurers; every part has to be paid exactly once.",
    "ic-ma-02": "Only B's dashboard recording shows who ran the red light.",
    "ic-ma-03": "The recording has to reach A's insurer by way of B's insurer.",
    "ic-ma-04": "An 80/20 split that rests on a police report arriving on day ten.",
    "ic-ma-05": "A's liability limit cannot pay both B and B's insurer in full.",
    "ic-ma-06": "B never bought collision cover; A's insurer owes B the car.",
    "ic-ma-07": "B's insurer pays, recovers from A's insurer, and passes the deductible back.",
    "ic-ma-08": "B claims only from A's insurer; nothing moves until B accepts an offer.",
}
CARELESS = {
    "the agent books on the brief alone, asking nobody": "the agent books on the brief alone, asking nobody",
    "the agent is careless: books apart": "the agent books each traveller the cheapest flight on their own route",
    "the agent is careless: richer first": "the agent gives the last cheap seat to the traveller who can afford more",
    "the agent is careless: each pays their own": "the agent has each traveller pay their own fare",
    "the agent is careless: ordinary path": "the agent takes the ordinary refund instead of what the cancellation gives",
    "the agent is careless: one consent is enough": "the agent cancels both tickets on Daniel's word",
    "the agent is careless: never splits": "the agent changes the shared order without splitting Maya off",
    "adjuster_a is careless: never asks": "Insurer A pays without asking what B's own policy covers",
    "adjuster_a is careless: own word": "Insurer A decides fault on its own driver's word",
    "driver_b keeps ev_dashcam_b from every insurer": "Driver B keeps the recording from both insurers",
    "adjuster_a is careless: pays the insurer first": "Insurer A pays B's insurer before B",
    "adjuster_b is careless: pays whatever is claimed": "Insurer B pays for a coverage B never bought",
    "adjuster_b is careless: pays as billed": "Insurer B pays the shop's bill, old damage included",
    "adjuster_a is careless: pays as billed": "Insurer A offers the shop's figure, old damage included",
}
DOMAIN = {
    "ticketing": ("Ticketing", "one booking agent, two travellers"),
    "insurance": ("Claims", "two drivers, two insurers"),
}
ROLES = [
    ("desk", "Booking agent", "acts for both travellers",
     ["never acts without the consent the world asks for", "claims what an airline change entitles a traveller to"],
     ["every traveller ends with what they wanted, within budget, each paying their own"]),
    ("person", "Traveller", "looks after their own trip and money",
     ["states only their true facts"],
     ["has what they wanted", "stays within budget", "pays only for their own ticket unless they said otherwise"]),
    ("car", "Driver", "looks after their own interest, truthfully",
     ["has the car repaired and claims it", "says nothing false", "gives their own insurer what it asks", "pays every bill"],
     ["is paid what their claims give, and not more than the loss"]),
    ("shield", "Adjuster", "handles every claim on its insurer by the rules",
     ["acknowledges, decides, pays, denies, demands and answers as the rules give, in time"],
     ["recovers what the evidence supports from the other insurer"]),
]


def condition_cards():
    def seat(name, kind, judged=False):
        tag = {"m": "model under test", "k": "reference model", "s": "script"}[kind]
        return (f'<span class="ma-seat is-{kind}{" is-judged" if judged else ""}"><b>{name}</b><small>{tag}</small>'
                + ('<i>judged</i>' if judged else '') + '</span>')

    rows = [
        ("A", "Model and scripts", [("Agent", "m", True), ("Maya", "s", False), ("Daniel", "s", False)],
         "The model under test plays one seat. Scripts play the others, and its card states their fixed rules.",
         "its own job against counterparts it can predict"),
        ("B", "Model and a reference model", [("Agent", "m", True), ("Maya", "k", False), ("Daniel", "k", False)],
         "The model under test plays one seat. One fixed reference model plays every other seat, each from its own card.",
         "its job among agents with goals of their own"),
        ("C", "The model in every seat", [("Agent", "m", True), ("Maya", "m", True), ("Daniel", "m", True)],
         "The model under test plays every seat, each in a session of its own with its own card. Every seat is judged.",
         "whether a team of it reaches the joint outcome"),
    ]
    cards = []
    for letter, name, seats, text, measures in rows:
        cards.append(f"""<article class="ma-cond">
        <header><span class="ma-letter">{letter}</span><h3>{escape(name)}</h3></header>
        <div class="ma-seats">{''.join(seat(*s) for s in seats)}</div>
        <p class="ma-world">The world: flights, orders, payments, consent</p>
        <p>{escape(text)}</p>
        <p class="ma-measures"><span>Measures</span>{escape(measures)}</p>
      </article>""")
    legend = (f'<ul class="ma-legend" aria-label="Legend">'
              f'<li><span class="ma-swatch is-m"></span>model under test</li>'
              f'<li><span class="ma-swatch is-k"></span>fixed reference model</li>'
              f'<li><span class="ma-swatch is-s"></span>script</li>'
              f'<li><span class="ma-swatch is-judged"></span>judged seat</li></ul>')
    return legend + f'<div class="ma-conds">{"".join(cards)}</div>'


def role_cards():
    out = []
    for symbol, name, job, own, shared in ROLES:
        out.append(f"""<div class="ma-role">
        <div class="ma-role-head"><span class="scenario-icon">{icon(symbol)}</span><div><h3>{name}</h3><p>{escape(job)}</p></div></div>
        <p class="ma-ctl">Up to the seat</p><ul>{''.join(f'<li>{escape(x)}</li>' for x in own)}</ul>
        <p class="ma-ctl is-shared">Shared with others</p><ul>{''.join(f'<li>{escape(x)}</li>' for x in shared)}</ul>
      </div>""")
    return "".join(out)


def picker(domains, first):
    groups = []
    for key, data in domains.items():
        title, seats = DOMAIN[key]
        cards = []
        for t in data["tasks"]:
            cards.append(f'<button class="type-card" type="button" data-case="{t["id"]}" aria-controls="case-{t["id"]}" '
                         f'aria-pressed="{str(t["id"] == first).lower()}"><span class="type-top">'
                         f'<span class="type-code">{t["id"]}</span><span class="type-count">{escape(t["kind"])}</span></span>'
                         f'<strong>{escape(t["title"])}</strong><small>{escape(LINES[t["id"]])}</small></button>')
        groups.append(f'<div class="type-group"><p class="type-group-label">{title} · {len(cards)} tasks · {seats}</p>'
                      f'<div class="type-grid ma-grid">{"".join(cards)}</div></div>')
    return f'<div class="type-picker" role="group" aria-label="Tasks of the set">{"".join(groups)}</div>'


def task_panel(t, active):
    labels = {s["seat"]: s["label"] for s in t["seats"]}
    seats = []
    for s in t["seats"]:
        focal = '<span class="ma-focal">can be focal</span>' if s["seat"] in t["focal_options"] else ""
        knows = "".join(f"<li>{escape(k)}</li>" for k in s["knows"])
        seats.append(f'<div class="ma-seatcard"><div class="ma-seatcard-head"><div><b>{escape(s["label"])}</b>'
                     f'<small>{escape(s["sub"])}</small></div>{focal}</div><ul>{knows}</ul></div>')
    world = (f'<p class="ma-worldline">{icon("clock")}<span><b>The world:</b> {escape("; ".join(t["world"]))}.</span></p>'
             if t["world"] else "")
    a = t["admission"]
    solved = all(w["joint_met"] for w in a["witnesses"])
    needed = ", ".join(labels[s] for s in a["needed"])
    careless = "".join(f'<li>{escape(CARELESS.get(c["name"], c["name"]))}: the joint result '
                       f'{"holds" if c["joint_met"] else "fails"}</li>' for c in a["careless"])
    said = re.sub(r"^From [\w-]+\. ", "", t["rewritten"] or "")
    rewritten = f'<p class="ma-rewritten"><b>Rewritten from {escape(t["from"])}.</b> {escape(said)}</p>' if t["rewritten"] else ""
    domain = DOMAIN[t["domain"]][0]
    origin = f"from {t['from']}"
    return f"""      <article class="case-panel ma-panel" id="case-{t['id']}" data-case-panel="{t['id']}"{'' if active else ' hidden'}>
        <div class="case-title"><div><p class="case-kicker">{domain} · {escape(t['kind'])} · {escape(origin)}</p>
          <h3>{escape(t['title'])}</h3><p>{escape(LINES[t['id']])}</p></div>
          <span class="case-id">{t['id']}</span>
        </div>
        {rewritten}
        <p class="ma-sub">What only each seat knows or holds at the start</p>
        <div class="ma-seatcards n{len(t['seats'])}">{''.join(seats)}</div>
        {world}
        <div class="ma-why">
          <div><p class="ma-sub">What has to pass between seats</p><ul>{''.join(f'<li>{escape(x)}</li>' for x in t['relies_on'])}</ul></div>
          <div><p class="ma-sub">Why another seat has to decide</p><ul>{''.join(f'<li>{escape(x)}</li>' for x in t['others_decide'])}</ul></div>
        </div>
        <div class="case-trap"><span class="trap-icon">{icon("alert")}</span>
          <div><p class="trap-label">Ways it fails</p><p>{escape(' · '.join(t['failure_modes']))}</p></div></div>
        <div class="ma-admit">
          <p class="ma-sub">Admitted, by playing the scripts</p>
          <ul>
            <li>{'Solved' if solved else 'Not solved'} under all {len(a['witnesses'])} seatings it declares: conditions {', '.join(t['conditions'])}, focal {', '.join(labels[s] for s in t['focal_options'])}</li>
            <li>If any one of these seats does nothing, the joint result fails: {escape(needed)}</li>
            {careless}
            <li>{len(a['bypass'])} calls around the rules, each refused by the world</li>
          </ul>
        </div>
        <div class="case-footer">
          <p>Every seat is judged by its own role. Task fingerprint <code>{t['task_sha256'][:12]}</code>.</p>
          <a class="scenario-text-button" href="{CODE}{t['sheet']}" target="_blank" rel="noopener">Read the full task sheet {icon("arrow")}</a>
        </div>
      </article>"""


def provenance(domains):
    rows, notes = [], []
    for key, data in domains.items():
        title = DOMAIN[key][0]
        by_new = {t["id"]: t for t in data["tasks"]}
        kept = [old for old, new in data["rewritten_from"].items() if not by_new[new]["rewritten"]]
        rewritten = [old for old, new in data["rewritten_from"].items() if by_new[new]["rewritten"]]
        folded = [old for old, why in data["left_out"].items() if "condition C of" in why or "focal seat of" in why]
        left = {old: why for old, why in data["left_out"].items() if old not in folded}
        rows.append(f'<tr><th scope="row">{title}</th><td>{len(kept)}</td><td>{len(rewritten)}</td><td>{len(folded)}</td><td>{len(left)}</td></tr>')
        reasons = "".join(f"<li><code>{escape(old)}</code> {escape(why)}</li>" for old, why in data["left_out"].items())
        notes.append(f'<details class="ma-left"><summary>{title}: what was folded in or left out, and why</summary><ul>{reasons}</ul></details>')
    return f"""<div class="ma-table"><table>
        <thead><tr><th scope="col">Scenario</th><th scope="col">Kept</th><th scope="col">Rewritten</th>
        <th scope="col">Folded in</th><th scope="col">Left out</th></tr></thead>
        <tbody>{''.join(rows)}</tbody></table></div>
      <p class="ma-tablenote">Counted in tasks, except for left out, which counts entries: one entry can stand for a family of tasks, such as all generated ones.</p>
      <div class="ma-lefts">{''.join(notes)}</div>"""


def render(ma):
    domains = ma["domains"]
    tasks = [t for d in domains.values() for t in d["tasks"]]
    first = tasks[0]["id"]
    n_tk, n_ic = (len(domains[k]["tasks"]) for k in ("ticketing", "insurance"))
    seatings = sum(len(t["admission"]["witnesses"]) for t in tasks)
    panels = "\n".join(task_panel(t, t["id"] == first) for t in tasks)
    checks = [
        "solved by scripts under every seating it declares",
        "at least two seats have to act",
        "every seat that can be focal has work of its own",
        "each counterfactual breaks the joint result or costs a seat money",
        "every call around the rules is refused by the world",
        "no card holds another seat's private facts",
    ]
    admit = "".join(f'<li>{icon("shield")}<span>{escape(c)}</span></li>' for c in checks)
    return f"""
  <div class="scenario-hero">
    <div class="wrap">
      <div class="scenario-hero-grid">
        <div class="scenario-hero-copy">
          <span class="scenario-hero-icon">{icon("exchange")}</span>
          <h1>No seat can finish alone</h1>
          <p>Fifteen tasks across ticketing and claims. Each seat acts for its own principal, knows facts the others do not and has powers the others lack. The same task runs with the model under test in one seat or in every seat; only who drives the other seats changes.</p>
          <a class="scenario-cta" href="#multiagent/cases">See the fifteen tasks {icon("arrow")}</a>
        </div>
        <figure class="role-map ma-admitbox">
          <figcaption>A task enters the set only if</figcaption>
          <ul>{admit}</ul>
          <p class="role-base">{icon("file")}Each test is played and recorded with the task</p>
        </figure>
      </div>
      <dl class="scenario-facts"><div><dt>Tasks</dt><dd>{n_tk + n_ic}</dd></div><div><dt>Ticketing · claims</dt><dd>{n_tk} · {n_ic}</dd></div>
        <div><dt>Seatings solved by scripts</dt><dd>{seatings}</dd></div></dl>
    </div>
  </div>
  <section class="scenario-section">
    <div class="wrap">
      <div class="cases-head">
        <h2>One task, three ways to seat it</h2>
        <p>The world, the private facts, the goals, the rules and the events are the same in every condition. Only who drives each seat changes, and the one section of each card that describes the other seats. Shown here with the booking agent as the seat under test; a task can offer a traveller, a driver or an adjuster instead.</p>
      </div>
      {condition_cards()}
    </div>
  </section>
  <section class="scenario-section">
    <div class="wrap">
      <div class="cases-head">
        <h2>Every seat is judged by its own role</h2>
        <p>The same contract whoever drives the seat: a model, a script or a reference model. Each requirement is marked as up to the seat or shared with others, so that a seat is not blamed for what only another seat could do.</p>
      </div>
      <div class="ma-roles">{role_cards()}</div>
      <div class="ma-rules">
        <p><b>Joint result</b> every seat meets every requirement. The lawful solution of each task shows that they can.</p>
        <p><b>Losses are never added</b> an insurer that paid less may be a driver who was not paid.</p>
        <p><b>Regret</b> a seat's loss above its loss when every seat is played by its script: a fixed point of comparison, not the best possible play.</p>
      </div>
    </div>
  </section>
  <section class="scenario-section scenario-cases" id="multiagent-cases">
    <div class="wrap">
      <div class="cases-head">
        <h2>The fifteen tasks</h2>
        <p>Pick a task to see who holds what, what has to pass between the seats, why a seat other than the one under test has to decide, and how it fails.</p>
      </div>
      {picker(domains, first)}
{panels}
    </div>
  </section>
  <section class="scenario-section">
    <div class="wrap">
      <div class="cases-head">
        <h2>Where the tasks came from</h2>
        <p>Every hand-built development task was checked against the standard above. The development sets and their results stay as they were, and are never reported beside this set.</p>
      </div>
      {provenance(domains)}
    </div>
  </section>
  <section class="scenario-section scenario-reference">
    <div class="wrap">
      <h2>What is verified so far</h2>
      <div class="scenario-scoring">
        <div class="score-card"><span class="scenario-icon">{icon("shield")}</span><h3>The protocol: tested</h3><p>Seatings and their refusals, scripts confined to their own seat, every seat's ending charged to the right seat, the same end played in one process and over the network.</p></div>
        <div class="score-card"><span class="scenario-icon">{icon("file")}</span><h3>The tasks: admitted</h3><p>All fifteen pass every test above when the scripts play them. The evidence is stored with the tasks and replayed by one command.</p></div>
        <div class="score-card"><span class="scenario-icon">{icon("chart")}</span><h3>Models: first trials</h3><p>First trials with a model are under way. No results are reported here yet.</p></div>
      </div>
    </div>
  </section>""".strip()
