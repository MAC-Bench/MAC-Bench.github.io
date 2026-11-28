"""Render the Shopping overview, scenarios and reference data."""
import json
from html import escape

from .scenarios import render as render_scenario
from .scenarios import render_overview, tile


def money(cents):
    return f"${cents / 100:,.2f}"


def task_row(task):
    ident = escape(task["task_id"])
    reference = task["reference"]
    careless = task["careless_agent"]
    outcome = (f'Succeeds with {money(careless["regret_cents"])} regret' if careless["success"]
               else f'Fails “{escape(", ".join(careless["failed"]))}”')
    return f"""<tr>
      <td><button type="button" class="scenario-text-button" data-open-task="{ident}"
                  aria-controls="shopping-record-{ident}">{ident}</button></td>
      <td>{escape(task["title"])}</td>
      <td>{escape(task["source"].capitalize())}</td>
      <td>{money(reference["loss_cents"])}</td>
      <td>{reference["calls"]}</td>
      <td>{outcome}</td>
    </tr>"""


def merchant_settings(task, merchants):
    offers = []
    for offer in task["opening_offers"]:
        variant = escape(offer["product"])
        if offer["value"] != "standard":
            variant += f' · {escape(offer["value"])}'
        if offer["substitute"]:
            variant += " (substitute)"
        offers.append(f"""<tr>
          <td>{variant}<br><code>{escape(offer["variant_id"])}</code></td>
          <td>{escape(merchants[offer["merchant"]])}</td>
          <td>{offer["stock"]}</td><td>{money(offer["price_cents"])}</td><td>{offer["delivery_days"]}</td>
        </tr>""")
    policies = []
    for merchant, policy in task["merchant_policies"].items():
        shipping = money(policy["shipping_fee_cents"])
        if policy["free_shipping_threshold_cents"] is not None:
            shipping += f' · free from {money(policy["free_shipping_threshold_cents"])}'
        discount = "—"
        if policy["discount_cents"] is not None:
            discount = f'{money(policy["discount_cents"])} off from {money(policy["discount_threshold_cents"])}'
        refund = "Original payment" if policy["refund_to"] == "original_payment" else "Store credit"
        reservation = f'{policy["reservation_minutes"]} min' if policy["reservation_minutes"] is not None else "—"
        policies.append(f"""<tr>
          <td>{escape(merchants[merchant])}</td><td>{shipping}</td><td>{discount}</td>
          <td>{refund} · {policy["return_window_days"]} days</td><td>{reservation}</td>
        </tr>""")
    return f"""<details class="tcard">
      <summary>Initial stock, prices and merchant policies</summary>
      <div class="stack">
        <h5>Wanted variants and substitutes at the start</h5>
        <div class="tscroll"><table class="ft shopping-settings">
          <thead><tr><th scope="col">Variant</th><th scope="col">Merchant</th><th scope="col">In stock</th><th scope="col">Unit price</th><th scope="col">Delivery days</th></tr></thead>
          <tbody>{"".join(offers)}</tbody>
        </table></div>
        <h5>Policies in this task</h5>
        <div class="tscroll"><table class="ft shopping-settings">
          <thead><tr><th scope="col">Merchant</th><th scope="col">Shipping</th><th scope="col">Order discount</th><th scope="col">Refund and window</th><th scope="col">Reservation</th></tr></thead>
          <tbody>{"".join(policies)}</tbody>
        </table></div>
      </div>
    </details>"""


def market_schedule(events, merchants):
    if not events:
        return ""
    rows = []
    for event in events:
        item = f'{event["quantity"]} units of <code>{escape(event["variant_id"])}</code>'
        action = f"Other shoppers try to buy {item} from unreserved stock" if event["kind"] == "demand" else f"The merchant adds {item}"
        rows.append(f'<li>Minute {event["at_minutes"]} · {escape(merchants[event["merchant"]])} · {action}.</li>')
    return f'\n      <div class="stack"><h5>Scheduled market events</h5><ul class="plain-list">{"".join(rows)}</ul></div>'


