"""Build the presentation sections from the site's exported task and interface data."""
from datetime import datetime
from html import escape


ICONS = {
    "plane": '<path d="M17 21v-8l-4-4V4a1 1 0 0 0-2 0v5l-4 4v8l5-3 5 3z"/><path d="M3 18l4-2m10 0 4 2"/>',
    "car": '<path d="m5 11 2-5h10l2 5m-15 7v2m16-2v2M4 11h16l1 2v5H3v-5l1-2zM7 15h2m6 0h2"/>',
    "person": '<circle cx="12" cy="7.5" r="3.25"/><path d="M5.5 20v-2a6.5 6.5 0 0 1 13 0v2"/>',
    "desk": '<rect x="3" y="5" width="18" height="12" rx="2"/><path d="M8 21h8m-4-4v4M8 11h8"/>',
    "message": '<path d="M21 15a2 2 0 0 1-2 2H9l-5 4v-4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h15a2 2 0 0 1 2 2zM6 9h11M6 13h7"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6"/><path d="m15 15 5 5"/>',
    "lock": '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 4v3"/>',
    "ticket": '<path d="M3 7h18v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4zM15 7v2m0 2v2m0 2v2"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/>',
    "chart": '<path d="M4 4v16h16M8 16v-3m4 3V9m4 7v-5m4 5V6"/>',
    "file": '<path d="M5 3h9l5 5v13H5zM14 3v5h5M8 12h8m-8 4h8"/>',
    "shield": '<path d="m12 3 7 3v5c0 4.6-3 7.8-7 10-4-2.2-7-5.4-7-10V6z"/><path d="m9 12 2 2 4-4"/>',
    "money": '<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.1m11.9 0h.1"/>',
    "exchange": '<path d="M3 8h17m-4-4 4 4-4 4M21 16H4m4-4-4 4 4 4"/>',
    "split": '<path d="M5 12h5m0 0 6-6h5m-4-3 4 3-4 3m-7 3 6 6h5m-4-3 4 3-4 3"/><circle cx="4" cy="12" r="1.5"/>',
    "scale": '<path d="M12 4v16m-4 0h8M5 7h14M5 7l-3 7h6L5 7Zm14 0-3 7h6l-3-7Z"/>',
    "alert": '<path d="M12 3 2.5 20h19zM12 9v5m0 3h.01"/>',
    "arrow": '<path d="M4 12h15m-6-6 6 6-6 6"/>',
    "down": '<path d="M12 4v15m-6-6 6 6 6-6"/>',
}

