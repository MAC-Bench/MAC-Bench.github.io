(function () {
  'use strict';

  var node = document.getElementById('data-tasks');
  if (!node) return;
  var T = JSON.parse(node.textContent);

  function byId(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function usd(c) { return (c < 0 ? '-' : '') + '$' + (Math.abs(c) / 100).toFixed(2); }
  function shortId(id) { return id.replace('tk-', '').toUpperCase(); }

  function careless(c) {
    if (!c || !c.name) return 'none for this task';
    var extra = [];
    if (c.acted_without_consent) extra.push('acts without consent ' + c.acted_without_consent + ' time' + (c.acted_without_consent > 1 ? 's' : ''));
    if (c.took_the_worse_path) extra.push('takes the worse path ' + c.took_the_worse_path + ' time' + (c.took_the_worse_path > 1 ? 's' : ''));
    return esc(c.name) + ': ' + (c.success ? 'succeeds' : 'fails') + (extra.length ? ', ' + extra.join(', ') : '');
  }

  function allCareless(t) {
    var all = [t.careless_agent].concat(t.other_careless_agents || []).filter(function (c) { return c && c.name; });
    return all.length ? all.map(careless).join('; ') : 'none for this task';
  }

  byId('t-rows').innerHTML = T.tasks.map(function (t) {
    return '<tr><td>' + esc(shortId(t.task_id)) + '</td><td>' + esc(t.family) + '</td><td>' + esc(t.title) +
      (t.paired_with ? '. Twin of ' + esc(shortId(t.paired_with)) : '') + '</td><td>' +
      usd(t.reference.total_loss_cents) + '</td><td>' + t.reference.process.calls + '</td><td>' +
      (t.idle.success ? 'succeeds: nothing needed doing' : 'fails') + '</td><td>' + allCareless(t) + '</td></tr>';
  }).join('');

  byId('t-gen-rows').innerHTML = T.generated.map(function (t) {
    return '<tr><td>' + esc(shortId(t.task_id)) + '</td><td>' + esc(t.family) + '</td><td>' + esc(t.title) +
      (t.paired_with ? '. Twin of ' + esc(shortId(t.paired_with)) : '') + '</td><td>' +
      usd(t.reference.loss_cents) + '</td><td>' + t.reference.calls + '</td><td>' +
      (t.leaving_succeeds ? 'succeeds: nothing needed doing' : 'fails') + '</td><td>' + careless(t.careless_agent) + '</td></tr>';
  }).join('');

  byId('t-foil-rows').innerHTML = T.careless_agents.map(function (a) {
    return '<tr><td>' + esc(a.name) + '</td><td>' + esc(a.lacks) + '</td><td>' + esc(a.families.join(', ')) + '</td></tr>';
  }).join('');

  var dropped = T.generated.reduce(function (n, t) { return n + t.dropped; }, 0);
  byId('t-sets').innerHTML = T.generated.length + ' tasks from a public seed, ' + T.per_family + ' per family; ' + dropped +
    ' candidates were dropped on the way. A held-out set of ' + T.heldout.count + ', ' + T.heldout.per_family +
    ' per family, comes from a seed that is not published. Its fingerprint is <code>' + esc(T.heldout.set_digest.slice(0, 16)) +
    '</code>&hellip; and is in the code repository, so the set can later be shown unchanged.';

  var PART = { cash_out: 'Money out', credit_received: 'Credit received, at their rate', stops: 'Connections', not_together: 'Not seated together' };

  function travellers(t) {
    return t.travelers.map(function (p) {
      var facts = Object.keys(p.facts).map(function (k) {
        return '<div><dt>' + esc(k) + '</dt><dd>' + esc(p.facts[k]) + '</dd></div>';
      }).join('');
      var plans = p.plans.map(function (i) {
        return '<li>' + i.at_minutes + ' minutes in: decides to ' + esc(i.kind) + (i.travel_date ? ' to ' + esc(i.travel_date) : '') +
          (i.latest_arrival_local ? ', landing by ' + esc(i.latest_arrival_local.replace('T', ' ')) : '') + '</li>';
      }).join('');
      return '<div class="stack"><h4 class="lbl">' + esc(p.name) + ' · ' + esc(p.seat) + '</h4><dl class="tfacts">' + facts + '</dl>' +
        '<ul class="plain-list">' + (plans || '<li>No change of plan.</li>') +
        '<li>Answers after ' + p.delay_minutes + ' minutes. ' +
        (p.attentive ? 'Reads what a quote says about a better path and refuses the worse one.' : 'Trusts the agent and does not look for a better path.') +
        '</li></ul></div>';
    }).join('');
  }

  function card(sc, label) {
    var checks = sc.checks.map(function (c) {
      return '<li class="' + (c.passed ? 'pass' : 'fail') + '">' + esc(c.name) + (c.seat ? ', ' + esc(c.seat) : '') +
        (c.detail ? ': ' + esc(c.detail) : '') + '</li>';
    }).join('');
    var rows = sc.travelers.map(function (p) {
      var parts = Object.keys(p.loss_parts).filter(function (k) { return p.loss_parts[k] !== 0; }).map(function (k) {
        return esc(PART[k] || k) + ' ' + usd(p.loss_parts[k]);
      }).join(', ');
      return '<tr><td>' + esc(p.seat) + '</td><td>' + (p.travelling ? 'ticket' : 'no ticket') + '</td><td>' + usd(p.spend_cents) +
        (p.budget_cents !== null ? ' of ' + usd(p.budget_cents) : '') + '</td><td>' + usd(p.loss_cents) + '</td><td>' + (parts || 'nothing') + '</td></tr>';
    }).join('');
    var pr = sc.process;
    var refused = Object.keys(pr.refused_by_code).map(function (k) { return pr.refused_by_code[k] + ' ' + k; }).join(', ');
    return '<div class="stack"><h4 class="lbl">' + esc(label) + ' · ' + (sc.success ? 'succeeds' : 'fails') + '</h4>' +
      '<ul class="checks">' + checks + '</ul>' +
      '<div class="tscroll"><table class="ft plain"><thead><tr><th>Traveller</th><th>Ends with</th><th>Spent</th><th>Loss</th><th>Made of</th></tr></thead><tbody>' +
      rows + '</tbody></table></div>' +
      '<p class="note">Total loss ' + usd(sc.total_loss_cents) +
      (sc.regret_cents !== null && sc.regret_cents !== undefined ? ', ' + usd(sc.regret_cents) + ' above the reference' : '') + '. ' +
      pr.calls + ' calls, ' + pr.refused + ' refused' + (refused ? ' (' + esc(refused) + ')' : '') + ', ' + pr.messages_sent + ' messages, ' +
      pr.world_minutes + ' world minutes. Acted without consent: ' + pr.acted_without_consent + '. Took the worse path: ' + pr.took_the_worse_path + '.</p></div>';
  }

  function booked(t) {
    var name = {};
    t.travelers.forEach(function (p) { name[p.seat] = p.name; });
    if (!t.booked || !t.booked.length) return '<li>Before the episode: nothing is booked.</li>';
    return t.booked.map(function (b) {
      var who = b.seats.map(function (s) { return esc(name[s] || s); }).join(' and ');
      var bags = b.bags.map(function (n, i) { return n ? esc(name[b.seats[i]] || b.seats[i]) + ' with ' + n + ' checked bag' + (n > 1 ? 's' : '') : ''; })
        .filter(Boolean).join(', ');
      return '<li>Before the episode: ' + who + (b.seats.length > 1 ? ' were ticketed on one order' : ' was ticketed on an order of their own') +
        ', ' + esc(b.flight_numbers.join(' + ')) + ' from ' + esc(b.origin) + ' to ' + esc(b.destination) + ' on ' + esc(b.date) +
        ', ' + esc(b.brand) + ' fare' + (b.together ? ', seated side by side' : '') + (bags ? '; ' + bags : '') + '.</li>';
    }).join('');
  }

  function checksOnTheTask(t) {
    var lines = [];
    var all = [t.careless_agent].concat(t.other_careless_agents || []).filter(function (c) { return c && c.name; });
    if (all.length) lines.push('<li>Careless agents the task was admitted against: ' + all.map(careless).join('; ') + '.</li>');
    if (t.baseline) {
      lines.push('<li>A lawful policy that finishes the job, <b>' + esc(t.baseline.name) + '</b>: ' + (t.baseline.success ? 'solves it' : 'fails') +
        (t.baseline.regret_cents !== null && t.baseline.regret_cents !== undefined ? ', ' + usd(t.baseline.regret_cents) + ' above the reference' : '') +
        ', takes the worse path ' + t.baseline.took_the_worse_path + ' time' + (t.baseline.took_the_worse_path === 1 ? '' : 's') + '.</li>');
    }
    return lines.length ? '<ul class="plain-list" style="margin:14px 0 0">' + lines.join('') + '</ul>' : '';
  }

  function steps(t) {
    if (!t.reference_steps || !t.reference_steps.length) return '';
    var began = Date.parse(t.reference_steps[0].t);
    var text = t.reference_steps.map(function (e) {
      var min = Math.round((Date.parse(e.t) - began) / 6000) / 10;
      var m = String(min.toFixed(1));
      return ('      ' + m).slice(-6) + ' min  ' + e.action + (e.ok ? '' : '   refused: ' + e.error);
    }).join('\n');
    return '<details class="tcard"><summary>What the reference policy called, in order: ' + t.reference_steps.length +
      ' calls</summary><pre class="json">' + esc(text) + '</pre></details>';
  }

  function render(i) {
    var t = T.tasks[i];
    var airline = t.airline.map(function (d) {
      return '<li>' + d.at_minutes + ' minutes in: ' + esc(d.flight_id.replace('flt_', '').replace(/_.*/, '')) + ' ' +
        (d.kind === 'cancellation' ? 'is cancelled' : 'moves by ' + d.shift_minutes + ' minutes') + ' (' + esc(d.cause) + ')</li>';
    }).join('');
    var knobs = Object.keys(t.axes).map(function (k) {
      return '<span class="chip"><i></i>' + esc(k) + ': ' + esc(t.axes[k]) + '</span>';
    }).join('');
    byId('t-detail').innerHTML =
      '<h3 style="margin:22px 0 6px">' + esc(shortId(t.task_id)) + ' · ' + esc(t.title) + '</h3>' +
      '<p style="max-width:78ch"><b>The agent is told:</b> ' + esc(t.brief) + '</p>' +
      '<p style="max-width:78ch"><b>What it is there to find out:</b> ' + esc(t.tests) + '</p>' +
      (t.paired_with ? '<p style="max-width:78ch"><b>Twin of ' + esc(shortId(t.paired_with)) + ':</b> the same task with one thing changed. What an agent does differently on the two is what that one thing does to it.</p>' : '') +
      '<div class="chips" style="display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 20px">' + knobs + '</div>' +
      '<h4 class="lbl" style="margin-bottom:10px">Hidden from the agent</h4>' +
      '<div class="two-col">' + travellers(t) + '</div>' +
      '<ul class="plain-list" style="margin:14px 0 24px">' +
      booked(t) +
      (airline || '<li>The airline changes nothing.</li>') +
      '<li>The world is as of ' + esc(t.world_now.replace('T', ' ').replace(':00Z', ' UTC')) + ' and is watched for ' + t.observation_minutes + ' minutes.</li></ul>' +
      card(t.reference, 'The reference policy') +
      '<div style="height:18px"></div>' + card(t.idle, 'An agent that leaves at once') +
      checksOnTheTask(t) + steps(t) +
      '<details class="tcard"><summary>The agent\'s role card, as it is given</summary><pre class="json">' + esc(t.agent_card) + '</pre></details>' +
      Object.keys(t.traveller_cards).map(function (seat) {
        return '<details class="tcard"><summary>Role card of ' + esc(seat) + '</summary><pre class="json">' + esc(t.traveller_cards[seat]) + '</pre></details>';
      }).join('');
  }

  var pick = byId('t-pick');
  function choose(i) {
    pick.innerHTML = T.tasks.map(function (t, n) {
      return '<button type="button" data-task="' + n + '" aria-pressed="' + (n === i) + '">' + esc(shortId(t.task_id)) + '</button>';
    }).join('');
    render(i);
  }
  pick.addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('button[data-task]') : null;
    if (b) choose(Number(b.getAttribute('data-task')));
  });
  choose(0);

  /* another part of the page asks for a task by its id: show it and bring it into view */
  document.addEventListener('mb-task', function (ev) {
    var n = T.tasks.map(function (t) { return t.task_id; }).indexOf(ev.detail);
    if (n < 0) return;
    choose(n);
    var top = byId('t-pick');
    if (top && top.scrollIntoView) top.scrollIntoView({ block: 'start' });
  });
})();