def task_record(task, merchants):
    ident = escape(task["task_id"])
    facts = task["facts"]
    labels = {
        "items": "Items", "accepts_substitute": "Substitutes", "budget_cents": "Budget",
        "needed_by": "Needed by", "may_return": "May return", "payment_method_id": "Payment methods",
        "credit_value_percent": "Store credit value",
    }
    values = dict(facts)
    if "budget_cents" in values:
        values["budget_cents"] = money(values["budget_cents"])
    if "credit_value_percent" in values:
        values["credit_value_percent"] = f'{values["credit_value_percent"]}%'
    if "may_return" in values:
        values["may_return"] = "Yes" if values["may_return"] else "No"
    details = "".join(f'<dt>{label}</dt><dd>{escape(str(values[key]))}</dd>'
                      for key, label in labels.items() if key in values)
    reference = task["reference"]
    slower = task["slower_reference"]
    slower_note = (f'\n      <p class="note">A reference that waits {slower["pause_minutes"]} extra minutes after learning the facts '
                   f'also succeeds, with {money(slower["regret_cents"])} regret.</p>' if slower and slower["success"] else "")
    leaving = "succeeds" if task["leaving_succeeds"] else "fails"
    start = escape(task["world_now"])
    cards = "".join(f'<details class="tcard"><summary>{escape(seat)} role card</summary>'
                    f'<pre class="json">{escape(card)}</pre></details>' for seat, card in task["cards"].items())
    return f"""<article class="stack shopping-task-record" id="shopping-record-{ident}" data-shopping-record hidden>
      <p class="note">{ident} · {escape(task["variant"])} · task fingerprint <code>{escape(task["digest"][:16])}</code></p>
      <h4 tabindex="-1">{escape(task["title"])}</h4>
      <div class="two-col">
        <div class="stack">
          <p><strong>Agent brief.</strong> {escape(task["brief"])}</p>
          <p><strong>What it tests.</strong> {escape(task["tests"])}</p>
          <p class="note">Starts <time datetime="{start}">{start[:10]} at {start[11:16]} UTC</time> · {task["observation_minutes"]}-minute episode · {task["delay_minutes"]}-minute shopper reply delay</p>
        </div>
        <div class="stack">
          <p class="lbl">Shopper’s private facts</p>
          <dl class="kv">{details}</dl>
        </div>
      </div>{market_schedule(task["events"], merchants)}
      {merchant_settings(task, merchants)}
      {cards}
      <div class="stack">
        <h5>Recorded runs</h5>
        <details class="box" data-shopping-run="reference" data-shopping-task="{ident}">
          <summary>Reference run · {reference["calls"]} agent calls</summary>
          <div class="stack shopping-run"></div>
        </details>
        <details class="box" data-shopping-run="careless" data-shopping-task="{ident}">
          <summary>Careless agent run · “{escape(task["careless_agent"]["name"])}”</summary>
          <div class="stack shopping-run"></div>
        </details>
      </div>
      <p class="note">Leaving at once {leaving}.</p>{slower_note}
    </article>"""


def action_rows(actions):
    rows = []
    group = None
    for action in actions:
        if action["group"] != group:
            group = action["group"]
            rows.append(f'<tr class="grp"><th colspan="4">{escape(group)}</th></tr>')
        roles = ", ".join("Agent" if role == "shopping_agent" else "Shopper" for role in action["roles"])
        cost = f'{action["time_cost_s"]} s'
        if action["wait_field"]:
            cost += " + wait"
        errors = escape(", ".join(action["errors"])) or "—"
        rows.append(f'<tr><td>{escape(action["name"])}</td><td>{roles}</td><td>{cost}</td><td class="errs">{errors}</td></tr>')
    return "\n".join(rows)