SCENARIOS = {
    "ticketing": {
        "title": "Flight ticketing",
        "intro": "A booking agent serves two travellers with separate goals, budgets and consent. Airline events can change the plan before the work is done.",
        "workflow_title": "From request to confirmed ticket",
        "steps": [
            ("message", "Learn each traveller’s needs", "Ask about arrival times, budget and preferences."),
            ("search", "Find a plan that fits", "Check availability, fares and what the airline allows."),
            ("lock", "Get the right consent", "Bind each traveller’s approval to the action and amount."),
            ("ticket", "Execute and verify", "Book, change or refund. Check the resulting orders and payments."),
        ],
        "cases": [
            {
                "id": "tk-t5-02",
                "ticket_seat": "traveler_a",
                "tab": "Flight cancelled",
                "title": "One cancellation, two different outcomes",
                "intro": "Maya still needs to fly. Daniel wants his money back. They start on one shared order.",
                "spine": [
                    ("alert", "Airline cancels AJ360", "Both reservations are disrupted."),
                    ("search", "Check the airline’s options", "Find the free rebooking and full-refund paths."),
                    ("split", "Split the shared order", "Handle each passenger separately and obtain any required approval."),
                ],
                "branches": [
                    ("plane", "Maya · free rebooking", "Find a flight that meets her arrival deadline."),
                    ("money", "Daniel · full refund", "Return the fare and bag fee to the original payment method."),
                ],
                "lesson": "Daniel will also approve the smaller ordinary refund. In the scripted comparison, that route adds $181.50 in traveller loss.",
            },
            {
                "id": "tk-t10-02",
                "tab": "A shared bill",
                "title": "Two travellers, one scarce fare",
                "intro": "Daniel cannot afford a suitable ticket alone. Maya can contribute, but takes 45 minutes to reply.",
                "spine": [
                    ("search", "Find the scarce seat", "Only one seat is available at the low fare."),
                    ("message", "Ask who can pay", "Confirm Maya’s willingness and propose each payer’s share."),
                    ("clock", "Refresh the offer", "The 20-minute quote can expire before Maya answers. Check price and consent again."),
                ],
                "branches": [
                    ("ticket", "Book separately", "Use the low fare and budget for an extra reply."),
                    ("exchange", "Book together", "Use one proposal to save a reply, at a higher fare."),
                ],
                "lesson": "Both routes can succeed. The task tests whether the agent can trade off price, reply time and valid consent.",
            },
        ],
        "checks": [
            ("ticket", "Both goals met", "Each traveller ends with the outcome they asked for, within budget."),
            ("lock", "Permission respected", "Charges and changes follow the consent rules enforced by the service."),
            ("chart", "Cost against a reference", "Successful plans can differ in cash, travel credit and itinerary quality."),
        ],
    },
    "insurance": {
        "title": "Auto-insurance claims",
        "intro": "Two drivers and two insurers work through one collision. Each desk has its own file, and every payout changes what someone else is still owed.",
        "workflow_title": "From accident report to settlement",
        "steps": [
            ("file", "Open the claim", "Drivers report the loss. Each insurer checks its policy."),
            ("search", "Gather evidence", "Collect statements and reports, then appraise damage and record fault."),
            ("money", "Pay what is owed", "Apply coverage, deductibles and limits to the repair and rental bills."),
            ("exchange", "Recover and reconcile", "Settle between insurers, or send the dispute to arbitration."),
        ],
        "cases": [
            {
                "id": "ic-c5-02",
                "tab": "A shared policy limit",
                "title": "Two claims on a $15,000 limit",
                "intro": "Driver B’s insurer has already paid under its own policy. Driver B still has a rental gap, and that insurer seeks recovery.",
                "spine": [
                    ("car", "Recognize both claims", "Driver B and their insurer seek payment from Insurer A."),
                    ("file", "Reconcile the rental bill", "Check what B’s policy already covered. The remaining gap is $125."),
                    ("scale", "Allocate the limit", "Apply the scenario’s driver-first rule and send the excess notice."),
                ],
                "branches": [
                    ("person", "$125 to Driver B", "Cover the unpaid portion of the rental bill."),
                    ("exchange", "$14,875 to Insurer B", "Use the remaining limit for its recovery claim."),
                ],
                "lesson": "The case tests who gets paid, for what, and in which order when the cap cannot cover both claims in full.",
            },
            {
                "id": "ic-c2-02",
                "tab": "Disputed fault",
                "title": "An insurer offers only half",
                "intro": "Both drivers say they had a green light. One holds a recording, and a witness can confirm what happened.",
                "spine": [
                    ("search", "Assemble the evidence", "Get the recording and witness statement before deciding fault."),
                    ("money", "Pay and seek recovery", "Pay the insured, then send the other desk a documented demand."),
                    ("message", "Review the counteroffer", "The other insurer offers half. The evidence supports more."),
                ],
                "branches": [
                    ("scale", "File for arbitration", "Submit the evidence so the forum can award the full supported amount."),
                    ("alert", "Accept the counteroffer", "Close the dispute with a shortfall in recovery."),
                ],
                "lesson": "The forum considers evidence filed with it. What the adjuster already knows must still be put on record.",
            },
        ],
        "checks": [
            ("money", "Correct payments", "Check what each driver and insurer received, by claim and amount."),
            ("clock", "Decisions and deadlines", "Inspect evidence gathering, appraisal, notices and payment timing."),
            ("chart", "Loss by seat", "Compare overpayment, unpaid amounts and missed recovery with a scripted reference."),
        ],
    },
}


def icon(name):
    return ('<svg class="s-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{ICONS[name]}</svg>')


def tile(symbol, title, detail, cls, heading="h3"):
    return (f'<div class="{cls}"><span class="scenario-icon">{icon(symbol)}</span>'
            f'<{heading}>{escape(title)}</{heading}><p>{escape(detail)}</p></div>')


def roles(view):
    def actor(symbol, name, detail):
        return (f'<div class="role-actor">{icon(symbol)}<div><strong>{name}</strong>'
                f'<small>{detail}</small></div></div>')

    if view == "ticketing":
        return (f'<div class="role-pair">{actor("person", "Maya", "Goals · budget · consent")}'
                f'{actor("person", "Daniel", "Goals · budget · consent")}</div>'
                '<div class="role-join"><span></span><span></span></div>'
                f'<div class="role-center">{actor("desk", "Booking agent", "Searches and acts for both")}</div>'
                f'<p class="role-base">{icon("plane")}Booking service · inventory, fares and orders</p>')
    return (f'<div class="role-pair">{actor("person", "Driver A", "Reports own loss")}'
            f'{actor("person", "Driver B", "Reports own loss")}</div>'
            f'<div class="role-pair role-connect"><span>{icon("down")} Own policy</span>'
            f'<span>{icon("down")} Own policy</span></div>'
            f'<div class="role-pair">{actor("shield", "Insurer A", "Coverage · liability")}'
            f'{actor("shield", "Insurer B", "Coverage · liability")}</div>'
            f'<p class="role-base">{icon("exchange")}Direct claims and insurer-to-insurer recovery</p>')


