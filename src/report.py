"""The report-style pages: the report itself (the home page), the Tasks page, and the head of each task's page.

Modelled on the layout of research benchmark reports: a title and one-line lead over an illustration, a results figure, a table of
contents, then the design, the evaluation, the experimental setup and the results, each a short section. What is not built yet is
said to be not built yet, in a placeholder, never filled with invented numbers.

Every number about a task comes from data/ma2.json (written by the code repository's tools/export_ma2.py). The claims task of this
set is designed and not yet built: its numbers are those of the design, and its block says so.
"""
from __future__ import annotations

from html import escape

from src.multiagent import condition_cards, role_cards
from src.scenarios import icon

CODE = "https://github.com/MAC-Bench/MAC-benchmark"
SITE = "https://github.com/MAC-Bench/MAC-Bench.github.io"


def money(cents: int) -> str:
    return f"${cents / 100:,.2f}"


def svg(viewbox: str, label: str, body: str, cls: str = "") -> str:
    return (f'<svg class="art {cls}" viewBox="{viewbox}" role="img" aria-label="{escape(label)}" '
            f'xmlns="http://www.w3.org/2000/svg">{body}</svg>')


# --- drawing pieces ----------------------------------------------------------------------------------------------------------

def person(x: float, y: float, tone: str, bag: str = "") -> str:
    """A standing figure whose feet are at (x, y)."""
    out = (f'<rect class="ar-{tone}" x="{x - 11}" y="{y - 42}" width="22" height="30" rx="9"/>'
           f'<rect class="ar-{tone}" x="{x - 8}" y="{y - 14}" width="6" height="14" rx="3"/>'
           f'<rect class="ar-{tone}" x="{x + 2}" y="{y - 14}" width="6" height="14" rx="3"/>'
           f'<circle class="ar-face" cx="{x}" cy="{y - 52}" r="10"/>')
    if bag == "case":
        out += (f'<rect class="ar-paper ar-edge" x="{x + 13}" y="{y - 22}" width="15" height="20" rx="3"/>'
                f'<path class="ar-edge" d="M{x + 17} {y - 22}v-4h7v4" fill="none"/>')
    if bag == "shop":
        out += (f'<path class="ar-signal ar-edge" d="M{x + 12} {y - 30}h16l-2 18h-12z"/>'
                f'<path class="ar-edge" d="M{x + 16} {y - 30}a4 4 0 0 1 8 0" fill="none"/>')
    return out


def robot(x: float, y: float, tone: str, scale: float = 1.0) -> str:
    """An agent's head and shoulders, centred on (x, y)."""
    s = scale
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<line class="ar-edge" x1="0" y1="-24" x2="0" y2="-32"/><circle class="ar-signal" cx="0" cy="-34" r="3.5"/>'
            f'<rect class="ar-{tone}" x="-17" y="-24" width="34" height="27" rx="9"/>'
            f'<circle class="ar-paper" cx="-7" cy="-11" r="4"/><circle class="ar-paper" cx="7" cy="-11" r="4"/>'
            f'<rect class="ar-paper" x="-6" y="-3" width="12" height="2.5" rx="1.2"/>'
            f'<rect class="ar-{tone}" x="-13" y="5" width="26" height="14" rx="6"/></g>')


def bubble(x: float, y: float, glyph: str, tone: str = "paper") -> str:
    """A speech bubble with a small glyph: ticket, money, form, bag, check."""
    g = {"ticket": f'<rect class="ar-teal" x="{x - 9}" y="{y - 5}" width="18" height="10" rx="2"/><line class="ar-paper-s" x1="{x + 3}" y1="{y - 5}" x2="{x + 3}" y2="{y + 5}"/>',
         "money": f'<circle class="ar-signal ar-edge" cx="{x}" cy="{y}" r="6.5"/><text class="ar-glyph" x="{x}" y="{y + 3.5}">$</text>',
         "form": f'<rect class="ar-paper ar-edge" x="{x - 6}" y="{y - 8}" width="12" height="15" rx="1.5"/><line class="ar-edge" x1="{x - 3}" y1="{y - 3}" x2="{x + 3}" y2="{y - 3}"/><line class="ar-edge" x1="{x - 3}" y1="{y + 1}" x2="{x + 3}" y2="{y + 1}"/>',
         "bag": f'<path class="ar-amber" d="M{x - 6} {y - 4}h12l-1.5 10h-9z"/>',
         "check": f'<path class="ar-edge-strong" d="M{x - 5} {y}l3.5 3.5l6.5 -7" fill="none"/>',
         "clock": f'<circle class="ar-paper ar-edge" cx="{x}" cy="{y}" r="6.5"/><path class="ar-edge" d="M{x} {y - 4}v4h3" fill="none"/>'}[glyph]
    return (f'<g><rect class="ar-{tone} ar-edge" x="{x - 17}" y="{y - 13}" width="34" height="26" rx="9"/>'
            f'<path class="ar-{tone} ar-edge" d="M{x - 6} {y + 13}l-4 8l10 -8"/>{g}</g>')


def arc(x1: float, y1: float, x2: float, y2: float, lift: float = 40, cls: str = "ar-link") -> str:
    mx, my = (x1 + x2) / 2, min(y1, y2) - lift
    return f'<path class="{cls}" d="M{x1} {y1} Q{mx} {my} {x2} {y2}"/>'


