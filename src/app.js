(function () {
  'use strict';

  var TK = JSON.parse(document.getElementById('data-ticketing').textContent);
  var PG = JSON.parse(document.getElementById('data-progress').textContent);
  var VIEWS = ['overview', 'ticketing', 'insurance', 'multiagent', 'shopping', 'progress'];

  function byId(id) { return document.getElementById(id); }
  function all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function rich(s) { return esc(s).replace(/`([^`]+)`/g, '<code>$1</code>'); }
  function pretty(v) { return esc(JSON.stringify(v, null, 2)); }

  /* ---------- routing ---------- */
  function route() {
    var parts = (location.hash || '#overview').slice(1).split('/');
    var view = VIEWS.indexOf(parts[0]) >= 0 ? parts[0] : 'overview';
    all('[data-view]').forEach(function (el) { el.hidden = el.getAttribute('data-view') !== view; });
    all('.links a').forEach(function (a) {
      var active = a.getAttribute('data-route') === view;
      a.classList.toggle('on', active);
      if (active) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
    var target = parts[1] === 'cases' ? byId(view + '-cases') : null;
    if (target) target.scrollIntoView({ block: 'start' });
    else window.scrollTo(0, 0);
  }
  window.addEventListener('hashchange', route);

  all('.scenario-page').forEach(function (view) {
    view.addEventListener('click', function (ev) {
      var choice = ev.target.closest('button[data-case]');
      if (choice) {
        var id = choice.getAttribute('data-case');
        all('button[data-case]', view).forEach(function (button) {
          button.setAttribute('aria-pressed', String(button === choice));
        });
        all('[data-case-panel]', view).forEach(function (panel) {
          panel.hidden = panel.getAttribute('data-case-panel') !== id;
        });
      }
      var task = ev.target.closest('button[data-open-task]');
      if (task) document.dispatchEvent(new CustomEvent('mb-task', { detail: task.getAttribute('data-open-task') }));
    });
  });

  /* ---------- progress ---------- */
  var STATUS_LABEL = { done: 'Done', next: 'Next up', planned: 'Planned' };
  var REVIEW_LABEL = { awaiting: 'Awaiting review', accepted: 'Accepted' };
  var SECTIONS = [
    ['done', 'What was done'], ['where', 'Where to look'], ['checked', 'How it was checked'],
    ['open', 'Not included yet'], ['plan', 'Planned scope']
  ];
  var CHECK = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.2 8.4l3 3 6.6-6.8" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  function allItems() {
    var out = [];
    PG.groups.forEach(function (g) { out = out.concat(g.items); });
    return out;
  }
  function count(items, pred) { return items.filter(pred).length; }
  function tallyHtml() {
    var items = allItems();
    var done = count(items, function (i) { return i.status === 'done'; });
    var waiting = count(items, function (i) { return i.status === 'done' && i.review !== 'accepted'; });
    var next = count(items, function (i) { return i.status === 'next'; });
    var planned = count(items, function (i) { return i.status === 'planned'; });
    return '<div><b>' + done + '</b><span>done, ' + waiting + ' awaiting review</span></div>' +
           '<div><b>' + next + '</b><span>next up</span></div>' +
           '<div><b>' + planned + '</b><span>planned</span></div>';
  }
  function getReviewed(id) {
    try { return localStorage.getItem('macbench.reviewed.' + id) === '1'; } catch (e) { return false; }
  }
  function setReviewed(id, on) {
    try { localStorage.setItem('macbench.reviewed.' + id, on ? '1' : '0'); } catch (e) { /* storage unavailable */ }
  }
  function itemHtml(it) {
    var meta = '<span class="chip s-' + it.status + '"><i></i>' + STATUS_LABEL[it.status] + '</span>';
    if (it.status === 'done') meta += '<span>' + esc(REVIEW_LABEL[it.review] || '') + '</span>';
    if (it.date) meta += '<span>' + esc(it.date) + '</span>';
    var body = '';
    SECTIONS.forEach(function (s) {
      var list = it[s[0]];
      if (!list || !list.length) return;
      body += '<div><h4>' + s[1] + '</h4><ul>' +
        list.map(function (x) { return '<li>' + rich(x) + '</li>'; }).join('') + '</ul></div>';
    });
    if (it.status === 'done' && it.review !== 'accepted') {
      body += '<label class="reviewed"><input type="checkbox" id="rev-' + esc(it.id) + '" data-review="' + esc(it.id) + '"' +
        (getReviewed(it.id) ? ' checked' : '') + '> I have looked at this (kept in this browser only)</label>';
    }
    return '<details class="pitem" data-status="' + it.status + '"' + (it.status === 'done' ? '' : '') + '>' +
      '<summary><span class="pmark">' + CHECK + '</span><span class="ptitle">' + esc(it.title) + '</span>' +
      '<span class="pmeta">' + meta + '</span></summary><div class="pbody">' + body + '</div></details>';
  }
  function renderProgress() {
    byId('tally-overview').innerHTML = tallyHtml();
    byId('tally-progress').innerHTML = tallyHtml();
    byId('updated').textContent = PG.updated;
    byId('pgroups').innerHTML = PG.groups.map(function (g) {
      var done = count(g.items, function (i) { return i.status === 'done'; });
      return '<section><div class="pgroup-head"><h3>' + esc(g.title) + '</h3><span>' + done + ' of ' + g.items.length +
        ' done</span></div><div class="pitems">' + g.items.map(itemHtml).join('') + '</div></section>';
    }).join('');
    byId('pgroups').addEventListener('change', function (e) {
      var id = e.target && e.target.getAttribute && e.target.getAttribute('data-review');
      if (id) setReviewed(id, e.target.checked);
    });
  }

  /* ---------- interface explorer ---------- */
  var schemas = TK.schemas;
  var actions = {};
  TK.actions.forEach(function (a) { actions[a.name] = a; });
  var errorText = {};
  ['common', 'domain'].forEach(function (k) {
    Object.keys(TK.errors[k]).forEach(function (c) { errorText[c] = TK.errors[k][c]; });
  });
  var state = { role: TK.roles[0].name, action: 'search_flights' };
  var formFields = [];

  function refName(p) { return p && p.$ref ? p.$ref.split('/').pop() : null; }
  function nonNull(list) { return list.filter(function (x) { return x.type !== 'null'; }); }
  function typeLabel(p) {
    if (!p) return '';
    if (p.$ref) return refName(p);
    if (p.const !== undefined) return JSON.stringify(p.const);
    if (p.enum) return p.enum.map(function (v) { return JSON.stringify(v); }).join(' | ');
    if (p.anyOf || p.oneOf) return nonNull(p.anyOf || p.oneOf).map(typeLabel).join(' | ');
    if (p.type === 'array') return typeLabel(p.items) + '[]';
    return p.type || 'object';
  }
  function fieldsTable(name) {
    var s = schemas[name];
    if (!s) return '<p class="note">Unknown schema.</p>';
    if (s.enum) {
      return '<p class="note">One of ' + s.enum.map(function (v) { return '<code>' + esc(v) + '</code>'; }).join(' ') + '</p>';
    }
    var props = s.properties || {}, req = s.required || [], keys = Object.keys(props);
    if (!keys.length) return '<p class="note">No fields.</p>';
    return '<table class="ft"><thead><tr><th>Field</th><th>Type</th><th>Required</th><th>Meaning</th></tr></thead><tbody>' +
      keys.map(function (k) {
        var p = props[k];
        return '<tr><td>' + esc(k) + '</td><td>' + esc(typeLabel(p)) + '</td><td class="req">' +
          (req.indexOf(k) >= 0 ? 'yes' : 'no') + '</td><td>' + rich(p.description || '') + '</td></tr>';
      }).join('') + '</tbody></table>';
  }
  function scalar(p) {
    var q = p;
    if (q.anyOf) {
      var rest = nonNull(q.anyOf);
      if (rest.length !== 1) return null;
      q = rest[0];
    }
    if (q.$ref) {
      var t = schemas[refName(q)];
      return t && t.enum ? { kind: 'enum', options: t.enum } : null;
    }
    if (q.enum) return { kind: 'enum', options: q.enum };
    if (q.type === 'string') return { kind: 'text', pattern: q.pattern };
    if (q.type === 'integer') return { kind: 'int', min: q.minimum, max: q.maximum };
    if (q.type === 'boolean') return { kind: 'bool' };
    return null;
  }
  function formHtml(a) {
    var s = schemas[a.request] || {}, props = s.properties || {}, req = s.required || [];
    formFields = [];
    var keys = Object.keys(props);
    if (!keys.length) return '<p class="note">This action takes no fields.</p>';
    return keys.map(function (k) {
      var p = props[k], sc = scalar(p) || { kind: 'json' };
      var id = 'f-' + a.name + '-' + k, required = req.indexOf(k) >= 0;
      formFields.push({ id: id, name: k, kind: sc.kind, required: required, pattern: sc.pattern, min: sc.min, max: sc.max, options: sc.options });
      var def = p.default === undefined || p.default === null ? '' : p.default;
      var control;
      if (sc.kind === 'enum') {
        control = '<select id="' + id + '">' + (required ? '' : '<option value="">(not set)</option>') +
          sc.options.map(function (o) {
            return '<option value="' + esc(o) + '"' + (String(def) === String(o) ? ' selected' : '') + '>' + esc(o) + '</option>';
          }).join('') + '</select>';
      } else if (sc.kind === 'bool') {
        control = '<input type="checkbox" id="' + id + '"' + (def === true ? ' checked' : '') + '>';
      } else if (sc.kind === 'int') {
        control = '<input type="number" id="' + id + '" step="1" value="' + esc(def) + '">';
      } else if (sc.kind === 'text') {
        control = '<input type="text" id="' + id + '" value="' + esc(def) + '" autocomplete="off" spellcheck="false">';
      } else {
        control = '<textarea id="' + id + '" spellcheck="false" placeholder="JSON"></textarea>';
      }
      return '<div class="field"><label for="' + id + '">' + esc(k) + ' <em>' + esc(typeLabel(p)) +
        (required ? ' · required' : '') + '</em></label>' + control +
        (p.description ? '<small>' + rich(p.description) + '</small>' : '') + '</div>';
    }).join('');
  }
  function fillExample(a) {
    var ex = TK.examples[a.name];
    if (!ex) return;
    formFields.forEach(function (f) {
      var el = byId(f.id), v = ex.request[f.name];
      if (!el) return;
      if (f.kind === 'bool') { el.checked = v === true; return; }
      if (v === undefined || v === null) { el.value = ''; return; }
      el.value = f.kind === 'json' ? JSON.stringify(v, null, 2) : String(v);
    });
  }
  function collect() {
    var payload = {}, errors = [];
    formFields.forEach(function (f) {
      var el = byId(f.id);
      if (f.kind === 'bool') { if (el.checked || f.required) payload[f.name] = el.checked; return; }
      var raw = el.value.trim();
      if (raw === '') { if (f.required) errors.push(f.name + ' is required.'); return; }
      if (f.kind === 'int') {
        if (!/^-?\d+$/.test(raw)) { errors.push(f.name + ' must be a whole number.'); return; }
        var n = parseInt(raw, 10);
        if (f.min !== undefined && n < f.min) { errors.push(f.name + ' must be at least ' + f.min + '.'); return; }
        if (f.max !== undefined && n > f.max) { errors.push(f.name + ' must be at most ' + f.max + '.'); return; }
        payload[f.name] = n; return;
      }
      if (f.kind === 'json') {
        try { payload[f.name] = JSON.parse(raw); } catch (e) { errors.push(f.name + ' is not valid JSON.'); }
        return;
      }
      if (f.kind === 'text' && f.pattern && !(new RegExp(f.pattern)).test(raw)) {
        errors.push(f.name + ' does not match the expected format.'); return;
      }
      if (f.kind === 'enum' && typeof f.options[0] === 'number') { payload[f.name] = Number(raw); return; }
      payload[f.name] = raw;
    });
    return { payload: payload, errors: errors };
  }
  function requestId() {
    var s = '';
    for (var i = 0; i < 6; i++) s += Math.floor(Math.random() * 16).toString(16);
    return 'req_' + s;
  }

  function renderRoles() {
    byId('tk-roles').innerHTML = TK.roles.map(function (r) {
      return '<button type="button" data-role="' + esc(r.name) + '" aria-pressed="' + (r.name === state.role) + '">' +
        esc(r.title) + ' · ' + r.actions.length + ' actions</button>';
    }).join('');
    var role = TK.roles.filter(function (r) { return r.name === state.role; })[0];
    byId('tk-role-note').innerHTML = rich(role.description) + ' Seats: ' +
      role.seats.map(function (s) { return '<code>' + esc(s) + '</code>'; }).join(' ') + '.';
  }
  function renderActions() {
    var role = TK.roles.filter(function (r) { return r.name === state.role; })[0];
    if (role.actions.indexOf(state.action) < 0) state.action = role.actions[0];
    var groups = [], seen = {};
    role.actions.forEach(function (n) {
      var g = actions[n].group;
      if (!seen[g]) { seen[g] = []; groups.push(g); }
      seen[g].push(actions[n]);
    });
    byId('tk-actions').innerHTML = groups.map(function (g) {
      return '<div><h4 class="lbl">' + esc(g) + '</h4>' + seen[g].map(function (a) {
        return '<button type="button" data-action="' + esc(a.name) + '" aria-current="' + (a.name === state.action) + '"' +
          (a.status === 'implemented' ? ' class="live" title="Runs in the kernel"' : '') + '>' +
          '<span>' + esc(a.name) + '</span><span class="eff e-' + a.effect + '">' + a.effect + '</span></button>';
      }).join('') + '</div>';
    }).join('');
  }
  function renderDetail() {
    var a = actions[state.action], ex = TK.examples[a.name];
    var errs = a.errors.map(function (c) {
      return '<dt>' + esc(c) + '</dt><dd>' + rich(errorText[c] || '') + '</dd>';
    }).join('');
    byId('tk-detail').innerHTML =
      '<div class="adetail-head"><h3>' + esc(a.name) + '</h3>' +
      '<div class="chips"><span class="eff e-' + a.effect + '">' + a.effect + '</span>' +
      '<span class="chip">costs ' + a.time_cost_s + ' s of world time</span>' +
      (a.status === 'implemented' ? '<span class="chip s-done"><i></i>runs in the kernel</span>'
                                    : '<span class="chip s-planned"><i></i>declared, not running yet</span>') +
      '<span class="chip">' + a.roles.map(esc).join(' · ') + '</span></div>' +
      '<p>' + rich(a.summary) + '</p>' +
      (a.description ? '<p class="dim">' + rich(a.description) + '</p>' : '') +
      (a.visibility ? '<p class="dim">Who can see it: ' + rich(a.visibility) + '</p>' : '') + '</div>' +
      '<div class="panes">' +
        '<div class="pane"><h4 class="lbl">Request</h4><form class="form" id="tk-form" novalidate>' + formHtml(a) +
        '<div class="actions"><button class="btn small" type="submit">Build request</button>' +
        (ex ? '<button class="btn ghost small" type="button" id="tk-fill">Fill with the example</button>' : '') + '</div>' +
        '<div id="tk-out"></div></form></div>' +
        '<div class="pane"><h4 class="lbl">Response</h4>' +
        (ex ? '<p class="note">Example response. This page does not run the world, so nothing is computed here.</p>' +
              (ex.note ? '<p class="note">' + rich(ex.note) + '</p>' : '') +
              '<pre class="json">' + pretty(ex.response) + '</pre>'
            : '<p class="note">No example yet. The response schema is below.</p>') + '</div>' +
      '</div>' +
      '<div class="stack">' +
        '<details class="box"><summary>Request schema · ' + esc(a.request) + '</summary><div>' + fieldsTable(a.request) + '</div></details>' +
        '<details class="box"><summary>Response schema · ' + esc(a.response) + '</summary><div>' + fieldsTable(a.response) + '</div></details>' +
        '<details class="box"><summary>Errors this action can return · ' + a.errors.length + ' specific, ' +
          Object.keys(TK.errors.common).length + ' common</summary><div>' +
          (errs ? '<dl class="kv">' + errs + '</dl>' : '<p class="note">Only the common errors.</p>') + '</div></details>' +
      '</div>';
    if (ex) fillExample(a);
    byId('tk-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var r = collect(), out = byId('tk-out');
      if (r.errors.length) {
        out.innerHTML = '<p class="err">' + r.errors.map(esc).join(' ') + '</p>';
        return;
      }
      var call = { action: a.name, payload: r.payload };
      if (a.effect === 'write') call.request_id = requestId();
      out.innerHTML = '<p class="note">This is the call a seat would send. It is not sent: this page does not run the world.</p>' +
        '<pre class="json">' + pretty(call) + '</pre>';
    });
    var fill = byId('tk-fill');
    if (fill) fill.addEventListener('click', function () { fillExample(a); byId('tk-out').innerHTML = ''; });
  }
  function renderStatic() {
    byId('tk-version').textContent = TK.version;
    byId('tk-live').textContent = TK.actions.filter(function (x) { return x.status === 'implemented'; }).length;
    byId('tk-total').textContent = TK.actions.length;
    byId('tk-conventions').innerHTML = Object.keys(TK.conventions).map(function (k) {
      return '<dt>' + esc(k) + '</dt><dd>' + rich(TK.conventions[k]) + '</dd>';
    }).join('');
    byId('tk-entities').innerHTML = TK.entities.map(function (n) {
      var d = (schemas[n] && schemas[n].description) || '';
      return '<details class="box"><summary>' + esc(n) + '</summary><div>' +
        (d ? '<p class="note" style="margin-bottom:8px">' + rich(d) + '</p>' : '') + fieldsTable(n) + '</div></details>';
    }).join('');
    var facts = TK.extras.fact_keys || {};
    byId('tk-facts').innerHTML = Object.keys(facts).map(function (k) {
      return '<dt>' + esc(k) + '</dt><dd>' + rich(facts[k]) + '</dd>';
    }).join('');
    byId('tk-errors').innerHTML = Object.keys(errorText).map(function (k) {
      return '<dt>' + esc(k) + '</dt><dd>' + rich(errorText[k]) + '</dd>';
    }).join('');
  }
  function renderExplorer() { renderRoles(); renderActions(); renderDetail(); }

  byId('tk-roles').addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('button[data-role]') : null;
    if (!b) return;
    state.role = b.getAttribute('data-role');
    renderExplorer();
  });
  byId('tk-actions').addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('button[data-action]') : null;
    if (!b) return;
    state.action = b.getAttribute('data-action');
    renderActions();
    renderDetail();
  });

  renderProgress();
  renderStatic();
  renderExplorer();
  route();
})();