def example_block(name, example):
    request = escape(json.dumps(example["request"], indent=2, ensure_ascii=False))
    result = escape(json.dumps(example["response"], indent=2, ensure_ascii=False))
    return f"""<details class="box">
      <summary><code>{escape(name)}</code></summary>
      <div class="two-col">
        <div class="stack"><h4>Request</h4><pre class="json">{request}</pre></div>
        <div class="stack"><h4>Response</h4><pre class="json">{result}</pre></div>
      </div>
    </details>"""


def after_sales_outcome(outcome):
    returned = outcome["returned"]
    exchanged = outcome["exchanged"]
    refunds = " and ".join(
        f'{money(refund["amount_cents"])} to {"store credit" if refund["method"] == "store_credit" else "the card"}'
        for refund in returned["payments"]
    )
    delivered = escape(outcome["delivered_at"])
    window_end = escape(outcome["window_end"])
    return f"""<div class="stack">
      <p>Order <code>{escape(outcome["order_id"])}</code> came from {escape(outcome["merchant"])} with two brick lipsticks
        and a black desk lamp, with a {money(outcome["discount_cents"])} order discount. It was delivered on <time datetime="{delivered}">{delivered[:10]}</time>.
        The original lines’ return window closes on <time datetime="{window_end}">{window_end[:10]} at {window_end[11:16]} UTC</time>.</p>
      <div class="two-col">
        <div class="gcell">
          <h4>Return one lipstick · {money(returned["settled_cents"])} refunded</h4>
          <p>Its net price after the order discount was {money(returned["net_cents"])}.
            Return shipping takes {money(returned["return_shipping_cents"])}. Inspection finds the lipstick unopened
            and sends {refunds}.</p>
        </div>
        <div class="gcell">
          <h4>Exchange the black lamp for white</h4>
          <p>Confirmation holds one white lamp at an exchange fee of {money(exchanged["fee_cents"])}.
            Inspection sends it as unit <code>{escape(exchanged["new_unit_id"])}</code>, due {escape(exchanged["arrives_on"])}.</p>
        </div>
      </div>
    </div>"""


def render(template, data, after_sales):
    catalogue = data["catalogue"]
    timing = data["after_sales"]
    steps = [
        ("file", "Read the delivered order", "Ask which units to handle, their condition and reason, and the desired replacement or fallback."),
        ("money", "Quote each case", f'Check the return window, fees and stock. A quote lives up to {timing["quote_minutes"]} minutes.'),
        ("lock", "Get consent and confirm", "The shopper authorizes the exact quote. Confirmation holds any replacement stock and charges the exchange fee."),
        ("exchange", "Follow the inspection", f'After {timing["inspection_minutes"]} minutes the merchant checks the item and settles the refund or ships the replacement.'),
    ]
    sections = {
        "OVERVIEW": render_overview("shopping", data, data),
        "PURCHASE": render_scenario("shopping", data, data, include_overview=False),
        "AFTER_STEPS": "".join(f'<li>{tile(*step, "journey-card")}</li>' for step in steps),
        "AFTER_OUTCOME": after_sales_outcome(after_sales["outcome"]),
        "TASK_ROWS": "\n".join(task_row(task) for task in data["tasks"]),
        "TASK_RECORDS": "\n".join(task_record(task, catalogue["merchants"]) for task in data["tasks"]),
        "CATALOGUE": (f'{catalogue["products"]} products in {catalogue["categories"]} categories, '
                      f'{catalogue["listings"]} merchant listings and {catalogue["variants"]} variants'),
        "INTERFACE": escape(data["interface"]),
        "ACTION_ROWS": action_rows(data["actions"]),
        "EXAMPLES": "\n".join(example_block(name, example) for name, example in data["examples"].items()),
    }
    for name, content in sections.items():
        marker = f"<!--SHOPPING_{name}-->"
        assert marker in template, marker
        template = template.replace(marker, content)
    return template