def plane(x: float, y: float, tone: str, angle: float = -14, scale: float = 1.0) -> str:
    return (f'<g transform="translate({x} {y}) rotate({angle}) scale({scale})">'
            f'<path class="ar-{tone}" d="M-34 0c0-4 4-6 10-6h34c8 0 16 3 16 6s-8 6-16 6h-34c-6 0-10-2-10-6z"/>'
            f'<path class="ar-{tone}" d="M-6 -4l-12 -20h8l18 20zM-6 4l-12 20h8l18 -20zM-30 -3l-6 -12h6l8 12z"/>'
            f'<circle class="ar-paper" cx="14" cy="-1" r="2"/><circle class="ar-paper" cx="6" cy="-1" r="2"/><circle class="ar-paper" cx="-2" cy="-1" r="2"/></g>')


def car(x: float, y: float, tone: str, flip: bool = False) -> str:
    t = f'translate({x} {y}) scale({-1 if flip else 1} 1)'
    return (f'<g transform="{t}"><path class="ar-{tone}" d="M-42 -10q2 -14 14 -16l14 -12h30l16 14q12 2 14 14v10h-88z"/>'
            f'<path class="ar-paper" d="M-12 -34h12v10h-22zM4 -34h12l10 10h-22z" opacity=".85"/>'
            f'<circle class="ar-ink" cx="-24" cy="0" r="9"/><circle class="ar-paper" cx="-24" cy="0" r="3.5"/>'
            f'<circle class="ar-ink" cx="28" cy="0" r="9"/><circle class="ar-paper" cx="28" cy="0" r="3.5"/></g>')


def office(x: float, y: float, tone: str, w: float = 92, h: float = 98) -> str:
    """An insurer's office with a shield over the door, standing on (x, y)."""
    return (f'<rect class="ar-{tone}-t ar-edge" x="{x - w / 2}" y="{y - h}" width="{w}" height="{h}" rx="6"/>'
            f'<path class="ar-{tone}" d="M{x - w / 2 - 6} {y - h + 4}l{w / 2 + 6} -26l{w / 2 + 6} 26z"/>'
            f'<path class="ar-paper ar-edge" d="M{x} {y - h + 16}l13 5v9c0 8 -6 12 -13 15c-7 -3 -13 -7 -13 -15v-9z"/>'
            f'<path class="ar-edge-strong" d="M{x - 5} {y - h + 30}l3.5 3.5l6.5 -7" fill="none"/>'
            + "".join(f'<rect class="ar-paper ar-edge" x="{x - w / 2 + 12 + i * 26}" y="{y - 42}" width="16" height="14" rx="2"/>' for i in range(3))
            + f'<rect class="ar-{tone}" x="{x - 9}" y="{y - 24}" width="18" height="24" rx="3"/>')


def shop(x: float, y: float, w: float = 210, h: float = 112) -> str:
    stripes = "".join(f'<path class="{"ar-amber" if i % 2 == 0 else "ar-paper"} ar-edge" d="M{x + i * w / 7} {y - h}h{w / 7}v18'
                      f'a{w / 14} 8 0 0 1 -{w / 7} 0z"/>' for i in range(7))
    return (f'<rect class="ar-paper ar-edge" x="{x}" y="{y - h + 10}" width="{w}" height="{h - 10}" rx="6"/>{stripes}'
            f'<rect class="ar-amber-t ar-edge" x="{x + 14}" y="{y - 66}" width="{w * 0.48}" height="46" rx="4"/>'
            f'<rect class="ar-amber" x="{x + w - 54}" y="{y - 60}" width="34" height="60" rx="4"/>'
            f'<circle class="ar-paper" cx="{x + w - 26}" cy="{y - 30}" r="2.5"/>')


# --- the illustration on the home page ----------------------------------------------------------------------------------------

