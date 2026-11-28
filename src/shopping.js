(function () {
  'use strict';

  function byId(id) { return document.getElementById(id); }
  function esc(value) {
    return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function pretty(value) { return esc(JSON.stringify(value, null, 2)); }
  function money(cents) { return '$' + (cents / 100).toFixed(2); }
  function clock(utc) { return esc(utc.slice(11, 19)); }

  var tablist = byId('shopping-tabs');
  var tabs = Array.prototype.slice.call(tablist.querySelectorAll('[role="tab"]'));
  var purchaseTab = tabs[0];
  var afterSalesTab = tabs[1];

  function showScenario(tab) {
    tabs.forEach(function (item) {
      var isSelected = item === tab;
      item.setAttribute('aria-selected', String(isSelected));
      item.tabIndex = isSelected ? 0 : -1;
      byId(item.getAttribute('aria-controls')).hidden = !isSelected;
    });
  }

  function chooseScenario(tab) {
    showScenario(tab);
    // Keep the selected scenario linkable without invoking the router's scroll behavior.
    var hash = tab === afterSalesTab ? '#shopping/after-sales' : '#shopping';
    history.replaceState(history.state, '', hash);
  }

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () { chooseScenario(tab); });
  });
  tablist.addEventListener('keydown', function (ev) {
    var next;
    if (ev.key === 'Home') next = purchaseTab;
    else if (ev.key === 'End') next = afterSalesTab;
    else if (ev.key === 'ArrowLeft' || ev.key === 'ArrowRight') next = ev.target === purchaseTab ? afterSalesTab : purchaseTab;
    if (!next) return;
    ev.preventDefault();
    chooseScenario(next);
    next.focus({ preventScroll: true });
  });

  function showLinkedScenario() {
    var parts = location.hash.slice(1).split('/');
    if (parts[0] === 'shopping') showScenario(parts[1] === 'after-sales' ? afterSalesTab : purchaseTab);
  }
  window.addEventListener('hashchange', showLinkedScenario);
  showLinkedScenario();

  var catalogue = byId('shopping-records');
  var runs;

  document.addEventListener('mb-task', function (ev) {
    var record = byId('shopping-record-' + ev.detail);
    if (!record) return;
    catalogue.open = true;
    Array.prototype.forEach.call(catalogue.querySelectorAll('[data-shopping-record]'), function (item) {
      item.hidden = item !== record;
    });
    record.scrollIntoView({ block: 'start' });
    record.querySelector('h4').focus({ preventScroll: true });
  });

  function callSummary(entry, reply) {
    var payload = entry.payload;
    if (!entry.ok) return reply.message;
    if (entry.action === 'send_message') return payload.text || 'Message sent';
    if (entry.action === 'read_inbox') return reply.messages.length + ' messages';
    if (entry.action === 'place_order') {
      return reply.orders.map(function (order) {
        return order.merchant_name + ' · ' + money(order.paid_cents);
      }).join(' · ');
    }
    if (reply.return_quote) return reply.return_quote.return_quote_id + ' · ' + money(reply.return_quote.refund_cents) + ' quoted refund';
    if (reply.exchange_quote) return reply.exchange_quote.exchange_quote_id + ' · ' + money(reply.exchange_quote.fee_cents) + ' quoted fee';
    if (reply.return_case) {
      return reply.return_case.return_id + ' · ' + reply.return_case.status +
        (reply.return_case.status === 'settled' ? ' · ' + money(reply.return_case.refunded_cents) + ' refunded' : '');
    }
    if (reply.exchange) return reply.exchange.exchange_id + ' · ' + reply.exchange.status;
    if (reply.reservation && entry.action !== 'price_cart') {
      return reply.reservation.reservation_id + ' · holds stock until ' + reply.reservation.expires_at.slice(11, 19);
    }
    if (reply.cart_quote) return reply.cart_quote.cart_quote_id + ' · ' + money(reply.cart_quote.total_cents) +
      ' · valid until ' + reply.cart_quote.expires_at.slice(11, 19);
    if (reply.proposal) return reply.proposal.proposal_id + ' · ' + reply.proposal.status + ' · ' + money(reply.proposal.total_cents);
    if (reply.authorization) return reply.authorization.authorization_id + ' · up to ' + money(reply.authorization.max_charge_cents);
    if (reply.product) return reply.product.name;
    return 'OK';
  }

  function eventSummary(entry, effect) {
    if (entry.kind === 'demand') return 'Other shoppers bought ' + effect.taken + ' of ' + effect.asked + ' requested units of ' + effect.variant_id;
    if (entry.kind === 'restock') return 'Added ' + effect.added + ' units of ' + effect.variant_id;
    if (entry.kind === 'controller') return 'Scripted shopper wakes to respond';
    if (entry.kind === 'reservation_expiry') return 'Scheduled expiry of ' + entry.data.reservation_id;
    if (entry.kind === 'orders_before_episode') return 'Load the orders delivered before this episode';
    if (entry.kind === 'return_inspection') return 'Merchant inspects return ' + entry.data.return_id;
    if (entry.kind === 'exchange_inspection') return 'Merchant inspects exchange ' + entry.data.exchange_id;
    if (entry.type === 'open') return 'Observation ends at ' + entry.observation_end.slice(11, 19);
    if (entry.type === 'close') return 'Observation complete';
    return entry.reason || entry.kind || entry.type;
  }

  function logRow(entry, run) {
    var time = '<time class="t" datetime="' + esc(entry.t) + '">' + clock(entry.t) + '</time>';
    if (entry.type !== 'call') {
      var effect = run.market[entry.i];
      return '<details class="sx world"><summary class="sx-row">' + time + '<span class="who">World</span>' +
        '<span class="act">' + esc(entry.kind || entry.type) + '</span><span class="sum">' + esc(eventSummary(entry, effect)) +
        '</span><span class="cost"></span></summary><div class="sx-body"><div><h5>Event</h5><pre class="json">' +
        pretty(entry) + '</pre></div>' + (effect ? '<div><h5>Stock change</h5><pre class="json">' + pretty(effect) + '</pre></div>' : '') +
        '</div></details>';
    }

    var reply = run.responses[entry.i];
    var scripted = entry.by === 'controller';
    var cost = entry.cost_s >= 60 ? Math.floor(entry.cost_s / 60) + ' min ' + entry.cost_s % 60 + ' s' : entry.cost_s + ' s';
    return '<details class="sx' + (scripted ? ' scripted' : '') + (entry.ok ? '' : ' fail') + '"><summary class="sx-row">' + time +
      '<span class="who">' + (entry.seat === 'shopper' ? 'Shopper' : 'Agent') + '</span><span class="act">' + esc(entry.action) + '</span>' +
      '<span class="sum">' + (entry.ok ? '' : '<b>' + esc(entry.error) + '</b> ') + esc(callSummary(entry, reply)) + '</span>' +
      '<span class="cost">+' + cost + '</span></summary><div class="sx-body"><div><h5>Payload</h5><pre class="json">' +
      pretty(entry.payload || entry.raw) + '</pre></div><div><h5>' + (entry.ok ? 'Response' : 'Error') + '</h5><pre class="json">' +
      pretty(reply) + '</pre></div><p class="note">Log entry ' + entry.i + ' · commit sequence ' + entry.seq + '</p></div></details>';
  }

  function renderLog(run) {
    return '<h5>Event log</h5><p class="note">' + run.events.length + ' entries · times in UTC · replay verified · log head <code>' +
      esc(run.head) + '</code></p><p class="note">Open a row for the call payload and response or the recorded world event.</p>' +
      '<div class="sess">' + run.events.map(function (entry) { return logRow(entry, run); }).join('') + '</div>';
  }

  function renderRun(run) {
    var score = run.score;
    var process = score.process;
    var checks = score.checks.map(function (check) {
      return '<li class="' + (check.passed ? 'pass' : 'fail') + '"><strong>' + esc(check.name) + '</strong>' +
        (check.detail ? ' · ' + esc(check.detail) : '') + '</li>';
    }).join('');
    var orders = run.orders.map(function (order) {
      return '<li><code>' + esc(order.order_id) + '</code> · ' + esc(order.merchant_name) + ' · ' + money(order.paid_cents) +
        ' paid · delivery by ' + esc(order.promised_delivery_date) + '</li>';
    }).join('');
    return '<h5>' + (score.success ? 'All requirements met' : 'Task failed') + '</h5><ul class="checks">' + checks + '</ul>' +
      '<p class="note">Loss ' + money(score.total_loss_cents) +
      (score.regret_cents === null ? '' : ' · regret ' + money(score.regret_cents)) + ' · ' + process.calls + ' agent calls · ' +
      process.refused + ' refused · ' + process.world_minutes + ' world minutes</p>' +
      '<h5>Orders placed</h5>' + (orders ? '<ul class="plain-list">' + orders + '</ul>' : '<p class="note">0 orders placed.</p>') +
      renderLog(run);
  }

  document.addEventListener('toggle', function (ev) {
    var detail = ev.target;
    var kind = detail.getAttribute('data-shopping-run');
    if (!kind || !detail.open) return;
    if (kind === 'after-sales') {
      var log = detail.querySelector('[data-shopping-log]');
      if (!log.firstElementChild) log.innerHTML = renderLog(JSON.parse(document.getElementById('data-shopping-after-session').textContent));
      return;
    }
    var body = detail.querySelector('.shopping-run');
    if (body.firstElementChild) return;
    if (!runs) runs = JSON.parse(document.getElementById('data-shopping-runs').textContent);
    body.innerHTML = renderRun(runs[detail.getAttribute('data-shopping-task')][kind]);
  }, true);
})();