def boarding_pass(ticket, title):
    def local_time(value):
        time = datetime.fromisoformat(value)
        return f'<time datetime="{escape(value)}">{time.day} {time:%b} · {time:%H:%M}</time>'

    return f"""<div class="case-node case-branch case-boarding stub live">
      <div class="stub-main">
        <h4>{escape(title)}</h4>
        <p class="stub-title">{escape(ticket["from"])} <span class="to" aria-hidden="true"></span> {escape(ticket["to"])}</p>
        <dl>
          <div><dt>Departs</dt><dd>{local_time(ticket["departs"])}</dd></div>
          <div><dt>Arrives</dt><dd>{local_time(ticket["arrives"])}</dd></div>
        </dl>
      </div>
      <div class="stub-side"><p class="lbl">Flight</p><p class="state">{escape(ticket["flight"])}</p></div>
    </div>"""


def case_panel(case, active, tickets):
    case_id = case["id"]
    spine = ''.join(tile(*node, "case-node", "h4") for node in case["spine"])
    branches = [tile(*node, "case-node case-branch", "h4") for node in case["branches"]]
    if "ticket_seat" in case:
        # The after-sales demo shares the rebooked flight with the task's reference run.
        branches[0] = boarding_pass(tickets[case["ticket_seat"]], case["branches"][0][1])
    return f"""      <article class="case-panel" id="case-{case_id}" data-case-panel="{case_id}"{' hidden' if not active else ''}>
        <div class="case-title"><div><h3>{escape(case["title"])}</h3><p>{escape(case["intro"])}</p></div>
          <span class="case-id">{case_id}</span>
        </div>
        <div class="case-flow" aria-label="Task flow in order, with two paths at the end">
          {spine}
          <div class="case-branches">{''.join(branches)}</div>
        </div>
        <div class="case-footer">
          <p>{escape(case["lesson"])}</p>
          <button class="scenario-text-button" type="button" data-open-task="{case_id}">Open task record {icon("arrow")}</button>
        </div>
      </article>"""


def render(view, catalog, interface, recorded_tickets=()):
    data = SCENARIOS[view]
    known = {task["task_id"] for task in catalog["tasks"]}
    assert all(case["id"] in known for case in data["cases"]), view
    count = len(known) + len(catalog.get("generated", ()))
    action_count = len(interface["actions"])
    stats = ([("Public dev tasks", count), ("Held-out tasks", catalog["heldout"]["count"]), ("Scenario actions", action_count)]
             if view == "ticketing" else [("Public dev tasks", count), ("Seats in the world", len(catalog["seats"])),
                                         ("Scenario actions", action_count)])
    facts = ''.join(f'<div><dt>{label}</dt><dd>{value}</dd></div>' for label, value in stats)
    steps = ''.join(f'<li>{tile(*step, "journey-card")}</li>' for step in data["steps"])
    checks = ''.join(tile(*check, "score-card") for check in data["checks"])
    buttons = ''.join(f'<button type="button" data-case="{case["id"]}" aria-controls="case-{case["id"]}" '
                      f'aria-pressed="{str(idx == 0).lower()}">{escape(case["tab"])}</button>'
                      for idx, case in enumerate(data["cases"]))
    tickets = {ticket["seat_name"]: ticket for ticket in recorded_tickets}
    panels = '\n'.join(case_panel(case, idx == 0, tickets) for idx, case in enumerate(data["cases"]))
    return f"""
  <div class="scenario-hero">
    <div class="wrap">
      <div class="scenario-hero-grid">
        <div class="scenario-hero-copy">
          <span class="scenario-hero-icon">{icon("plane" if view == "ticketing" else "car")}</span>
          <h1>{escape(data["title"])}</h1>
          <p>{escape(data["intro"])}</p>
          <a class="scenario-cta" href="#{view}/cases">Walk through a task {icon("arrow")}</a>
        </div>
        <figure class="role-map">
          <figcaption>Who takes part</figcaption>
          {roles(view)}
        </figure>
      </div>
      <dl class="scenario-facts">{facts}</dl>
    </div>
  </div>
  <section class="scenario-section">
    <div class="wrap">
      <h2>{escape(data["workflow_title"])}</h2>
      <ol class="scenario-journey">{steps}</ol>
    </div>
  </section>
  <section class="scenario-section scenario-cases" id="{view}-cases">
    <div class="wrap">
      <div class="cases-head">
        <h2>Task walkthroughs</h2>
        <div class="case-controls" role="group" aria-label="Choose a task">{buttons}</div>
      </div>
{panels}
    </div>
  </section>
  <section class="scenario-section">
    <div class="wrap">
      <h2>What the benchmark checks</h2>
      <div class="scenario-scoring">{checks}</div>
    </div>
  </section>""".strip()