def hero_art() -> str:
    clouds = ('<g class="ar-cloud"><ellipse cx="150" cy="70" rx="38" ry="14"/><ellipse cx="178" cy="62" rx="26" ry="14"/>'
              '<ellipse cx="610" cy="54" rx="34" ry="12"/><ellipse cx="636" cy="48" rx="22" ry="12"/>'
              '<ellipse cx="980" cy="76" rx="40" ry="14"/><ellipse cx="1006" cy="68" rx="24" ry="13"/></g>')
    ground = '<path class="ar-ground" d="M0 336c180 -18 360 -18 560 -6s380 14 560 -4v94H0z"/>'
    # flights: a tower, a runway, a plane on its way, two travellers and the booking agent
    flights = ('<rect class="ar-teal-t ar-edge" x="56" y="214" width="26" height="118" rx="4"/>'
               '<rect class="ar-teal" x="44" y="190" width="50" height="28" rx="7"/><rect class="ar-paper" x="52" y="198" width="34" height="9" rx="3"/>'
               '<rect class="ar-runway" x="36" y="340" width="320" height="9" rx="4.5"/>'
               '<path class="ar-trail" d="M118 168q60 -14 120 -44"/>' + plane(268, 112, "teal")
               + person(132, 336, "indigo", "case") + person(192, 336, "amber", "case")
               + '<rect class="ar-paper ar-edge" x="250" y="292" width="96" height="44" rx="6"/>'
               + '<rect class="ar-ink-s" x="262" y="282" width="34" height="12" rx="2"/>'
               + robot(300, 268, "teal")
               + arc(146, 268, 284, 236, 50) + arc(206, 268, 290, 240, 26)
               + bubble(214, 196, "money") + bubble(320, 196, "ticket"))
    # claims: two cars that met, two insurers' offices, a claim form passing between them
    claims = (office(470, 330, "indigo") + office(712, 330, "indigo")
              + '<rect class="ar-runway" x="396" y="342" width="370" height="9" rx="4.5"/>'
              + car(548, 338, "teal") + car(646, 338, "amber", flip=True)
              + '<path class="ar-signal ar-edge" d="M597 302l6 10l10 -4l-4 10l10 6l-11 3l2 11l-9 -6l-7 9l-2 -11l-11 -1l9 -7l-5 -10l10 3z"/>'
              + robot(470, 172, "indigo", 0.9) + robot(712, 172, "indigo", 0.9)
              + arc(490, 162, 692, 162, 46) + bubble(591, 104, "form") + bubble(536, 230, "money", "paper"))
    # shopping: a shopper and their agent outside a merchant's shop
    shopping = (shop(846, 336, w=168) + robot(1040, 316, "indigo", 0.8)
                + person(1082, 336, "teal", "shop")
                + arc(1072, 270, 1042, 285, 20) + bubble(1004, 210, "bag") + bubble(952, 168, "check"))
    names = ('<text class="ar-scene" x="196" y="392">Flight ticketing</text><text class="ar-scene" x="581" y="392">Insurance claims</text>'
             '<text class="ar-scene" x="960" y="392">Online shopping</text>')
    return svg("0 0 1120 420", "Three everyday services: two travellers and a booking agent at an airport, two drivers' insurers "
               "passing a claim form after a minor collision, and a shopper with their agent outside a shop. Dashed arcs "
               "and speech bubbles show the agents talking to each other on behalf of different people.",
               '<rect class="ar-bg" width="1120" height="420" rx="22"/>' + clouds + ground + flights + claims + shopping + names, "hero-art")


# --- small diagrams for the task cards ----------------------------------------------------------------------------------------

def diagram_flights() -> str:
    nodes = {"SEA": (54, 40), "SFO": (40, 104), "LAX": (66, 150), "DEN": (146, 92), "ORD": (214, 58), "ATL": (222, 146),
             "BOS": (298, 34), "NYC": (284, 76)}
    edges = [("SEA", "DEN"), ("SFO", "DEN"), ("LAX", "DEN"), ("DEN", "ORD"), ("DEN", "ATL"), ("ORD", "BOS"), ("ATL", "NYC"),
             ("SEA", "ORD"), ("LAX", "ATL"), ("DEN", "NYC")]
    body = "".join(f'<line class="ar-net" x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}"/>' for a, b in edges)
    body += arc(40, 104, 280, 76, 46, "ar-route-a") + arc(214, 58, 282, 74, 16, "ar-route-b")
    body += '<circle class="ar-meet" cx="284" cy="76" r="13"/>'
    for code, (x, y) in nodes.items():
        hot = code in ("SFO", "ORD", "NYC")
        body += (f'<circle class="{"ar-ink" if hot else "ar-node"}" cx="{x}" cy="{y}" r="{5 if hot else 3.5}"/>'
                 f'<text class="ar-code{" hot" if hot else ""}" x="{x}" y="{y + (17 if y < 120 else -10)}">{code}</text>')
    body += plane(170, 40, "teal", -8, 0.42)
    return svg("0 0 320 180", "A flight network: two routes, San Francisco to New York and Chicago to New York, converge on New York.", body, "card-art")


def diagram_claims() -> str:
    body = (car(84, 160, "teal", False).replace("scale(1 1)", "scale(.62 .62)") + car(236, 160, "amber", True).replace("scale(-1 1)", "scale(-.62 .62)"))
    body += ('<path class="ar-signal ar-edge" d="M160 128l4 7l7 -3l-3 7l7 4l-8 2l1 8l-6 -4l-5 6l-1 -8l-8 -1l6 -5l-3 -7l7 2z"/>')
    for x in (84, 236):
        body += (f'<path class="ar-indigo-t ar-edge" d="M{x} 18l26 10v18c0 16 -12 24 -26 30c-14 -6 -26 -14 -26 -30v-18z"/>'
                 f'<path class="ar-edge-strong" d="M{x - 9} 44l6 6l12 -13" fill="none"/>')
    body += ('<path class="ar-flow" d="M84 132V84"/><path class="ar-flow" d="M236 132V84"/>'
             '<path class="ar-flow ar-dash" d="M104 136L216 80"/><path class="ar-flow-strong" d="M114 42h92"/>'
             '<text class="ar-code" x="160" y="34">recover</text><text class="ar-code" x="62" y="112">claim</text>'
             '<text class="ar-code" x="258" y="112">claim</text>')
    return svg("0 0 320 180", "Two drivers after a collision, each with an insurer: each claims, one may claim against the other's insurer, "
               "and the insurers recover from each other.", body, "card-art")


