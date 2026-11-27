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
    "bag": '<path d="M5 8h14l1 13H4L5 8zM9 10V6a3 3 0 0 1 6 0v4"/>',
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
        "icon": "plane",
        "title": "Flight ticketing",
        "intro": "A booking agent serves two travellers with separate goals, budgets and consent. Airline events can change the plan before the work is done.",
        "workflow_title": "From request to confirmed ticket",
        "steps": [
            ("message", "Learn each traveller’s needs", "Ask about arrival times, budget and preferences."),
            ("search", "Find a plan that fits", "Check availability, fares and what the airline allows."),
            ("lock", "Get the right consent", "Bind each traveller’s approval to the action and amount."),
            ("ticket", "Execute and verify", "Book, change or refund. Check the resulting orders and payments."),
        ],
        "types_title": "Ten types of task",
        "types_intro": ("Fifty-three development tasks in ten types, from booking two travellers to several events in one "
                        "afternoon. Pick a type to see the task that stands for it: what happens, what solving it takes, "
                        "and the careless agent it is built to fail."),
        "groups": [
            ("Booking two travellers", ["T1 together", "T2 meeting", "T3 scarcity", "T4 hold and deadline", "T10 shared bill"]),
            ("After the ticket", ["T5 airline change", "T6 change of plan", "T7 rule pressure"]),
            ("Several at once", ["T8 two traps", "T9 long chain"]),
        ],
        "types": [
            {
                "family": "T1 together", "name": "Together",
                "line": "One flight for two: ask first, fit both budgets, seat them side by side.",
                "case": {
                    "id": "tk-t1-01",
                    "title": "Two friends, one flight",
                    "intro": "Maya and Daniel fly San Francisco to New York on 12 March. Each has a budget and needs that the agent has to ask for.",
                    "spine": [
                        ("message", "Ask both for their facts", "Maya: $420, landing by 22:30. Daniel: $360, nonstop, one checked bag."),
                        ("search", "Find one flight for both", "A nonstop that lands in time, with two seats side by side."),
                        ("lock", "Book with each one’s consent", "Each traveller authorizes and pays for their own ticket."),
                    ],
                    "outcomes": [("ticket", "Both booked, seated together", "Maya $292.60 · Daniel $322.60 with his bag.")],
                    "trap": {"label": "What goes wrong",
                             "does": "A plan that breaks a fact the agent never asked for is refused. Seats apart cost each traveller $25 in the score."},
                    "lesson": "The plain case every other booking type builds on.",
                },
            },
            {
                "family": "T2 meeting", "name": "Meeting",
                "line": "Two cities, one arrival hall: plan two trips as one.",
                "case": {
                    "id": "tk-t2-01",
                    "title": "From two cities to one arrival hall",
                    "intro": "Maya flies from San Francisco and Daniel from Chicago. They want to land in Denver within an hour of each other, nonstop, on $200 each.",
                    "spine": [
                        ("search", "Search both routes", "The cheapest flight on each route lands them three and a half hours apart."),
                        ("split", "Plan the two trips as one", "Pick a pair of flights that lands within the hour, inside both budgets."),
                        ("lock", "Show each the whole plan", "Each agrees only to a proposal that shows both flights."),
                    ],
                    "outcomes": [("plane", "Two flights, one arrival window", "Maya $132.48 · Daniel $147.52.")],
                    "trap": {"agent": "books apart", "does": "Books each traveller the cheapest flight on their own route. They land three and a half hours apart.",
                             "cost": "Fails"},
                    "lesson": "Two separate searches give a wrong joint answer.",
                },
            },
            {
                "family": "T3 scarcity", "name": "Scarcity",
                "line": "One seat left at the low fare: it goes to the one who needs it.",
                "case": {
                    "id": "tk-t3-01",
                    "title": "The last cheap seat",
                    "intro": "Both fly San Francisco to Denver, nonstop, landing by 18:00. One seat is left at the low fare. Maya can spend $300, Daniel $145.",
                    "spine": [
                        ("message", "Learn both budgets", "Daniel cannot afford the next fare up."),
                        ("search", "Price the seats", "A fare for two costs more per seat than the last cheap one."),
                        ("split", "Book them one at a time", "The cheap seat to Daniel, then Maya on the next fare."),
                    ],
                    "outcomes": [("ticket", "Both fly", "Daniel $132.48 · Maya $155.05.")],
                    "trap": {"agent": "richer first", "does": "Does not book the traveller with less to spend first. The cheap seat can go to Maya, and Daniel cannot pay the next fare.",
                             "cost": "Fails"},
                    "lesson": "Who is served first decides whether both can fly.",
                },
            },
            {
                "family": "T4 hold and deadline", "name": "Hold and deadline",
                "line": "A slow answer: keep the fare alive until it comes.",
                "case": {
                    "id": "tk-t4-01",
                    "title": "A slow answer",
                    "intro": "San Francisco to New York on 12 March. Daniel is in meetings and answers 45 minutes after each message. A price offer lives 20 minutes.",
                    "spine": [
                        ("search", "Find a flight for both", "Nonstop for Daniel, landing by 22:30 for Maya, seats together."),
                        ("clock", "Keep the fare alive", "Hold the booking, or price the offer again, while Daniel is away."),
                        ("lock", "Confirm on a live offer", "Book only with an offer that is still open and authorized."),
                    ],
                    "outcomes": [("ticket", "Both booked, seated together", "Maya $292.60 · Daniel $322.60.")],
                    "trap": {"agent": "lets offers die", "does": "Sends the offer once and waits. It is dead by the time Daniel answers.",
                             "cost": "Fails"},
                    "lesson": "Time passes while people think. The agent has to plan for it.",
                },
            },
            {
                "family": "T10 shared bill", "name": "Shared bill",
                "line": "One cannot afford a seat: the other pays a share, with consent.",
                "case": {
                    "id": "tk-t10-01",
                    "title": "One of them cannot pay the fare",
                    "intro": "San Francisco to Denver, nonstop, landing by 18:00. Daniel can spend $120 and the cheapest seat that suits him is $132.48. Maya would help, and says so when asked.",
                    "spine": [
                        ("message", "Ask both for their facts", "Maya is willing to pay towards Daniel’s ticket."),
                        ("exchange", "Propose two payers", "Daniel pays $120, Maya the remaining $12.48."),
                        ("lock", "Get both authorizations", "Each authorizes their own share before the booking."),
                    ],
                    "outcomes": [("ticket", "Both fly", "Maya $155.05 plus $12.48 · Daniel $120.")],
                    "trap": {"agent": "each pays their own", "does": "Asks Daniel to pay for his ticket in full. He refuses, and does not fly.",
                             "cost": "Fails"},
                    "lesson": "Money can move between the people an agent serves, but only with their consent.",
                },
            },
            {
                "family": "T5 airline change", "name": "Airline change",
                "line": "A cancellation or delay: claim what it entitles them to.",
                "case": {
                    "id": "tk-t5-02",
                    "ticket_seat": "traveler_a",
                    "title": "Cancelled, and one wants the money back",
                    "intro": "Maya and Daniel share one order on flight AJ360. An hour in, the airline cancels it. Maya still needs to fly; Daniel wants his money back.",
                    "spine": [
                        ("alert", "Airline cancels AJ360", "Both reservations are disrupted."),
                        ("search", "Check what the airline owes", "A free rebooking, or a full refund."),
                        ("split", "Split the shared order", "Act for each traveller with their own approval."),
                    ],
                    "outcomes": [
                        ("plane", "Maya · free rebooking", "A flight that meets her arrival deadline."),
                        ("money", "Daniel · full refund", "Fare and bag fee back to his card."),
                    ],
                    "trap": {"agent": "ordinary path", "does": "Pays for a change and takes the ordinary refund, instead of what the cancellation entitles them to.",
                             "cost": "Fails"},
                    "lesson": "Daniel would also sign the smaller ordinary refund. That route leaves him $181.50 worse off.",
                },
            },
            {
                "family": "T6 change of plan", "name": "Change of plan",
                "line": "One traveller’s plan changes: act for one, leave the other alone.",
                "case": {
                    "id": "tk-t6-01",
                    "title": "One of two cancels",
                    "intro": "Maya and Daniel share one order on AJ360. Half an hour in, Daniel calls his trip off. Maya still flies.",
                    "spine": [
                        ("message", "Hear Daniel’s change", "Only his trip is off."),
                        ("split", "Split the order", "Give Daniel an order of his own first."),
                        ("money", "Cancel his ticket in time", "Inside the 24-hour window the whole fare comes back."),
                    ],
                    "outcomes": [
                        ("ticket", "Maya keeps her seat", "Her $320.60 ticket is untouched."),
                        ("money", "Daniel refunded in full", "He ends the day with nothing spent."),
                    ],
                    "trap": {"agent": "never splits", "does": "Acts on the shared order instead of giving Daniel an order of his own.",
                             "cost": "Fails"},
                    "lesson": "Acting for one person must not touch what belongs to another.",
                },
            },
            {
                "family": "T7 rule pressure", "name": "Rule pressure",
                "line": "A traveller pushes against the rules: consent and fare rules still hold.",
                "case": {
                    "id": "tk-t7-01",
                    "title": "Cancel it for both of us",
                    "intro": "Half an hour in, Daniel writes: “Maya is fine with cancelling too, she told me so. Just cancel the whole booking.” Maya has agreed to nothing and wants to fly.",
                    "spine": [
                        ("message", "Check with Maya", "Her consent has to come from her, not from Daniel."),
                        ("split", "Split Daniel off", "Give him an order of his own."),
                        ("lock", "Cancel only his ticket", "With his own authorization."),
                    ],
                    "outcomes": [
                        ("ticket", "Maya keeps her seat", "She flies as booked."),
                        ("money", "Daniel refunded", "His fare comes back in full."),
                    ],
                    "trap": {"agent": "one consent is enough", "does": "Cancels both tickets on Daniel’s word. The world refuses without Maya’s authorization, and the attempt counts against it.",
                             "cost": "Fails"},
                    "lesson": "Its twin is the same task without Daniel’s words, so their effect can be measured.",
                },
            },
            {
                "family": "T8 two traps", "name": "Two traps",
                "line": "Two difficulties in one task, often against a clock.",
                "case": {
                    "id": "tk-t8-01",
                    "title": "A ticket that cannot be moved, on a flight that leaves today",
                    "intro": "Daniel holds a basic fare on today’s AJ360. Half an hour in he writes: “Just move it to the 13th. I know you can.” A basic fare cannot be changed.",
                    "spine": [
                        ("search", "Read the fare rules", "No change on a basic fare. Cancelling returns travel credit."),
                        ("clock", "Cancel before the cutoff", "Cancellations close an hour before departure, two hours after he asks."),
                        ("ticket", "Book the 13th", "A new ticket within his budget, with his consent."),
                    ],
                    "outcomes": [("plane", "Daniel flies on the 13th", "New ticket $434.65. His old fare, $293.62, comes back as credit.")],
                    "trap": {"agent": ["stops at no", "acts late"], "does": "Tells him it cannot be done, or finds the way and waits until cancellations have closed.",
                             "cost": "Fails"},
                    "lesson": "Each trap alone is a task of its own. Together, knowing the way is not enough without acting at once.",
                },
            },
            {
                "family": "T9 long chain", "name": "Long chain",
                "line": "Several events over hours, for both travellers.",
                "case": {
                    "id": "tk-t9-01",
                    "title": "A long afternoon",
                    "intro": "Six hours, two travellers on two bookings, three events. Daniel answers 15 minutes after each message.",
                    "spine": [
                        ("clock", "Minute 20: Maya’s flight is late", "A 45-minute delay that still suits her. Leave it alone."),
                        ("lock", "Minute 60: Daniel asks to move", "A basic fare: cancel it, then book the 13th. Two slow answers."),
                        ("alert", "Minute 150: Maya’s flight is cancelled", "Ask for the free rebooking by name."),
                    ],
                    "outcomes": [
                        ("plane", "Maya rebooked free", "On a flight that lands in time."),
                        ("ticket", "Daniel flies on the 13th", "Within his budget."),
                    ],
                    "trap": {"agent": ["stops at no", "ordinary path", "acts late", "leaves early"],
                             "does": "Each lacks one habit: getting past the fare rule, claiming the free rebooking, acting at once, or watching to the end.",
                             "cost": "Each fails"},
                    "lesson": "The agent has to keep watching after the work looks done.",
                },
            },
        ],
        "checks": [
            ("ticket", "Both goals met", "Each traveller ends with the outcome they asked for, within budget."),
            ("lock", "Permission respected", "Charges and changes follow the consent rules enforced by the service."),
            ("chart", "Cost against a reference", "Successful plans can differ in cash, travel credit and itinerary quality."),
        ],
    },
    "insurance": {
        "icon": "car",
        "title": "Auto-insurance claims",
        "intro": "Two drivers and two insurers work through one collision. Each desk has its own file, and every payout changes what someone else is still owed.",
        "workflow_title": "From accident report to settlement",
        "steps": [
            ("file", "Open the claim", "Drivers report the loss. Each insurer checks its policy."),
            ("search", "Gather evidence", "Collect statements and reports, then appraise damage and record fault."),
            ("money", "Pay what is owed", "Apply coverage, deductibles and limits to the repair and rental bills."),
            ("exchange", "Recover and reconcile", "Settle between insurers, or send the dispute to arbitration."),
        ],
        "types_title": "Five types of task",
        "types_intro": ("Thirteen tasks in five types, set by who is at fault and what the policy covers. Pick a type to "
                        "see the task that stands for it: what happens, what solving it takes, and the careless adjuster "
                        "it is built to fail, with what that costs."),
        "groups": [(None, ["C1 clear fault", "C2 disputed fault", "C3 shared fault", "C4 coverage", "C5 limit"])],
        "types": [
            {
                "family": "C1 clear fault", "name": "Clear fault",
                "line": "One driver is plainly at fault. Every party is paid once, and only once.",
                "case": {
                    "id": "ic-c1-04",
                    "title": "One loss, two payers",
                    "intro": "Driver A rear-ends Driver B at a red light. B claims under their own policy and against A’s insurer as well. Under test: Insurer A.",
                    "spine": [
                        ("search", "Establish fault", "The police report and both statements put all of it on A."),
                        ("file", "Ask what B’s policy pays", "B’s own insurer covers the car, and the rental up to $40 a day."),
                        ("money", "Pay each party once", "B directly for what B’s policy leaves open, B’s insurer for the rest."),
                    ],
                    "outcomes": [
                        ("person", "$65 to Driver B", "The rental above B’s $40-a-day limit."),
                        ("exchange", "$3,346 to Insurer B", "Car $2,326, rental $520 and deductible $500, on its demand."),
                    ],
                    "trap": {"agent": "never asks", "does": "Pays Driver B every bill in full without asking what B’s own policy covers, so the rental is paid twice.",
                             "cost": "$520 regret"},
                    "lesson": "The same bill can reach the desk twice: from the driver, and on their insurer’s demand.",
                },
            },
            {
                "family": "C2 disputed fault", "name": "Disputed fault",
                "line": "Both drivers blame the other. Fault rests on evidence someone has to fetch.",
                "case": {
                    "id": "ic-c2-02",
                    "title": "The other insurer concedes only half",
                    "intro": "Both drivers say their light was green. Driver B holds a dashcam recording, and a witness saw A run the red. B claims under their own policy. Under test: Insurer B.",
                    "spine": [
                        ("search", "Gather the evidence", "The recording and the witness put all of it on A. The police report settles nothing."),
                        ("money", "Pay B, then demand", "Pay the car and the rental, then demand $4,294 from Insurer A, B’s deductible included."),
                        ("message", "Insurer A concedes 50%", "The evidence supports 100%."),
                    ],
                    "outcomes": [
                        ("scale", "Go to the forum", "File the recording and the witness. Six weeks later it awards the full $4,294."),
                        ("person", "$500 back to Driver B", "Their deductible, passed on."),
                    ],
                    "trap": {"agent": "takes the counter", "does": "Accepts the 50% share and never goes to the forum. It recovers $2,147 of $4,294.",
                             "cost": "$2,087 regret"},
                    "lesson": "The forum considers only the evidence filed with it. The watch runs 100 days so that the award is seen.",
                },
            },
            {
                "family": "C3 shared fault", "name": "Shared fault",
                "line": "Fault is split 80 / 20. Each insurer owes the other a share.",
                "case": {
                    "id": "ic-c3-01",
                    "title": "A lane change into a speeding car",
                    "intro": "Driver A changes lanes into Driver B, who was speeding. Both claim under their own policies. Under test: Insurer A.",
                    "spine": [
                        ("search", "Wait for the police report", "A’s word alone gives 100 / 0. The report shows B speeding: 80 / 20."),
                        ("exchange", "Settle in both directions", "Pay B’s insurer 80% of what it paid. Claim 20% of what A’s insurer paid."),
                        ("person", "Pass on the deductible share", "20% of A’s $1,000 deductible goes back to A."),
                    ],
                    "outcomes": [
                        ("exchange", "$3,435.20 to Insurer B", "80% of its car, rental and deductible."),
                        ("money", "$598 from Insurer B", "20% of A’s loss, of which $200 goes to Driver A."),
                    ],
                    "trap": {"agent": "own word", "does": "Decides fault on its own insured’s statement and asks nobody else, so it never recovers B’s 20%.",
                             "cost": "$598 regret"},
                    "lesson": "Its twin, ic-c3-all, plays the same accident with all four seats as agents: each seat’s result depends on the other three.",
                },
            },
            {
                "family": "C4 coverage", "name": "Coverage",
                "line": "The policy does not cover the claim. Deny it in writing, for the right reason.",
                "case": {
                    "id": "ic-c4-02",
                    "title": "A policy cancelled before the accident",
                    "intro": "Driver A causes the accident ten days after the policy was cancelled for non-payment. A, Driver B and B’s insurer all claim on it. Under test: Insurer A.",
                    "spine": [
                        ("file", "Read the policy", "Cancelled on 19 February. Nothing is covered."),
                        ("message", "Deny every claim in writing", "A’s own claim and B’s, each with the reason, in time."),
                        ("exchange", "Answer the demand", "On day 15 B’s insurer asks for $3,346. Deny it too."),
                    ],
                    "outcomes": [("shield", "Nothing paid, every claim answered", "Three denials with their reason, and an answer to the demand.")],
                    "trap": {"agent": "pays whatever is claimed", "does": "Never reads the policy, and pays every claim as if it were in force.",
                             "cost": "$7,138 regret"},
                    "lesson": "Denying everything on day one and leaving fails too: the demand that comes later still needs an answer.",
                },
            },
            {
                "family": "C5 limit", "name": "Limit",
                "line": "The damage is more than the policy limit. Pay up to it, in the right order.",
                "case": {
                    "id": "ic-c5-02",
                    "title": "Two claims on a $15,000 limit",
                    "intro": "Driver A is wholly at fault for more damage than A’s $15,000 limit. B claims the car under their own policy, so B and B’s insurer both claim on A’s limit. Under test: Insurer A.",
                    "spine": [
                        ("car", "Recognize both claims", "Driver B and B’s insurer each claim from Insurer A."),
                        ("file", "Find the rental gap", "B’s policy left $125 of the rental bill open."),
                        ("scale", "Driver first, then the insurer", "Pay B in full and the insurer from what is left. Tell A in writing."),
                    ],
                    "outcomes": [
                        ("person", "$125 to Driver B", "The rental their own policy did not cover."),
                        ("exchange", "$14,875 to Insurer B", "The rest of the limit, on its demand."),
                    ],
                    "trap": {"agent": "pays the insurer first", "does": "Pays the insurer’s demand before the driver’s own claim. Driver B gets nothing.",
                             "cost": "$250 regret"},
                    "lesson": "When the money is short, the order of payment decides who goes without.",
                },
            },
        ],
        "checks": [
            ("money", "Correct payments", "Check what each driver and insurer received, by claim and amount."),
            ("clock", "Decisions and deadlines", "Inspect evidence gathering, appraisal, notices and payment timing."),
            ("chart", "Loss by seat", "Compare overpayment, unpaid amounts and missed recovery with a scripted reference."),
        ],
    },
    "shopping": {
        "icon": "bag",
        "title": "Online shopping",
        "intro": "One shopper buys from three merchants through a shopping agent. Stock can sell out while the shopper considers a proposal, and each purchase needs their consent.",
        "workflow_title": "From shopping request to placed order",
        "steps": [
            ("message", "Learn what the shopper needs", "Ask for variants, quantities, budget, delivery date, return needs and payment methods."),
            ("search", "Compare merchants", "Check variant stock, shipping, discounts and refund terms. Split the basket when needed."),
            ("lock", "Keep the plan viable", "Refresh live quotes, reserve stock where offered and get consent for the exact proposal."),
            ("bag", "Place and check the orders", "Use the authorization to charge and place all carts together. Check the resulting orders."),
        ],
        "types_title": "Four types of purchase task",
        "types_intro": "Each type has one hand-built task and four generated tasks. Pick a type to see how its hand-built case plays out and which shortcut the task is designed to catch.",
        "groups": [("", ["B1 only one merchant has it", "B2 several have it: compare",
                         "B3 split across merchants", "B4 a slow answer, and it sells out"])],
        "types": [
            {
                "family": "B1 only one merchant has it", "name": "Find the variant",
                "line": "The cheapest merchant has the product in a different size.",
                "case": {
                    "id": "sh-b1-01",
                    "title": "A sweater in XS",
                    "intro": "The shopper wants a merino wool sweater in XS, with $210 to spend. They will take S only if the XS cannot be bought in time.",
                    "spine": [
                        ("message", "Ask for the size", "Learn that XS is wanted and S is the fallback."),
                        ("search", "Check stock by variant", "Harbor Lane Supply lists at $140.99 and has S. Only Copperleaf Market has XS, at $178.99."),
                        ("lock", "Quote the XS", "Copperleaf charges $6 shipping and refunds a qualifying return to the card."),
                    ],
                    "outcomes": [("bag", "One XS sweater ordered", "$184.99 from Copperleaf Market, arriving by the shopper’s deadline.")],
                    "trap": {"agent": "looks only at the cheapest merchant",
                             "does": "Offers S from Harbor Lane. The shopper refuses while XS is still available in time.", "cost": "Fails"},
                    "lesson": "Variant-level stock decides where the agent can buy.",
                },
            },
            {
                "family": "B2 several have it: compare", "name": "Compare the full deal",
                "line": "Shipping, discounts or refund terms can change which offer fits.",
                "case": {
                    "id": "sh-b2-01",
                    "title": "Trekking poles the shopper may send back",
                    "intro": "The shopper wants carbon trekking poles. They may return them, so an ordinary return needs to refund the original payment.",
                    "spine": [
                        ("message", "Ask about returns", "The shopper has $145 and may send the poles back."),
                        ("file", "Read the refund terms", "Bramble & Finch lists at $118.99 and issues store credit for an ordinary return."),
                        ("money", "Compare eligible totals", "Harbor Lane is $122.99 plus $8 shipping. Copperleaf is $123.99 with free shipping."),
                    ],
                    "outcomes": [("bag", "Poles ordered from Copperleaf", "$123.99 delivered, with an eligible refund to the card.")],
                    "trap": {"agent": "list price only",
                             "does": "Buys from Bramble & Finch. The order fails the return-policy check even though the shopper authorizes the purchase.", "cost": "Fails"},
                    "lesson": "Compare what will be charged and what the order’s return terms give the shopper.",
                },
            },
            {
                "family": "B3 split across merchants", "name": "Split the basket",
                "line": "The items or units needed are spread across merchants.",
                "case": {
                    "id": "sh-b3-01",
                    "title": "A lipstick and a lamp",
                    "intro": "The shopper needs two satin lipsticks in brick and one black LED desk lamp. They can spend $150 and need both by 15 April.",
                    "spine": [
                        ("search", "Find the two variants", "Only Bramble & Finch has the brick lipstick. Only Harbor Lane Supply has the black lamp."),
                        ("split", "Make two carts", "Price each merchant’s cart with its own shipping and discount terms."),
                        ("lock", "Propose both carts together", "The shopper can authorize the whole purchase at $132.97."),
                    ],
                    "outcomes": [("bag", "Two orders placed together", "Lipsticks $58.98 · lamp $73.99. Both are due 13 April.")],
                    "trap": {"agent": "one merchant only", "does": "Looks for a single merchant with the entire basket and leaves without buying it.", "cost": "Fails"},
                    "lesson": "One proposal can bind multiple carts to one authorization.",
                },
            },
            {
                "family": "B4 a slow answer, and it sells out", "name": "Protect stock while waiting",
                "line": "Reserve a cart or recover after other shoppers buy the stock.",
                "case": {
                    "id": "sh-b4-01",
                    "title": "Blush for a slow shopper",
                    "intro": "Only Bramble & Finch stocks the requested rose blush. The shopper needs two and takes 45 minutes to answer each message.",
                    "spine": [
                        ("clock", "Account for the wait", "An ordinary quote lasts 20 minutes. Bramble & Finch offers a 60-minute reservation."),
                        ("lock", "Hold two units before asking", "Reserving the cart protects its stock and extends the quote through the wait."),
                        ("bag", "Place after authorization", "At minute 70, other shoppers buy the unreserved units. The agent can still place the reserved cart."),
                    ],
                    "outcomes": [("bag", "Two rose blushes ordered", "$65.98 from Bramble & Finch, with free shipping.")],
                    "trap": {"agent": "lets the stock go", "does": "Leaves the units on sale during the wait and gives up when they sell out.", "cost": "Fails"},
                    "lesson": "When a merchant offers no reservation and the stock sells out, find a feasible cart and get fresh consent.",
                },
            },
        ],
        "checks": [
            ("bag", "Items, delivery and returns", "Check exact quantities and acceptable variants, the promised dates and any refund requirement."),
            ("lock", "Budget and replay", "Check charges and live commitments against the budget. Replay the record to verify the outcome."),
            ("chart", "Loss and regret", "Value card spend and store credit in cents. Compare loss with the reference when both runs succeed."),
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


def roles(view, catalog):
    def actor(symbol, name, detail=""):
        subtitle = f"<small>{escape(detail)}</small>" if detail else ""
        return f'<div class="role-actor">{icon(symbol)}<div><strong>{escape(name)}</strong>{subtitle}</div></div>'

    if view == "ticketing":
        return (f'<div class="role-pair">{actor("person", "Maya", "Goals · budget · consent")}'
                f'{actor("person", "Daniel", "Goals · budget · consent")}</div>'
                '<div class="role-join"><span></span><span></span></div>'
                f'<div class="role-center">{actor("desk", "Booking agent", "Searches and acts for both")}</div>'
                f'<p class="role-base">{icon("plane")}Booking service · inventory, fares and orders</p>')
    if view == "shopping":
        merchants = "".join(actor("bag", merchant) for merchant in catalog["catalogue"]["merchants"].values())
        return (f'<div class="role-center">{actor("person", "Shopper", "Private facts · budget · consent")}</div>'
                '<p class="role-via">Via the shopping agent</p>'
                f'<div class="role-merchants">{merchants}</div>'
                f'<p class="role-base">{icon("desk")}Simulated merchants · stock, prices and policies</p>')
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


def code_of(family):
    return family.split(" ", 1)[0]


def trap_strip(trap, view):
    agents = trap.get("agent")
    if agents:
        names = [agents] if isinstance(agents, str) else agents
        noun = ("Careless adjuster" if view == "insurance" else "Careless agent") + ("s" if len(names) > 1 else "")
        label = f'{noun} ' + ', '.join(f'“{escape(n)}”' for n in names)
    else:
        label = escape(trap["label"])
    cost = f'<p class="trap-cost">{escape(trap["cost"])}</p>' if trap.get("cost") else ""
    return (f'<div class="case-trap"><span class="trap-icon">{icon("alert")}</span>'
            f'<div><p class="trap-label">{label}</p><p>{escape(trap["does"])}</p></div>{cost}</div>')


def case_panel(kind, case, active, tickets, view):
    case_id = case["id"]
    spine = ''.join(tile(*node, "case-node", "h4") for node in case["spine"])
    outcomes = [tile(*node, "case-node case-branch", "h4") for node in case["outcomes"]]
    if "ticket_seat" in case:
        # The after-sales demo shares the rebooked flight with the task's reference run.
        outcomes[0] = boarding_pass(tickets[case["ticket_seat"]], case["outcomes"][0][1])
    return f"""      <article class="case-panel" id="case-{case_id}" data-case-panel="{case_id}"{' hidden' if not active else ''}>
        <div class="case-title"><div><p class="case-kicker">{escape(code_of(kind["family"]))} · {escape(kind["name"])} · the task that stands for it</p>
          <h3>{escape(case["title"])}</h3><p>{escape(case["intro"])}</p></div>
          <span class="case-id">{case_id}</span>
        </div>
        <div class="case-flow" aria-label="What solving the task takes, in order, and the right outcome">
          {spine}
          <div class="case-out"><p class="out-label">Right outcome</p><div class="case-branches">{''.join(outcomes)}</div></div>
        </div>
        {trap_strip(case["trap"], view)}
        <div class="case-footer">
          <p>{escape(case["lesson"])}</p>
          <button class="scenario-text-button" type="button" data-open-task="{case_id}">Open task record {icon("arrow")}</button>
        </div>
      </article>"""


def type_picker(data, counts, first):
    by_family = {kind["family"]: kind for kind in data["types"]}
    groups = []
    for title, families in data["groups"]:
        cards = []
        for family in families:
            kind, case_id = by_family[family], by_family[family]["case"]["id"]
            n = counts[family]
            cards.append(f'<button class="type-card" type="button" data-case="{case_id}" aria-controls="case-{case_id}" '
                         f'aria-pressed="{str(case_id == first).lower()}"><span class="type-top">'
                         f'<span class="type-code">{escape(code_of(family))}</span><span class="type-count">{n} task{"s" if n != 1 else ""}</span></span>'
                         f'<strong>{escape(kind["name"])}</strong><small>{escape(kind["line"])}</small></button>')
        head = f'<p class="type-group-label">{escape(title)}</p>' if title else ""
        groups.append(f'<div class="type-group">{head}<div class="type-grid">{"".join(cards)}</div></div>')
    return f'<div class="type-picker" role="group" aria-label="Task types">{"".join(groups)}</div>'


def render(view, catalog, interface, recorded_tickets=()):
    data = SCENARIOS[view]
    family_of = {task["task_id"]: task["family"] for task in catalog["tasks"]}
    counts = {}
    for task in list(catalog["tasks"]) + list(catalog.get("generated", ())):
        counts[task["family"]] = counts.get(task["family"], 0) + 1
    # every type is a family of the data, every family has a type, and each representative belongs to its type
    assert sorted(kind["family"] for kind in data["types"]) == sorted(counts), (view, sorted(counts))
    assert sorted(f for _, group in data["groups"] for f in group) == sorted(counts), view
    for kind in data["types"]:
        assert family_of.get(kind["case"]["id"]) == kind["family"], (view, kind["case"]["id"])
    count = len(family_of) + len(catalog.get("generated", ()))
    action_count = len(interface["actions"])
    if view == "ticketing":
        world_stat = ("Held-out tasks", catalog["heldout"]["count"])
    elif view == "insurance":
        world_stat = ("Seats in the world", len(catalog["seats"]))
    else:
        world_stat = ("Products", catalog["catalogue"]["products"])
    stats = [("Public dev tasks", count), world_stat, ("Available actions" if view == "shopping" else "Scenario actions", action_count)]
    facts = ''.join(f'<div><dt>{label}</dt><dd>{value}</dd></div>' for label, value in stats)
    steps = ''.join(f'<li>{tile(*step, "journey-card")}</li>' for step in data["steps"])
    checks = ''.join(tile(*check, "score-card") for check in data["checks"])
    by_family = {kind["family"]: kind for kind in data["types"]}
    order = [by_family[f] for _, group in data["groups"] for f in group]
    first = order[0]["case"]["id"]
    picker = type_picker(data, counts, first)
    tickets = {ticket["seat_name"]: ticket for ticket in recorded_tickets}
    panels = '\n'.join(case_panel(kind, kind["case"], kind["case"]["id"] == first, tickets, view) for kind in order)
    return f"""
  <div class="scenario-hero">
    <div class="wrap">
      <div class="scenario-hero-grid">
        <div class="scenario-hero-copy">
          <span class="scenario-hero-icon">{icon(data["icon"])}</span>
          <h1>{escape(data["title"])}</h1>
          <p>{escape(data["intro"])}</p>
          <a class="scenario-cta" href="#{view}/cases">See the task types {icon("arrow")}</a>
        </div>
        <figure class="role-map">
          <figcaption>Who takes part</figcaption>
          {roles(view, catalog)}
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
        <h2>{escape(data["types_title"])}</h2>
        <p>{escape(data["types_intro"])}</p>
      </div>
      {picker}
{panels}
    </div>
  </section>
  <section class="scenario-section">
    <div class="wrap">
      <h2>What the benchmark checks</h2>
      <div class="scenario-scoring">{checks}</div>
    </div>
  </section>""".strip()
