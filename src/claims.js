(function () {
  'use strict';

  var node = document.getElementById('data-claims');
  if (!node) return;
  var C = JSON.parse(node.textContent);

  function byId(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function usd(c) {
    return (c < 0 ? '-' : '') + '$' + (Math.abs(c) / 100).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
  function code(s) { return '<code>' + esc(s) + '</code>'; }
  function words(s) { return String(s).replace(/_/g, ' '); }
  function shortId(id) { return id.replace('ic-', '').toUpperCase(); }
  function span(sec) {
    if (sec < 60) return sec + ' s';
    if (sec < 3600) return Math.round(sec / 60) + ' min';
    return (sec / 3600) + ' h';
  }
  function yes(v) { return v ? 'yes' : 'no'; }
  // The details of a check are written for a log: amounts in cents, items as a mapping. Shown here in dollars.
  function detail(text) {
    if (!text) return '';
    if (text.indexOf('determination') >= 0) return esc(text);
    return esc(text.replace(/[{}']/g, '').replace(/(\w+): (-?\d+)/g, '$1 $2')
      .replace(/(-?)\b(\d{3,})\b( cents)?/g, function (m, sign, n) { return sign + usd(Number(n)); }));
  }

  var SEATS = C.seats.map(function (s) { return s.seat; });
  var DRIVERS = SEATS.filter(function (s) { return s.indexOf('driver') === 0; });
  var WANTS = {
    policyholder: 'The car repaired, and what the rules give them, with as little out of pocket as the rules allow.',
    adjuster: 'To handle every claim on its insurer as the claims manual and the State\'s rules say: pay what is owed, no more and no less, in time.'
  };
  var ABOUT = { outcome: 'the outcome', work: 'the work' };
  var FROM = { rules: 'the State\'s rules and the policy', manual: 'the insurer\'s manual' };
  var PART = {
    paid_but_not_owed: 'paid but not owed', owed_but_not_paid: 'owed but not paid', not_recovered: 'not recovered', forum_fees: 'forum fees',
    out_of_pocket: 'out of pocket', unrepaired_damage: 'damage never repaired',
    of_which_owed_to_them_and_not_received: 'of which owed to them and not received'
  };
  var DOCS = {
    auto_policy: 'The policy form', claims_rules: 'The State\'s claims rules', fault_law: 'The law on fault', liability_guide: 'The liability guide',
    forum_rules: 'The forum\'s rules', claims_manual: 'The insurer\'s claims manual', claimant_guide: 'A guide for claimants'
  };

  // ---------------------------------------------------------------- head, seats, modules
  byId('ic-version').textContent = C.interface_version;
  byId('ic-n-actions').textContent = C.actions.length;
  byId('ic-n-tasks').textContent = C.tasks.length;
  byId('ic-n-tests').textContent = C.tests;

  byId('ic-seats').innerHTML = C.seats.map(function (s) {
    var who = s.role === 'policyholder' ? esc(s.who) + ', insured with ' + esc(s['with']) : 'The ' + esc(s.who) + '. Its insured is ' + esc(s['with']);
    return '<tr><td>' + esc(s.seat) + '</td><td>' + (s.role === 'policyholder' ? 'driver' : 'claims adjuster') + '</td><td>' + who +
      '</td><td>' + WANTS[s.role] + '</td></tr>';
  }).join('');

  var lines = 0;
  byId('ic-modules').innerHTML = C.modules.map(function (g) {
    return '<tr class="grp"><th colspan="3">' + esc(g.group) + '</th></tr>' + g.items.map(function (m) {
      lines += m.lines;
      return '<tr><td>' + esc(m.path.replace('src/macbench/', '')) + '</td><td>' + m.lines + '</td><td>' + esc(m.does) + '</td></tr>';
    }).join('');
  }).join('');
  byId('ic-modules-note').textContent = 'Paths are under src/macbench/ unless they start with tools/. ' + lines +
    ' lines in all, counted when the page was built. The kernel, the board, the server, the client and the runner are the ones ticketing uses.';

  // ---------------------------------------------------------------- tasks
  function lossOf(t, seat) {
    var r = t.reference[seat];
    var parts = Object.keys(r.loss_parts).map(function (k) { return PART[k] || words(k); }).join(', ');
    return usd(r.loss_cents) + (r.loss_cents ? ' ' + parts : '');
  }
  function underTest(t) {
    return t.focal.length === SEATS.length ? 'all four seats' : t.focal.map(esc).join(', ');
  }

  byId('ic-task-rows').innerHTML = C.tasks.map(function (t) {
    var book = t.focal.length === 1 ? lossOf(t, t.focal[0]) :
      t.focal.map(function (s) { return esc(s) + ' ' + usd(t.reference[s].loss_cents); }).join(', ');
    var foils = t.careless.map(function (c) {
      return esc(c.manner) + ': ' + usd(c.regret_cents) + (c.met_outcome ? ', the outcome is right and a step of the work is skipped' : '');
    });
    if (!foils.length) {
      foils = [t.focal.length === 1 ? 'no manner for a driver; doing nothing fails, ' + usd(t.doing_nothing[t.focal[0]].regret_cents) :
        'none; all four doing nothing fails'];
    }
    return '<tr><td>' + esc(shortId(t.task_id)) + '</td><td>' + underTest(t) + '</td><td>' + esc(t.title) +
      (t.paired_with ? '. Twin of ' + esc(shortId(t.paired_with)) : '') + '</td><td>' + t.observation_days + ' days</td><td>' +
      DRIVERS.map(function (d) { return t.fault_percent[d]; }).join(' / ') + '</td><td>' + book + '</td><td>' + foils.join('; ') + '</td></tr>';
  }).join('');

  function accident(t) {
    var a = t.accident;
    var guide = C.guide.filter(function (g) { return g.kind === a.kind; })[0] || { shifts: [] };
    var said = {};
    guide.shifts.forEach(function (s) { said[s.fact] = s.says; });
    var facts = Object.keys(a.facts).map(function (k) {
      return '<div><dt>' + esc(k) + '</dt><dd>' + yes(a.facts[k]) + (said[k] ? ' <span class="dim">· ' + esc(said[k]) + '</span>' : '') + '</dd></div>';
    }).join('');
    var evidence = a.evidence.map(function (e) {
      var shows = Object.keys(e.shows).map(function (k) { return esc(k) + ': ' + yes(e.shows[k]); }).join(', ');
      return '<li><b>' + esc(words(e.kind)) + '</b>, held by ' + esc(e.held_by) +
        (e.ready_after_days ? ', to be had ' + e.ready_after_days + ' days after the accident' : '') + '. ' + esc(e.summary) +
        (shows ? ' <span class="dim">Shows ' + shows + '.</span>' : ' <span class="dim">Speaks to none of the guide\'s facts.</span>') + '</li>';
    }).join('');
    return '<div class="stack"><h4 class="lbl">The accident · ' + esc(words(a.kind)) + '</h4>' +
      '<p style="font-size:14.5px">' + esc(a.place) + ', ' + esc(a.happened_at.slice(0, 10)) + '. The watch starts ' + esc(a.starts_at.slice(0, 10)) +
      ' and lasts ' + t.observation_days + ' days.</p>' +
      '<p class="lbl" style="margin-top:6px">What happened, known to the drivers and to the score</p><dl class="tfacts">' + facts + '</dl>' +
      '<p class="lbl" style="margin-top:6px">Evidence that exists</p><ul class="plain-list">' + evidence + '</ul></div>';
  }

  function driver(t, seat) {
    var d = t.drivers[seat], p = d.policy, m = d.damage;
    var lies = Object.keys(d.says).filter(function (k) { return d.says[k] !== t.accident.facts[k]; });
    var where = d.claims_with.map(function (w) { return w === 'own_insurer' ? 'their own insurer' : 'the other driver\'s insurer'; }).join(' and ');
    var rows = [
      ['in the accident', esc(d.role) + ', ' + esc(d.car)],
      ['insurer', esc(d.carrier) + (p.cancelled_on ? ' · policy cancelled on ' + esc(p.cancelled_on) : '')],
      ['property damage limit', usd(p.property_damage_limit_cents)],
      ['collision', p.collision_deductible_cents === null ? 'not bought' : 'deductible ' + usd(p.collision_deductible_cents)],
      ['rental reimbursement', p.rental_daily_limit_cents === null ? 'not bought' :
        usd(p.rental_daily_limit_cents) + ' a day, ' + usd(p.rental_total_limit_cents) + ' in all'],
      ['the shop writes', usd(m.written_by_the_shop_cents) + ' in ' + m.lines + ' lines' +
        (m.found_at_teardown_cents ? ', ' + usd(m.found_at_teardown_cents) + ' of it as a supplement' : '')],
      ['from this accident', usd(m.from_this_accident_cents) +
        (m.written_by_the_shop_cents !== m.from_this_accident_cents ? ' · ' + usd(m.written_by_the_shop_cents - m.from_this_accident_cents) + ' was there before' : '')],
      ['repair takes', m.repair_days + ' days from the go-ahead']
    ];
    if (t.focal.indexOf(seat) < 0) {
      rows.push(['as a script, claims with', where]);
      rows.push(['as a script, says', lies.length ? 'against what happened: ' + lies.map(function (k) { return esc(k) + ' ' + yes(d.says[k]); }).join(', ') : 'what happened']);
      if (d.withholds.length) rows.push(['as a script, keeps back', esc(d.withholds.join(', '))]);
    }
    return '<div class="stack"><h4 class="lbl">' + esc(d.name) + ' · ' + esc(seat) + '</h4><dl class="tfacts">' +
      rows.map(function (r) { return '<div><dt>' + r[0] + '</dt><dd>' + r[1] + '</dd></div>'; }).join('') + '</dl></div>';
  }

  function failed(r) {
    return r.failed.map(function (f) {
      return '<li class="fail">' + esc(f.name) + (f.kind === 'work' ? ' <span class="dim">(work)</span>' : '') +
        (f.detail ? ': ' + detail(f.detail) : '') + '</li>';
    }).join('');
  }

  function yardstick(t) {
    var rows = SEATS.map(function (s) {
      var r = t.reference[s], focal = t.focal.indexOf(s) >= 0;
      var by = focal ? '<b>under test</b>; by the book in this run' :
        (s.indexOf('driver') === 0 ? 'script' : 'script, ' + esc(t.desks[s].manner));
      var req = r.success ? 'all ' + r.checks + ' met' :
        'not met: ' + r.failed.map(function (f) { return esc(f.name); }).join('; ');
      var parts = Object.keys(r.loss_parts).map(function (k) { return esc(PART[k] || words(k)) + ' ' + usd(r.loss_parts[k]); }).join(', ');
      return '<tr><td>' + esc(s) + '</td><td>' + by + '</td><td>' + req + '</td><td>' + usd(r.loss_cents) + '</td><td>' + (parts || 'nothing') + '</td></tr>';
    }).join('');
    return '<div class="stack"><h4 class="lbl">What the yardstick run ends with</h4>' +
      '<div class="tscroll"><table class="ft plain mono1"><thead><tr><th>Seat</th><th>Played by</th><th>Requirements</th><th>Loss</th><th>Made of</th></tr></thead><tbody>' +
      rows + '</tbody></table></div>' +
      '<p class="note">A scripted seat that departs from the rules, because the task has it so, fails its own requirements here. That is no fault of the seat under test.</p></div>';
  }

  function admission(t) {
    var idle = t.focal.map(function (s) {
      var r = t.doing_nothing[s];
      return '<div class="stack"><p style="font-size:14.5px"><b>' + esc(s) + ' hands back control at once.</b> ' +
        (r.failed.length ? r.failed.length + ' requirements not met' : 'Nothing was asked of it, since nobody reported a claim') +
        ', ' + usd(r.regret_cents) + ' above the yardstick.</p><ul class="checks">' + failed(r) + '</ul></div>';
    }).join('');
    var foils = t.careless.map(function (c) {
      return '<div class="stack"><p style="font-size:14.5px"><b>' + esc(c.seat) + ' plays "' + esc(c.manner) + '".</b> ' + esc(c.does) + ' ' +
        usd(c.regret_cents) + ' above the yardstick' + (c.met_outcome ? ': every outcome is right, and the task is still failed on the work.' : '.') +
        '</p><ul class="checks">' + failed(c) + '</ul></div>';
    }).join('');
    return '<div class="stack"><h4 class="lbl">Runs that have to fail it</h4>' + foils + idle +
      (t.focal.length > 1 ? '<p class="note">A joint task: the four seats succeed or fail together.</p>' : '') + '</div>';
  }

  function cards(t) {
    return t.focal.map(function (s) {
      return '<details class="tcard"><summary>The card ' + esc(s) + ' is given</summary><pre class="json">' + esc(t.cards[s]) + '</pre></details>';
    }).join('');
  }

  var lane = 'all';
  function timeline(t) {
    var day = -1, shown = 0;
    var rows = t.timeline.map(function (r) {
      var concerns = r.who === 'world' ? r['for'] : r.who;
      if (lane !== 'all' && r.who !== lane && concerns !== lane) return '';
      shown += 1;
      var head = '';
      if (Math.floor(r.d) !== day) {
        day = Math.floor(r.d);
        head = '<div class="tl-day">Day ' + day + '</div>';
      }
      var cls = r.who === 'world' ? ' world' : (t.focal.indexOf(r.who) >= 0 ? ' focal' : ' scripted');
      var who = r.who === 'world' ? 'world' + (r['for'] ? ' → ' + r['for'] : '') : r.who;
      return head + '<div class="sx' + cls + '"><div class="sx-row tl"><span class="t">' + r.d.toFixed(2) + '</span><span class="who">' + esc(who) +
        '</span><span class="act">' + esc(r.who === 'world' ? words(r.a) : r.a) + '</span><span class="sum">' +
        (r.refused ? '<b>' + esc(r.refused) + '</b> ' : '') + esc(r.s) + '</span></div></div>';
    }).join('');
    var buttons = ['all'].concat(SEATS).map(function (s) {
      return '<button type="button" data-lane="' + s + '" aria-pressed="' + (s === lane) + '">' + (s === 'all' ? 'Everyone' : esc(s)) + '</button>';
    }).join('');
    return '<div class="stack"><h4 class="lbl">The yardstick run, day by day</h4>' +
      '<p style="font-size:14.5px;max-width:78ch">Every call that changes the world and every event of the world\'s own parties, with the day of the watch it happened on. Reads are left out. All four seats are scripted in this run; the seat under test is marked.</p>' +
      '<div class="seg" role="group" aria-label="Seat">' + buttons + '</div>' +
      '<p class="note">' + shown + ' of ' + t.timeline.length + ' rows.</p><div class="sess">' + rows + '</div></div>';
  }

  var current = 0;
  function show() {
    var t = C.tasks[current];
    byId('ic-pick').innerHTML = C.tasks.map(function (x, n) {
      return '<button type="button" data-task="' + n + '" aria-pressed="' + (n === current) + '">' + esc(shortId(x.task_id)) + '</button>';
    }).join('');
    var knobs = Object.keys(t.axes).map(function (k) {
      return '<div><dt>' + esc(k) + '</dt><dd>' + esc(t.axes[k]) + '</dd></div>';
    }).join('');
    byId('ic-detail').innerHTML =
      '<div class="stack"><h3>' + esc(shortId(t.task_id)) + ' · ' + esc(t.title) + '</h3>' +
      '<p style="max-width:82ch">' + esc(t.tests) + '</p>' +
      '<p class="note">' + esc(t.family) + ' · under test: ' + underTest(t) + ' · fingerprint ' + code(t.task_sha256.slice(0, 16)) + '</p></div>' +
      '<div class="two-col"><div class="stack"><h4 class="lbl">Knobs</h4><dl class="tfacts">' + knobs + '</dl></div>' + accident(t) + '</div>' +
      '<div class="two-col">' + DRIVERS.map(function (d) { return driver(t, d); }).join('') + '</div>' +
      yardstick(t) + admission(t) + '<div>' + cards(t) + '</div>' + timeline(t);
  }
  byId('ic-pick').addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('button[data-task]') : null;
    if (b) { current = Number(b.getAttribute('data-task')); lane = 'all'; show(); }
  });
  byId('ic-detail').addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('button[data-lane]') : null;
    if (b) { lane = b.getAttribute('data-lane'); show(); }
  });
  document.addEventListener('mb-task', function (ev) {
    var n = C.tasks.map(function (t) { return t.task_id; }).indexOf(ev.detail);
    if (n < 0) return;
    byId('insurance-records').open = true;
    current = n;
    lane = 'all';
    show();
    var top = byId('ic-pick');
    top.scrollIntoView({ block: 'start' });
    top.querySelector('button[aria-pressed="true"]').focus({ preventScroll: true });
  });
  show();

  // ---------------------------------------------------------------- scoring
  ['adjuster', 'driver'].forEach(function (role) {
    byId('ic-checks-' + role).innerHTML = C.checks[role].map(function (c) {
      return '<tr><td>' + esc(c.name) + '</td><td>' + ABOUT[c.kind] + '</td><td>' + FROM[c.source] + '</td></tr>';
    }).join('');
  });

  // ---------------------------------------------------------------- rules
  byId('ic-clocks').innerHTML = C.clocks.map(function (c) {
    return '<tr><td>' + esc(c.what) + '</td><td>' + c.days + '</td><td>' + esc(c.counted) + '</td><td>' + esc(c.scored) + '</td></tr>';
  }).join('');
  byId('ic-money').innerHTML = '<b>The forum</b> has to be used for disputes of up to ' + usd(C.money.arbitration_limit_cents) +
    ' paid. Filing costs ' + usd(C.money.arbitration_fee_cents) + ', borne by the insurer that files. Two amounts within ' +
    usd(C.money.tolerance_cents) + ' of each other count as the same.';
  byId('ic-guide').innerHTML = C.guide.map(function (g) {
    var split = function (s) { return s[0] + ' / ' + s[1]; };
    var shifts = g.together.map(function (x) {
      return '<li>' + esc(x.says) + ' <b>' + split(x.split) + '</b> <span class="dim">· ' + x.facts.map(esc).join(' and ') + ', read first</span></li>';
    }).concat(g.shifts.map(function (s) {
      return '<li>' + esc(s.says) + ' <b>' + split(s.split) + '</b> <span class="dim">· ' + esc(s.fact) + ', counts against the ' + esc(s.burdens) + '</span></li>';
    })).join('');
    return '<tr><td>' + esc(words(g.kind)) + '</td><td>' + esc(g.roles.join(' / ')) + '</td><td><b>' +
      (g.base[0] + g.base[1] ? split(g.base) : 'nothing proven') + '</b><br><span class="dim">' + esc(g.rule) + '</span></td><td>' +
      (shifts ? '<ol class="plain-list">' + shifts + '</ol>' : 'none') + '</td></tr>';
  }).join('');
  byId('ic-handbook').innerHTML = C.handbook.map(function (h) {
    return '<tr><td>' + esc(h.document) + '</td><td>' + h.passages + '</td><td>' + esc(DOCS[h.document] || '') + '. ' +
      (h.adjusters_only ? 'Adjusters only.' : (h.document === 'claimant_guide' ? 'Both roles. Written for drivers.' : 'Both roles.')) + '</td></tr>';
  }).join('');

  // ---------------------------------------------------------------- interface, scripted seats
  var role = C.roles[0].name;
  function actions() {
    var r = C.roles.filter(function (x) { return x.name === role; })[0];
    byId('ic-roles').innerHTML = C.roles.map(function (x) {
      return '<button type="button" data-role="' + esc(x.name) + '" aria-pressed="' + (x.name === role) + '">' + esc(x.title) + ' · ' + x.actions.length + '</button>';
    }).join('');
    byId('ic-role-note').textContent = r.description + ' Seats: ' + r.seats.join(', ') + '.';
    var group = null;
    byId('ic-actions').innerHTML = C.actions.filter(function (a) { return a.roles.indexOf(role) >= 0; }).map(function (a) {
      var head = '';
      if (a.group !== group) {
        group = a.group;
        head = '<tr class="grp"><th colspan="5">' + esc(group) + '</th></tr>';
      }
      return head + '<tr><td>' + esc(a.name) + '</td><td><span class="eff e-' + esc(a.effect) + '">' + esc(a.effect) + '</span></td><td>' + span(a.time_cost_s) +
        '</td><td>' + esc(a.summary) + (a.description ? ' <span class="dim">' + esc(a.description) + '</span>' : '') + '</td><td class="errs">' +
        (a.errors.length ? a.errors.map(esc).join(', ') : '<span class="dim">common errors only</span>') + '</td></tr>';
    }).join('');
  }
  byId('ic-roles').addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('button[data-role]') : null;
    if (b) { role = b.getAttribute('data-role'); actions(); }
  });
  actions();
  byId('ic-facts').innerHTML = Object.keys(C.fact_keys).map(function (k) {
    return '<dt>' + esc(k) + '</dt><dd>' + esc(C.fact_keys[k]) + '</dd>';
  }).join('');

  var foilOf = {}, counterpartOf = {};
  C.tasks.forEach(function (t) {
    t.careless.forEach(function (c) { (foilOf[c.manner] = foilOf[c.manner] || []).push(shortId(t.task_id)); });
    Object.keys(t.desks).forEach(function (s) {
      var m = t.desks[s].manner;
      if (t.focal.indexOf(s) < 0 && m !== 'by the book') (counterpartOf[m] = counterpartOf[m] || []).push(shortId(t.task_id));
    });
  });
  byId('ic-manners').innerHTML = C.manners.map(function (m) {
    var used = [];
    if (m.name === 'by the book') used.push('every scripted desk unless a task says otherwise, and the yardstick run');
    if (counterpartOf[m.name]) used.push('the counterpart in ' + counterpartOf[m.name].join(', '));
    if (foilOf[m.name]) used.push('has to fail ' + foilOf[m.name].join(', '));
    return '<tr><td>' + esc(m.name) + '</td><td>' + esc(m.does) + '</td><td>' + (used.join('; ') || '<span class="dim">no task yet</span>') + '</td></tr>';
  }).join('');

  // ---------------------------------------------------------------- calibration
  function amount(v, unit) {
    var n = String(unit === 'dollars' ? Math.round(v) : Math.round(v * 10) / 10).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return unit === 'dollars' ? '$' + n : n + (unit === 'percent' ? '%' : ' ' + unit);
  }
  byId('ic-calibration').innerHTML = C.calibration.map(function (b) {
    var band = (b.least === null ? 'no floor' : 'from ' + amount(b.least, b.unit)) + (b.most === null ? ', no ceiling' : ' to ' + amount(b.most, b.unit));
    var values = b.task_set.length > 5 ? amount(b.task_set[0], b.unit) + ' to ' + amount(b.task_set[b.task_set.length - 1], b.unit) + ', ' + b.task_set.length + ' values' :
      b.task_set.map(function (v) { return amount(v, b.unit); }).join(', ');
    return '<tr><td>' + esc(b.quantity.replace(/, (dollars|days|percent)$/, '')) + '</td><td>' + amount(b.published, b.unit) + ' <span class="dim">' + esc(b.year) + '</span></td><td>' +
      '<a href="' + esc(b.url) + '">' + esc(b.source) + '</a></td><td>' + band +
      '</td><td>' + (values || '<span class="dim">none in the set</span>') + '</td></tr>';
  }).join('');
})();