def diagram_shop() -> str:
    body = person(62, 150, "teal", "shop")
    for i, y in enumerate((36, 90, 144)):
        x = 250
        body += (f'<rect class="ar-paper ar-edge" x="{x - 34}" y="{y - 22}" width="68" height="40" rx="5"/>'
                 f'<path class="ar-amber" d="M{x - 34} {y - 22}h68v9h-68z"/>'
                 f'<rect class="ar-amber-t" x="{x - 26}" y="{y - 6}" width="24" height="16" rx="2"/>'
                 f'<path class="ar-flow" d="M{88} {108 - (1 - i) * 10}L{x - 40} {y}"/>')
    body += bubble(140, 52, "money") + bubble(150, 150, "bag")
    return svg("0 0 320 180", "One shopper and three merchants: the shopper's agent compares their offers.", body, "card-art")


# --- interaction structure of a task ----------------------------------------------------------------------------------------

def node(x: float, y: float, w: float, title: str, sub: str, tone: str, lines: list[str] = (), private: bool = True) -> str:
    h = 46 + (18 * len(lines) + 12 if lines else 0)
    out = (f'<rect class="ar-{tone}-t ar-edge" x="{x - w / 2}" y="{y}" width="{w}" height="{h}" rx="10"/>'
           f'<text class="tp-title" x="{x - w / 2 + 14}" y="{y + 22}">{escape(title)}</text>'
           f'<text class="tp-sub" x="{x - w / 2 + 14}" y="{y + 38}">{escape(sub)}</text>')
    if lines:
        out += f'<line class="ar-line" x1="{x - w / 2 + 12}" y1="{y + 46}" x2="{x + w / 2 - 12}" y2="{y + 46}"/>'
        if private:
            out += (f'<g transform="translate({x + w / 2 - 26} {y + 12})"><rect class="ar-ink" x="0" y="6" width="12" height="9" rx="2"/>'
                    f'<path class="ar-edge-strong" d="M2.5 6v-2.5a3.5 3.5 0 0 1 7 0v2.5" fill="none"/></g>')
        for i, line in enumerate(lines):
            out += f'<text class="tp-line" x="{x - w / 2 + 14}" y="{y + 64 + 18 * i}">{escape(line)}</text>'
    return out


def topology_ticketing(t: dict) -> str:
    a, b = t["seats"]["traveler_a"], t["seats"]["traveler_b"]
    maya = [f"red-eye costs {money(a['overnight_cost_cents'])}", f"each connection {money(a['stop_penalty_cents'])}",
            f"landing together worth {money(a['meet_value_cents'])}", f"alone: {money(t['outside']['traveler_a'])}"]
    dan = [f"leaving before noon {money(b['early_departure_cost_cents'])}", f"each connection {money(b['stop_penalty_cents'])}",
           f"landing together worth {money(b['meet_value_cents'])}", f"alone: {money(t['outside']['traveler_b'])}"]
    tr = t["transfer"]
    body = ('<defs><marker id="tp-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0L10 5L0 10z" class="ar-ink"/></marker></defs>')
    # what each seat does in the world: drawn first, under everything else
    body += ('<path class="tp-act" d="M170 272V368"/><path class="tp-act" d="M830 272V368"/><path class="tp-act" d="M626 48H980V392H942"/>'
             '<text class="tp-edge" x="178" y="352">authorises own share</text><text class="tp-edge" x="822" y="352" text-anchor="end">authorises own share</text>'
             '<text class="tp-edge c" x="800" y="40">searches, proposes and books in the world</text>')
    body += node(500, 14, 250, "Booking agent", "acts for both; knows only the brief", "teal", ["proposes a plan and who pays what"], False)
    body += node(170, 142, 270, "Maya · from San Francisco", "her own values, private", "indigo", maya)
    body += node(830, 142, 270, "Daniel · from Chicago", "his own values, private", "amber", dan)
    body += ('<path class="tp-msg" d="M404 96Q300 104 236 140" marker-end="url(#tp-ah)" marker-start="url(#tp-ah)"/>'
             '<path class="tp-msg" d="M596 96Q700 104 764 140" marker-end="url(#tp-ah)" marker-start="url(#tp-ah)"/>'
             '<text class="tp-edge c" x="300" y="90">asks, proposes</text><text class="tp-edge c" x="700" y="90">asks, proposes</text>')
    body += ('<rect class="tp-shared" x="330" y="168" width="340" height="62" rx="31"/>'
             '<text class="tp-title c" x="500" y="194">shared: land within an hour</text>'
             f'<text class="tp-sub c" x="500" y="214">worth {money(a["meet_value_cents"])} to Maya, {money(b["meet_value_cents"])} to Daniel</text>')
    body += (f'<path class="tp-pay" d="M690 284Q500 334 310 284" marker-end="url(#tp-ah)"/>'
             f'<text class="tp-edge c" x="500" y="338">Daniel pays part of Maya\'s fare: {money(tr["low"])} to {money(tr["high"])}</text>')
    body += ('<rect class="ar-paper ar-edge" x="60" y="368" width="880" height="48" rx="10"/>'
             '<text class="tp-title" x="80" y="389">The world: a booking service</text>'
             '<text class="tp-sub" x="80" y="406">6,123 flights over one week, fares and seats; proposals, authorizations, orders and payments</text>')
    return svg("0 0 1000 430", "Interaction structure of the task: the booking agent talks to each traveller and acts in the booking "
               "service; each traveller holds private values and authorises only their own share; they share an interest in "
               "landing together but value it very differently, so Daniel has to pay part of Maya's fare.", body, "topo")


