(function () {
  'use strict';

  var node = document.getElementById('data-session');
  if (!node) return;
  var ALL = JSON.parse(node.textContent);
  var LABELS = ['Booking', 'After booking'];

  function byId(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function pretty(v) { return esc(JSON.stringify(v, null, 2)); }
  function span(sec) {
    var m = Math.floor(sec / 60), s = sec % 60;
    return (m ? m + ' min ' : '') + (s || !m ? s + ' s' : '');
  }

  function usd(c) { return '$' + (c / 100).toFixed(2); }
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function when(local) { return Number(local.slice(8, 10)) + ' ' + MON[Number(local.slice(5, 7)) - 1] + ' ' + local.slice(11); }
  function codes(list) { return list.map(function (s) { return '<code>' + esc(s) + '</code>'; }).join(', '); }

  function render(S) {
  var m = S.meta;
  byId('s-title').textContent = m.title;
  byId('s-story').textContent = m.story;
  byId('s-meta').innerHTML =
    'World time ' + esc(m.start.slice(5, 10)) + ' ' + esc(m.start.slice(11, 16)) + ' to ' + esc(m.end.slice(11, 16)) + ' UTC. ' +
    (m.scripted_seats.length
      ? 'Live: ' + codes(m.live_seats) + '. Scripted: ' + codes(m.scripted_seats) + ', which react to typed attachments only. '
      : 'All three seats are live and played by one fixed script: ' + codes(m.live_seats) + '. ') +
    m.entries + ' log entries, ' + m.writes + ' commits. Sealed log head <code>' + esc(m.head) + '</code>. ' +
    (m.replay_ok ? 'Replayed from the log into a fresh world: identical log and final state.'
                 : 'Replay from the log did NOT reproduce the session.');

  byId('s-tickets').innerHTML = (S.tickets || []).map(function (t) {
    return '<div class="stub live"><div class="stub-main"><p class="lbl">' + esc(t.name) + ' · ' + esc(t.fare) + ' fare</p>' +
      '<p class="stub-title">' + esc(t.from) + ' <span class="to" aria-hidden="true"></span> ' + esc(t.to) + '</p><dl>' +
      '<div><dt>Flight</dt><dd>' + esc(t.flight) + '</dd></div>' +
      '<div><dt>Departs</dt><dd>' + esc(when(t.departs)) + '</dd></div>' +
      '<div><dt>Arrives</dt><dd>' + esc(when(t.arrives)) + '</dd></div>' +
      '<div><dt>Seat</dt><dd>' + esc(t.seat || 'none') + '</dd></div>' +
      '<div><dt>Bags</dt><dd>' + t.bags + '</dd></div>' +
      '<div><dt>Reference</dt><dd>' + esc(t.reference) + '</dd></div>' +
      '<div><dt>Ticket</dt><dd>' + esc(t.ticket) + '</dd></div></dl></div>' +
      '<div class="stub-side"><p class="lbl">Charged</p><p class="state">' + usd(t.charged_cents) + '</p>' +
      (t.budget_cents ? '<p class="lbl">Budget ' + usd(t.budget_cents) + '</p>' : '') + '</div></div>';
  }).join('');
  byId('s-proposals').innerHTML = (S.proposals || []).map(function (p) {
    var who = p.responses.map(function (r) {
      return esc(r.seat) + ' ' + esc(r.decision) + 'ed' + (r.reason ? ' (' + esc(r.reason) + ')' : '');
    }).join(', ');
    return '<code>' + esc(p.id) + '</code> ' + esc(p.status) + (who ? ': ' + who : '') + '.';
  }).concat((S.outcomes || []).map(function (line) { return esc(line) + '.'; })).join(' ');

  byId('s-list').innerHTML = S.entries.map(function (e) {
    var time = '<span class="t">' + esc(e.t.slice(11, 19)) + '</span>';
    if (e.type !== 'call') {
      return '<div class="sx world"><div class="sx-row">' + time + '<span class="who">world</span><span class="act">' +
        esc(e.type === 'event' ? 'event' : e.type) + '</span><span class="sum">' + esc(e.summary) + '</span><span class="cost"></span></div></div>';
    }
    var scripted = e.by === 'controller';
    var cost = e.cost_s ? '<span class="cost' + (e.cost_s >= 300 ? ' jump' : '') + '">+' + span(e.cost_s) + '</span>' : '<span class="cost">+0 s</span>';
    var body = '<div class="sx-body"><div><h4 class="lbl">Payload</h4><pre class="json">' + pretty(e.payload) + '</pre></div>' +
      (e.result ? '<div><h4 class="lbl">' + (e.ok ? 'Result, long lists shortened' : 'Error') + '</h4><pre class="json">' + pretty(e.result) + '</pre></div>' : '') +
      '<p class="note">Commit sequence after this call: ' + e.seq + '. ' +
      (scripted ? 'Made by a scripted seat inside an event, so it costs no world time.' : '') + '</p></div>';
    return '<details class="sx' + (scripted ? ' scripted' : '') + (e.ok ? '' : ' fail') + '"><summary class="sx-row">' + time +
      '<span class="who">' + esc(e.seat) + '</span><span class="act">' + esc(e.action) + '</span><span class="sum">' +
      (e.ok ? '' : '<b>' + esc(e.error) + '</b> ') + esc(e.summary) + '</span>' + cost + '</summary>' + body + '</details>';
  }).join('');
  }

  var pick = byId('s-pick');
  function choose(i) {
    pick.innerHTML = ALL.map(function (S, n) {
      return '<button type="button" data-session="' + n + '" aria-pressed="' + (n === i) + '">' + esc(LABELS[n] || S.meta.title) + '</button>';
    }).join('');
    render(ALL[i]);
  }
  pick.addEventListener('click', function (ev) {
    var b = ev.target.closest ? ev.target.closest('button[data-session]') : null;
    if (b) choose(Number(b.getAttribute('data-session')));
  });
  choose(0);
})();
