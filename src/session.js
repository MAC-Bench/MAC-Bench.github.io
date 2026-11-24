(function () {
  'use strict';

  var node = document.getElementById('data-session');
  if (!node) return;
  var S = JSON.parse(node.textContent);

  function byId(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function pretty(v) { return esc(JSON.stringify(v, null, 2)); }
  function span(sec) {
    var m = Math.floor(sec / 60), s = sec % 60;
    return (m ? m + ' min ' : '') + (s || !m ? s + ' s' : '');
  }

  var m = S.meta;
  byId('s-meta').innerHTML =
    'Recorded by the kernel on the dev world, ' + esc(m.start.slice(11, 16)) + ' to ' + esc(m.end.slice(11, 16)) + ' UTC world time. One live seat, <code>' +
    esc(m.live_seat) + '</code>. ' + m.scripted_seats.map(function (s) { return '<code>' + esc(s) + '</code>'; }).join(' and ') +
    ' are scripted and only answer typed questions. ' + m.entries + ' log entries, ' + m.writes + ' commits. Sealed log head <code>' + esc(m.head) + '</code>. ' +
    (m.replay_ok ? 'Replayed from the log into a fresh world: identical log and final state.'
                 : 'Replay from the log did NOT reproduce the session.');

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
})();