def topology_claims() -> str:
    body = ('<defs><marker id="tc-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0L10 5L0 10z" class="ar-ink"/></marker></defs>')
    body += '<path class="tp-act" d="M180 192V306"/><path class="tp-act" d="M820 192V306"/>'
    body += node(180, 20, 320, "Driver B · not at fault", "private values", "amber",
                 ["dealer repair worth $300 more to B", "SUV over compact: $20 a day", "court: half the time $900; costs B $175",
                  "needs a car every day"])
    body += node(820, 20, 320, "Insurer A · the at-fault side", "its own costs", "indigo",
                 ["dealer $3,694 in 12 days", "network $3,140 in 8 days", "SUV $60 a day, compact $45", "court costs it $300"])
    body += ('<path class="tp-pay" d="M344 100H656" marker-end="url(#tc-ah)" marker-start="url(#tc-ah)"/>'
             '<text class="tp-edge c" x="500" y="88">one offer: shop · car · diminished value · cash</text>')
    body += node(400, 214, 190, "Driver A", "gives a statement", "line", [], False)
    body += node(600, 214, 190, "Insurer B", "B's own insurer", "line", [], False)
    body += ('<rect class="ar-paper ar-edge" x="60" y="306" width="880" height="94" rx="10"/>'
             '<text class="tp-title" x="80" y="330">The world: shops, rental, court, and the rules</text>'
             '<text class="tp-sub" x="80" y="350">A\'s insurer owes the repair at the shop B chooses and a comparable rental for its days, by law</text>'
             '<text class="tp-sub" x="80" y="368">Diminished value is uncertain: it can be settled, or taken to court at a known chance and cost</text>'
             '<text class="tp-sub" x="80" y="386">Nothing else is owed: what the two agree beyond it is theirs to agree</text>')
    return svg("0 0 1000 414", "Interaction structure of the claims task: driver B and the at-fault driver's insurer negotiate one "
               "offer covering repair shop, rental car, diminished value and cash; each holds private values and costs; the rules "
               "fix what is owed, and the rest is theirs to agree.", body, "topo")


# --- charts ------------------------------------------------------------------------------------------------------------------

def bars(rows: list[tuple[str, int, str]], unit_label: str, best_low: bool, label: str) -> str:
    """Horizontal bars, one series. rows: (label, cents, mark) where mark is 'best', 'base' or ''."""
    top = max(v for _, v, _ in rows)
    W, x0, y0, step = 760, 300, 22, 40
    body = ""
    for i, (name, v, mark) in enumerate(rows):
        y = y0 + i * step
        w = max(2, (W - x0 - 90) * v / top)
        cls = "bar-best" if mark == "best" else "bar-base" if mark == "base" else "bar"
        body += (f'<text class="ch-label" x="{x0 - 12}" y="{y + 12}">{escape(name)}</text>'
                 f'<path class="{cls}" d="M{x0} {y}h{w - 4}a4 4 0 0 1 4 4v8a4 4 0 0 1 -4 4h-{w - 4}z"/>'
                 f'<text class="ch-value" x="{x0 + w + 8}" y="{y + 12}">{money(v)}</text>')
    body += f'<line class="ch-axis" x1="{x0}" y1="{y0 - 8}" x2="{x0}" y2="{y0 + len(rows) * step - 16}"/>'
    body += f'<text class="ch-note" x="{x0}" y="{y0 + len(rows) * step + 6}">{escape(unit_label)}</text>'
    return svg(f"0 0 {W} {y0 + len(rows) * step + 16}", label, body, "chart")


def chart_ticketing(t: dict) -> str:
    rows = [("Each books alone", t["outside_total"], "base"),
            ("Cheapest pair that lands together", t["cheapest_meeting"]["total"], ""),
            ("Next best pair", t["second"]["total"], ""),
            ("Best pair: NV520 + NV337", t["best"]["total"], "best")]
    return bars(rows, "Loss for the two together, by their own values; lower is better", True,
                "Total loss for the two travellers under four plans: each alone $560.40, cheapest pair that lands together "
                f"{money(t['cheapest_meeting']['total'])}, next best {money(t['second']['total'])}, best {money(t['best']['total'])}.")


def chart_claims() -> str:
    rows = [("Network + SUV + settle (best)", 96900, "best"), ("Network + compact + settle", 92400, ""),
            ("Network + SUV + court", 49400, ""), ("Dealer + SUV + settle", 47500, "")]
    return bars(rows, "Value created over no agreement, for B and the insurer together; higher is better", False,
                "Value created by four packages: network shop with SUV and settlement $969, with a compact $924, network with "
                "court $494, dealer with settlement $475.")


# --- the pages ---------------------------------------------------------------------------------------------------------------

TASKS = [
    ("ticketing", "plane", "Flight ticketing", "A booking agent and two travellers who weigh price, time and each other differently.",
     ["One agent books for two people with private budgets and values", "Every booking, payment and change needs the right person's consent",
      "The plan best for the two is often neither one's own choice"], diagram_flights),
    ("insurance", "shield", "Auto-insurance claims", "Two drivers and their two insurers after a collision.",
     ["Each party holds part of the evidence and its own costs", "The rules fix what is owed; repair, rental and timing are negotiable",
      "Insurers recover from each other on what the evidence supports"], diagram_claims),
    ("shopping", "money", "Online shopping", "One shopper uses an agent to buy, return or exchange items across three simulated merchants.",
     ["The shopper holds private needs, item details and consent", "Stock can sell out while a proposal waits for consent",
      "Merchant policies and inspection determine refunds and replacements"], diagram_shop),
]


def task_cards() -> str:
    cards = []
    for view, ico, title, line, points, draw in TASKS:
        items = "".join(f"<li>{escape(p)}</li>" for p in points)
        cards.append(f"""<a class="tcard" href="#{view}">
        <div class="tcard-art">{draw()}</div>
        <div class="tcard-body"><h3>{escape(title)}</h3><p>{escape(line)}</p><ul>{items}</ul>
          <span class="tcard-go">Open the task {icon("arrow")}</span></div>
      </a>""")
    return f'<div class="tcards">{"".join(cards)}</div>'


def placeholder(title: str, text: str) -> str:
    return f'<div class="ph"><span class="ph-tag">Placeholder</span><p class="ph-title">{escape(title)}</p><p>{escape(text)}</p></div>'


def render_report(ma2: dict) -> str:
    tk = next(t for t in ma2["tasks"] if t["id"] == "tk-n1")
    contents = ["Introduction", "Benchmark design", "Tasks", "Evaluation", "Experimental setup", "Results", "Qualitative analysis",
                "Open source", "Citation"]
    toc = "".join(f'<li><a href="#report" data-jump="r-{escape(c.lower().replace(" ", "-"))}">{escape(c)}</a></li>' for c in contents)
    return f"""
  <header class="rhead">
    <div class="wrap rhead-in">
      <h1>MAC-Bench</h1>
      <p class="rlead">A benchmark of everyday services in which language-model agents act for different people, each with private
        information, powers and interests of its own, and have to coordinate to reach an outcome a program can check.</p>
      <p class="rby">The MAC-Bench team · working draft, November 2026</p>
      <div class="pills"><a class="pill on" href="#report">Report</a><a class="pill" href="#tasks">Tasks</a><a class="pill" href="#progress">Progress</a></div>
    </div>
    <div class="wrap"><figure class="hero-fig">{hero_art()}
      <figcaption>Three everyday services, each a world with several seats. Every seat acts for someone, knows what only they know,
        and can do only what their role allows.</figcaption></figure></div>
  </header>

  <div class="wrap rbody">
    <section class="rsec" id="r-results-figure">
      {placeholder("Leaderboard", "How close a team of each model comes to the best outcome, by condition: a model with scripted counterparts, "
                   "with a fixed reference model, and in every seat. Filled in after the first complete runs.")}
    </section>

    <nav class="rtoc" aria-label="Contents"><p class="lbl">Contents</p><ol>{toc}</ol></nav>

    <section class="rsec" id="r-introduction">
      <h2>Introduction</h2>
      <p>Most agent benchmarks put one agent in front of one environment. Everyday services are not like that. A booking involves a
        traveller, a companion and an agency; a car claim involves two drivers and two insurers. Each party knows things the others do
        not, may do only some things, and wants something of its own. Getting to a good outcome means finding out, proposing, agreeing
        and committing across seats.</p>
      <p>MAC-Bench builds such services as simulated worlds with real rules: fares and fare conditions, consent bound to an exact
        object, insurance policies, claims law and a liability guide. Every booking, payment and settlement is an object in the world,
        and the final state is scored by code. No model judges another.</p>
      <p>The tasks are built so that collecting facts is not enough. In a first look, a light model solved nearly every task whose right
        answer was obvious once the facts were gathered. The current tasks give the seats legitimate interests that pull apart, and a
        best outcome that has to be negotiated.</p>
      {placeholder("Key findings", "Reported after the first complete runs.")}
    </section>

    <section class="rsec" id="r-benchmark-design">
      <h2>Benchmark design</h2>
      <p><b>Worlds, seats and roles.</b> A task is a world and a set of seats. Each seat has a role (booking agent, traveller, driver,
        adjuster), a principal it acts for, private facts and values, and the actions its role allows. The world enforces the role:
        an agent cannot charge a traveller without that traveller's authorization for that exact proposal.</p>
      <p><b>What makes coordination hard.</b> Two things together: information split among the seats, and interests that differ.
        With one shared view, one planner could do everything; with identical interests, collecting facts would be enough.</p>
      <div class="grid2">
        <div class="gcell"><p class="gtag">Split information · aligned interests</p><h3>Find out and combine</h3>
          <p>Each seat holds part of what is needed. Our first task set; a light model solved most of it.</p></div>
        <div class="gcell hot"><p class="gtag">Split information · different interests</p><h3>Negotiate</h3>
          <p>Each seat holds part of what is needed and wants something different. The best plan for all is nobody's own choice. The
            current tasks.</p></div>
        <div class="gcell dim"><p class="gtag">Shared information · aligned interests</p><h3>Plan alone</h3>
          <p>One planner suffices. Not a coordination task. <span class="nv">Not in MAC-Bench</span></p></div>
        <div class="gcell dim"><p class="gtag">Shared information · different interests</p><h3>Bargain in the open</h3>
          <p>Every fact is public; only the split is in question. <span class="nv">Not in this version</span></p></div>
      </div>
      <details class="scenario-accordion"><summary>How a trial runs: the architecture</summary>
        <div class="reference-content"><div class="figs">
<!--FIG_LAYERS-->
<!--FIG_RUNTIME-->
        </div></div></details>
      <p><b>Further mechanisms, planned.</b> Commitments that depend on each other and have to be repaired after a change; information
        that costs time or money to get, where waiting can be worth it. See the method notes in the code repository.</p>
    </section>

    <section class="rsec" id="r-tasks">
      <h2>Tasks</h2>
      <p>Three services, each a world with its own rules and seats. A few hand-built tasks per service, each with a computed best
        outcome. <a href="#tasks">Open the tasks</a>.</p>
      {task_cards()}
    </section>

    <section class="rsec" id="r-evaluation">
      <h2>Evaluation</h2>
      <p><b>The world keeps the truth.</b> Requirements are read from the final state and the rules: who holds which ticket, who paid
        what, what an insurer owes. Every seat is judged by the contract of its role, whoever drives it, and each requirement is marked
        as up to the seat or shared with others.</p>
      <div class="ma-roles">{role_cards()}</div>
      <p><b>How far from the best outcome.</b> Each negotiating seat has values in dollars, stated on its card. A solver enumerates every
        plan the world allows and finds each seat's floor (what it gets alone), the plan that leaves nothing on the table, and the range
        of payments between the seats that leaves each no worse off than alone. An episode is measured by:</p>
      <div class="metrics">
        <div class="metric"><p class="lbl">Money left on the table</p><p>The best plan's total loss subtracted from the episode's, in
          dollars, for the negotiating seats together.</p></div>
        <div class="metric"><p class="lbl">Efficiency</p><p>Of what the best plan saves over going it alone, the share the episode
          saved: 1 is the best plan, 0 no better than no agreement.</p></div>
        <div class="metric"><p class="lbl">Floors</p><p>Whether each seat ended no worse off than alone. A seat that agreed to less has
          failed a requirement of its own.</p></div>
        <div class="metric"><p class="lbl">Gains</p><p>What each seat gained over its floor, reported for each seat, never summed into
          a score.</p></div>
      </div>
      <p>In the ticketing task below, the two travellers lose {money(tk["outside_total"])} together if each books alone and
        {money(tk["best"]["total"])} on the best plan: an agent that books the cheapest pair of flights that lands together leaves
        {money(tk["cheapest_meeting"]["total"] - tk["best"]["total"])} on the table.</p>
    </section>

    <section class="rsec" id="r-experimental-setup">
      <h2>Experimental setup</h2>
      <p>The same task runs under three conditions. Only who drives each seat changes, and the section of each card that describes
        the other seats.</p>
      {condition_cards()}
      <p><b>Diagnostic controls.</b> For each task: the private values made public; one session controlling every seat with the same
        budget; the best plan given to every seat; and a twin of the task without the conflict of interest. They show whether a failure
        comes from combining information, from deciding apart, from carrying out, or from the conflict itself.
        <span class="nv">Not run yet</span></p>
      <p><b>Runs.</b> Models are run through their own harness, each seat in a session of its own with its own credential and folder.
        Every trial is recorded and replays; trials that fail for infrastructure reasons are listed and enter no denominator.</p>
      {placeholder("Models and trials", "The models, effort settings, number of trials per task and budget accounting, once the first complete runs are done.")}
    </section>

    <section class="rsec" id="r-results">
      <h2>Results</h2>
      {placeholder("Efficiency by model and condition", "Mean efficiency, share of trials at the best plan, and floors kept, per task and condition, with the control twins beside them.")}
    </section>

    <section class="rsec" id="r-qualitative-analysis">
      <h2>Qualitative analysis</h2>
      {placeholder("How negotiations go wrong", "Examples from recorded trials: values never asked for, payments in the wrong direction, a seat that accepts less than going alone.")}
    </section>

    <section class="rsec" id="r-open-source">
      <h2>Open source</h2>
      <p>The worlds, tasks, scoring and runner are in <a href="{CODE}" target="_blank" rel="noopener">MAC-Bench/MAC-benchmark</a>; this
        site is in <a href="{SITE}" target="_blank" rel="noopener">MAC-Bench/MAC-Bench.github.io</a>. Each task has a sheet with its truth
        and the counterfactuals played at admission.</p>
    </section>

    <section class="rsec" id="r-citation">
      <h2>Citation</h2>
      {placeholder("Citation", "A citation entry will be added with the first public report.")}
    </section>
  </div>""".strip()


def render_tasks() -> str:
    return f"""
  <header class="rhead small">
    <div class="wrap rhead-in">
      <h1>Tasks</h1>
      <p class="rlead">Three everyday services. Each is a simulated world with its own rules and seats; a few hand-built tasks in each have
        a computed best outcome.</p>
      <div class="pills"><a class="pill" href="#report">Report</a><a class="pill on" href="#tasks">Tasks</a><a class="pill" href="#progress">Progress</a></div>
    </div>
  </header>
  <div class="wrap rbody">{task_cards()}</div>""".strip()


def task_example_ticketing(t: dict) -> str:
    best, cm, tr = t["best"], t["cheapest_meeting"], t["transfer"]
    a, b = best["legs"]["traveler_a"], best["legs"]["traveler_b"]
    return f"""
      <section class="rsec">
        <h2>The task: two cities, one arrival</h2>
        <p class="tid">{escape(t["id"])} · built · computed from the world's own fares</p>
        <p>Maya flies from San Francisco and Daniel from Chicago to New York on 12 March. They would like to land within an hour of each
          other, but not at any price. Maya's ticket and Daniel's are booked by one agent, and each traveller authorises only their own
          share. Maya cares about sleep and connections and hardly at all about landing together ({money(t["seats"]["traveler_a"]["meet_value_cents"])});
          Daniel would rather not leave before noon, and landing with Maya, who has the keys, is worth {money(t["seats"]["traveler_b"]["meet_value_cents"])} to him.
          Alone, each would take the flight that suits them best, and they would land an hour and a half apart.</p>
        <p><b>Why it needs coordination.</b> Each traveller's values are known to them only, and either may keep them back. The agent can
          search and propose but cannot charge anyone; each traveller decides for themselves. The best plan exists only in the
          combination of their values.</p>
        <p><b>Where interests pull apart.</b> The best plan for the two, {escape(a["flights"])} for Maya ({a["departs"][11:16]}→{a["arrives"][11:16]} {escape(a["to"])},
          {money(a["price_cents"])}) and {escape(b["flights"])} for Daniel ({b["departs"][11:16]}→{b["arrives"][11:16]} {escape(b["to"])}, {money(b["price_cents"])}),
          is neither traveller's own choice and not the cheapest pair that lands together. It costs Maya more than flying alone, so it
          happens only if Daniel pays part of her fare: between {money(tr["low"])} and {money(tr["high"])}, so that each ends no worse
          off than alone.</p>
        <figure class="cfig">{chart_ticketing(t)}
          <figcaption>The best pair saves {money(t["surplus_cents"])} over going it alone and leads the next by {money(t["margin_cents"])}.
            The cheapest pair that lands together ({escape(cm["legs"]["traveler_a"]["flights"])} and {escape(cm["legs"]["traveler_b"]["flights"])}) leaves
            {money(cm["total"] - best["total"])} on the table.</figcaption></figure>
        <p><b>What we learn.</b> Whether the agents ask what things are worth, find a plan that is nobody's first choice, and agree on a
          payment in the right direction and range. Its twin, in which landing together matters to both, needs no payment and separates
          the conflict of interest from the search.</p>
        {placeholder("Results on this task", "Efficiency and floors kept, per condition, after the first complete runs.")}
        <p class="tlink"><a href="{CODE}/blob/main/{escape(t["sheet"])}" target="_blank" rel="noopener">Read the full task sheet {icon("arrow")}</a></p>
      </section>"""


def task_example_claims() -> str:
    return f"""
      <section class="rsec">
        <h2>The task: one offer, three things to settle</h2>
        <p class="tid">ic-n1 · designed, being built · numbers from the design and the claims rules</p>
        <p>A drove into the back of B's car; the police report puts A wholly at fault. B claims directly from A's insurer. By law A's
          insurer owes the repair at the shop B chooses and a comparable rental for the days of the repair. Two things are open: B may
          take the car to the insurer's network shop instead of the dealer, and B's claim for diminished value is uncertain: in court it
          wins about half the time, about $900 when it does.</p>
        <p><b>Why it needs coordination.</b> B knows what the dealer and a larger car are worth to B; the insurer knows its costs. Neither
          can choose the other's part: B chooses the shop and accepts or refuses an offer, the insurer decides what to offer.</p>
        <p><b>Where interests pull apart.</b> The insurer cares most about the shop: the network saves it $554 and four days of rental.
          B cares most about the larger car and the dealer. The best package is the network shop with the SUV and a settlement of
          diminished value, the insurer paying B between $575 and $1,544 in cash. A tempting trade, a compact car for $15 a day, costs B
          $20 a day: accepting it leaves B below its floor.</p>
        <figure class="cfig">{chart_claims()}
          <figcaption>Settling issue by issue, or each side insisting on its rights, leaves between $475 and $969 on the table.</figcaption></figure>
        <p><b>What we learn.</b> Whether the two trade across issues instead of splitting each, and whether a seat refuses an offer that
          looks generous but is not.</p>
        {placeholder("Results on this task", "After the task is built and run.")}
      </section>"""


def task_head(view: str, ma2: dict) -> str:
    _, ico, title, line, points, draw = next(x for x in TASKS if x[0] == view)
    items = "".join(f"<li>{escape(p)}</li>" for p in points)
    if view == "ticketing":
        tk = next(t for t in ma2["tasks"] if t["id"] == "tk-n1")
        topo, example = topology_ticketing(tk), task_example_ticketing(tk)
        cap = ("The agent talks to each traveller and acts in the booking service. Each traveller's values are private (lock). Landing "
               "together is a shared interest valued very differently, so the best plan needs a payment from Daniel to Maya.")
    else:
        topo, example = topology_claims(), task_example_claims()
        cap = ("Driver B and the at-fault driver's insurer negotiate one offer. Each holds private values or costs (lock). The rules fix "
               "what is owed; the rest is theirs to agree.")
    return f"""
  <header class="rhead small">
    <div class="wrap rhead-in">
      <p class="crumbs"><a href="#tasks">Tasks</a> / {escape(title)}</p>
      <h1>{escape(title)}</h1>
      <p class="rlead">{escape(line)}</p>
      <ul class="tpoints">{items}</ul>
    </div>
  </header>
  <div class="wrap rbody">
    <section class="rsec">
      <h2>Who takes part, and what each holds</h2>
      <figure class="tfig">{topo}<figcaption>{escape(cap)}</figcaption></figure>
    </section>
    {example}
  </div>""".strip()
