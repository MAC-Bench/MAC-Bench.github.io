(function () {
  'use strict';

  var node = document.getElementById('data-world');
  if (!node) return;
  var W = JSON.parse(node.textContent);

  function byId(id) { return document.getElementById(id); }
  function all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function commas(s) { return s.replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function usd(c) { return '$' + commas(String(Math.round(c / 100))); }
  function usd2(c) { return '$' + commas((c / 100).toFixed(2)); }
  function hm(min) { var h = Math.floor(min / 60), m = min % 60; return (h ? h + ' h ' : '') + m + ' min'; }
  function clock(min) { var m = ((min % 1440) + 1440) % 1440; return pad(Math.floor(m / 60)) + ':' + pad(m % 60); }

  var airports = W.airports, carriers = W.carriers, aircraft = W.aircraft;
  var carrierName = {};
  carriers.forEach(function (c) { carrierName[c.code] = c.name; });
  var cityOf = {};
  airports.forEach(function (a) { cityOf[a.code] = a.city; });
  var first = W.meta.first_date.split('-').map(Number);
  var WEEKDAY = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  var MONTH = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function dayLabel(i) {
    var d = new Date(Date.UTC(first[0], first[1] - 1, first[2] + i));
    return WEEKDAY[d.getUTCDay()] + ' ' + d.getUTCDate() + ' ' + MONTH[d.getUTCMonth()];
  }
  function dateLabel(iso) {
    var p = iso.slice(0, 10).split('-').map(Number), d = new Date(Date.UTC(p[0], p[1] - 1, p[2]));
    return WEEKDAY[d.getUTCDay()] + ' ' + d.getUTCDate() + ' ' + MONTH[d.getUTCMonth()];
  }
  function dayDiff(a, b) {
    return Math.round((Date.parse(b.slice(0, 10) + 'T00:00:00Z') - Date.parse(a.slice(0, 10) + 'T00:00:00Z')) / 86400000);
  }

  /* ---------- tabs ---------- */
  byId('w-tabs').addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('button[data-wtab]') : null;
    if (!b) return;
    var tab = b.getAttribute('data-wtab');
    all('#w-tabs button').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
    all('[data-wpanel]').forEach(function (p) { p.hidden = p.getAttribute('data-wpanel') !== tab; });
  });

  /* ---------- world summary ---------- */
  byId('w-meta').innerHTML =
    'Dev world, seed ' + W.meta.seed + ', digest <code>' + esc(W.meta.digest) + '</code>. World time ' +
    esc(W.meta.now.replace('T', ' ').replace('Z', ' UTC')) + '. Schedule ' + dayLabel(0) + ' to ' + dayLabel(W.meta.days - 1) +
    ' 2027: ' + commas(String(W.meta.flights)) + ' flights, ' + W.meta.airports + ' airports, ' + W.meta.city_pairs +
    ' city pairs, ' + carriers.length + ' carriers. Airport positions and distances are real. Carriers, timetables, loads and fares are synthetic.';

  /* ---------- seat map ---------- */
  function seatSvg(sm) {
    var rows = sm.rows[1] - sm.rows[0] + 1, cols = sm.cols, ai = cols.indexOf(sm.aisle_after);
    var cell = 13, step = 16, left = 26, top = 6, aisle = 12;
    var w = left + rows * step + 8, h = top + cols.length * step + aisle + 20;
    var out = '<svg class="seatmap" viewBox="0 0 ' + w + ' ' + h + '" width="' + w + '" height="' + h +
      '" role="img" aria-label="Seat map, front of the cabin on the left. ' + sm.sold + ' of ' + sm.capacity + ' seats taken.">';
    cols.forEach(function (c, j) {
      var y = top + j * step + (j > ai ? aisle : 0);
      out += '<text x="8" y="' + (y + 10.5) + '" class="sm-t">' + esc(c) + '</text>';
      for (var i = 0; i < rows; i++) {
        var taken = sm.occ[i].charAt(j) === 'x', extra = sm.extra.indexOf(sm.rows[0] + i) >= 0;
        out += '<rect x="' + (left + i * step) + '" y="' + y + '" width="' + cell + '" height="' + cell + '" rx="2.5" class="' +
          (taken ? 'sm-occ' : extra ? 'sm-extra' : 'sm-free') + '"/>';
      }
    });
    for (var r = 0; r < rows; r++) {
      var num = sm.rows[0] + r;
      if (r === 0 || num % 5 === 0) {
        out += '<text x="' + (left + r * step + cell / 2) + '" y="' + (h - 5) + '" text-anchor="middle" class="sm-t">' + num + '</text>';
      }
    }
    return out + '</svg>';
  }

  /* ---------- sample searches ---------- */
  var BRANDS = ['basic', 'standard', 'flex'];
  var brandInfo = {};
  W.brands.forEach(function (b) { brandInfo[b.brand] = b; });
  var sortKey = {
    price: function (r) { return Math.min.apply(null, BRANDS.map(function (b) { return r.brands[b] ? r.brands[b].pp : 1e12; })); },
    duration: function (r) { return r.dur; },
    departure: function (r) { return Date.parse(r.dep_utc); },
    arrival: function (r) { return Date.parse(r.arr_utc); }
  };
  function refundText(b) {
    return { original_payment: 'refund to the original payment', travel_credit: 'refund as travel credit', none: 'no refund' }[b.refund_to];
  }
  function itinHtml(r, pax) {
    var a = r.segs[0], z = r.segs[r.segs.length - 1];
    var plus = dayDiff(a.dep, z.arr);
    var stops = r.stops ? '1 stop in ' + esc(a.d) + ' · ' + hm(r.lay[0]) + ' layover' : 'Nonstop';
    var flightsTxt = r.segs.map(function (s) { return s.fn; }).join(' + ');
    var prices = BRANDS.map(function (b) {
      var p = r.brands[b];
      if (!p) return '<div class="px none"><span class="lbl">' + b + '</span><b>Sold out</b></div>';
      return '<div class="px"><span class="lbl">' + b + '</span><b>' + usd(p.pp) + '</b>' +
        (p.left < 9 ? '<span class="left">' + p.left + ' left</span>' : '<span class="left">&nbsp;</span>') + '</div>';
    }).join('');
    var segs = r.segs.map(function (s, i) {
      var d = dayDiff(s.dep, s.arr);
      return '<li><b>' + esc(s.dep.slice(11)) + '</b> ' + esc(s.o) + ' ' + esc(cityOf[s.o]) + ' <span class="dim">' + dateLabel(s.dep) + '</span><br>' +
        '<span class="dim">' + esc(carrierName[s.c]) + ' ' + esc(s.fn) + ' · ' + esc(s.ac) + ' · ' + hm(s.blk) + ' · ' + commas(String(s.km)) + ' km</span><br>' +
        '<b>' + esc(s.arr.slice(11)) + '</b> ' + esc(s.d) + ' ' + esc(cityOf[s.d]) + (d ? ' <span class="dim">next day</span>' : '') +
        (i < r.lay.length ? '<br><span class="lay">Connection in ' + esc(s.d) + ': ' + hm(r.lay[i]) + '</span>' : '') + '</li>';
    }).join('');
    var fareRows = BRANDS.map(function (b) {
      var p = r.brands[b], info = brandInfo[b];
      if (!p) return '<tr><td>' + b + '</td><td colspan="5">Sold out for ' + pax + '</td></tr>';
      return '<tr><td>' + b + '</td><td>' + usd2(p.base) + '</td><td>' + usd2(p.tax) + '</td><td>' + usd2(p.pp) + '</td><td>' +
        (pax > 1 ? usd2(p.pp * pax) : usd2(p.pp)) + '</td><td>' +
        (info.changeable ? 'Changes allowed' : 'No changes') + '; cancel fee ' + usd(info.cancel_fee_cents) + ', ' + refundText(info) +
        '; class ' + esc(p.cls) + '</td></tr>';
    }).join('');
    var maps = r.segs.map(function (s) {
      var sm = W.seat_maps[s.fid];
      return sm ? '<div><p class="dim">' + esc(s.fn) + ' · ' + esc(sm.aircraft) + ' · ' + sm.sold + ' of ' + sm.capacity +
        ' seats taken</p><div class="smscroll">' + seatSvg(sm) + '</div></div>' : '';
    }).join('');
    return '<details class="itin"><summary>' +
      '<div class="it-main"><div class="it-times"><b>' + esc(a.dep.slice(11)) + '</b><span class="it-bar"></span><b>' + esc(z.arr.slice(11)) + '</b>' +
      (plus ? '<sup>+' + plus + '</sup>' : '') + '</div>' +
      '<div class="it-sub">' + esc(a.o) + ' to ' + esc(z.d) + ' · ' + hm(r.dur) + ' · ' + stops + '</div>' +
      '<div class="it-sub dim">' + esc(carrierName[a.c]) + ' · ' + esc(flightsTxt) + '</div></div>' +
      '<div class="it-prices">' + prices + '</div></summary>' +
      '<div class="it-body"><ol class="segs">' + segs + '</ol>' +
      '<div class="tscroll"><table class="ft"><thead><tr><th>Fare</th><th>Base</th><th>Taxes and fees</th><th>Per traveller</th><th>' +
      (pax > 1 ? 'For ' + pax : 'Total') + '</th><th>Conditions</th></tr></thead><tbody>' + fareRows + '</tbody></table></div>' +
      (maps ? '<div class="maps">' + maps + '<p class="dim"><span class="key sm-free"></span> free <span class="key sm-extra"></span> free, extra legroom <span class="key sm-occ"></span> taken</p></div>' : '') +
      '</div></details>';
  }
  function renderSearch() {
    var s = W.samples[+byId('w-sample').value], key = sortKey[byId('w-sort').value];
    var list = s.itineraries.slice().sort(function (x, y) { return key(x) - key(y); });
    var q = s.request, pax = q.passengers;
    var cheapest = Math.min.apply(null, list.map(sortKey.price));
    var fastest = Math.min.apply(null, list.map(sortKey.duration));
    byId('w-summary').innerHTML =
      '<code>search_flights</code> ' + esc(q.origin) + ' to ' + esc(q.destination) + ', ' + dateLabel(q.date) + ', ' + pax +
      (pax > 1 ? ' travellers' : ' traveller') + '. ' + s.itineraries_total + ' itineraries in three fare brands' +
      (s.itineraries_total > list.length ? ', the ' + list.length + ' cheapest shown' : '') +
      '. From ' + usd(cheapest) + ' per traveller, fastest ' + hm(fastest) + '. Prices include taxes and fees.';
    byId('w-itins').innerHTML = list.map(function (r) { return itinHtml(r, pax); }).join('');
  }
  byId('w-sample').innerHTML = W.samples.map(function (s, i) {
    return '<option value="' + i + '">' + esc(s.label) + '</option>';
  }).join('');
  byId('w-sample').addEventListener('change', renderSearch);
  byId('w-sort').addEventListener('change', renderSearch);

  /* ---------- departures board ---------- */
  function renderBoard() {
    var a = +byId('w-airport').value, day = +byId('w-day').value;
    var rows = W.flights.filter(function (f) { return f[0] === a && Math.floor(f[4] / 1440) === day; });
    byId('w-board-note').textContent = rows.length + ' departures from ' + airports[a].name + ' on ' + dayLabel(day) +
      '. Local times, ' + airports[a].tz + '.';
    byId('w-board').innerHTML = rows.map(function (f) {
      var plus = Math.floor(f[5] / 1440) - Math.floor(f[4] / 1440);
      return '<tr><td><b>' + clock(f[4]) + '</b></td><td>' + esc(carriers[f[2]].code) + f[3] + '</td><td>' + esc(airports[f[1]].code) + ' ' +
        esc(airports[f[1]].city) + '</td><td>' + clock(f[5]) + (plus ? ' +' + plus : '') + '</td><td>' + hm(f[6]) + '</td><td>' +
        esc(aircraft[f[7]].code) + '</td><td>' + (f[8] === null ? 'Sold out' : usd2(f[8])) + '</td><td>' +
        (f[8] === null ? '' : (f[9] >= 9 ? '9 or more' : f[9])) + '</td></tr>';
    }).join('');
  }
  byId('w-airport').innerHTML = airports.map(function (a, i) {
    return '<option value="' + i + '"' + (a.code === 'SFO' ? ' selected' : '') + '>' + esc(a.code) + ' · ' + esc(a.city) + '</option>';
  }).join('');
  var days = '';
  for (var i = 0; i < W.meta.days; i++) days += '<option value="' + i + '"' + (i === 4 ? ' selected' : '') + '>' + dayLabel(i) + '</option>';
  byId('w-day').innerHTML = days;
  byId('w-airport').addEventListener('change', renderBoard);
  byId('w-day').addEventListener('change', renderBoard);

  /* ---------- network map ---------- */
  var LABEL = { SFO: [-12, 4, 'end'], LAX: [-12, 4, 'end'], SEA: [-12, 4, 'end'], EWR: [-11, 5, 'end'], DCA: [-11, 6, 'end'],
                LGA: [8, -9, 'start'], JFK: [11, 12, 'start'], BOS: [10, -2, 'start'], MIA: [11, 4, 'start'] };
  function xy(a) { return [40 + (a.lon + 125) / 56 * 920, 28 + (50 - a.lat) / 26 * 544]; }
  function renderMap() {
    var hubs = {};
    carriers.forEach(function (c) { c.hubs.forEach(function (h) { hubs[h] = true; }); });
    var out = '<svg viewBox="0 0 1000 600" role="img" aria-label="Route map of the dev world: ' + W.meta.airports +
      ' airports and ' + W.meta.city_pairs + ' city pairs. Denser lines mean more flights per day.">';
    W.routes.forEach(function (r) {
      var p = xy(airports[r[0]]), q = xy(airports[r[1]]);
      out += '<line x1="' + p[0].toFixed(1) + '" y1="' + p[1].toFixed(1) + '" x2="' + q[0].toFixed(1) + '" y2="' + q[1].toFixed(1) +
        '" class="rt" stroke-opacity="' + Math.min(0.75, 0.10 + 0.045 * r[2]).toFixed(2) + '"/>';
    });
    airports.forEach(function (a) {
      var p = xy(a), l = LABEL[a.code] || [10, 4, 'start'];
      out += '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="' + (2 + a.size) + '" class="' + (hubs[a.code] ? 'ap hub' : 'ap') + '"/>' +
        '<text x="' + (p[0] + l[0]).toFixed(1) + '" y="' + (p[1] + l[1]).toFixed(1) + '" text-anchor="' + l[2] + '" class="apl">' + esc(a.code) + '</text>';
    });
    byId('w-map').innerHTML = out + '</svg>';
    byId('w-carriers').innerHTML = carriers.map(function (c) {
      return '<dt>' + esc(c.code) + ' · ' + esc(c.name) + '</dt><dd>Hubs: ' + c.hubs.map(esc).join(', ') + '</dd>';
    }).join('');
    byId('w-checks').innerHTML = W.checks.map(function (c) {
      return '<tr><td>' + esc(c.a) + ' to ' + esc(c.b) + '</td><td>' + commas(String(c.km)) + ' km</td><td>' + hm(c.blk_out) + '</td><td>' + hm(c.blk_back) +
        '</td><td>' + c.per_day + '</td><td>' + c.carriers.map(esc).join(', ') + '</td><td>' + usd(c.std_min) + ' to ' + usd(c.std_max) + '</td></tr>';
    }).join('');
  }

  /* ---------- fares and rules ---------- */
  function renderFares() {
    var f = W.fees;
    byId('w-brands').innerHTML = W.brands.map(function (b) {
      return '<tr><td>' + esc(b.brand) + '</td><td>' + Math.round(b.multiplier * 100) + '%</td><td>' +
        (b.changeable ? 'Yes, fee ' + usd(b.change_fee_cents) : 'No') + '</td><td>Fee ' + usd(b.cancel_fee_cents) + ', ' + refundText(b) +
        '</td><td>' + (b.holdable ? 'Yes' : 'No') + '</td><td>' + b.checked_bags_included + '</td><td>' + (b.seat_selection_included ? 'Included' : 'Seat fee applies') + '</td></tr>';
    }).join('');
    byId('w-buckets').innerHTML = W.buckets.map(function (b) {
      return '<tr><td>' + esc(b['class']) + '</td><td>' + Math.round(b.share * 100) + '%</td><td>' + Math.round(b.multiplier * 100) + '%</td></tr>';
    }).join('');
    byId('w-rules').innerHTML = [
      'Lowest standard base fare: ($' + f.fare_fixed_usd + ' + $' + f.fare_per_km_usd + ' per km) × a route factor × a time-of-day and weekday factor, rounded to whole dollars.',
      'Each flight sells from the cheapest fare class that still has enough seats for the whole party, so several seats can cost more each than one seat.',
      'A connection is priced on the origin-to-destination distance at 93% and takes the dearer class of its two flights.',
      'Taxes and fees per traveller: ' + (f.excise_rate * 100) + '% of the base fare, ' + usd2(f.security_fee) + ' per one-way trip, ' + usd2(f.segment_fees) + ' per flight.',
      'Checked bags: ' + f.bags.map(usd).join(', ') + ' for the first, second and third. Seats: ' + usd(f.seat.window) + ' window or aisle, ' + usd(f.seat.extra_legroom) + ' extra legroom, middle seats free.',
      'Connections: same carrier, at least the airport\'s minimum connection time, at most 4 hours.',
      'No nonstop beyond ' + commas(String(f.perimeter_km.LGA)) + ' km from LaGuardia or ' + commas(String(f.perimeter_km.DCA)) + ' km from Washington National.',
      'An offer expires ' + f.offer_ttl_minutes + ' minutes after the search that produced it.'
    ].map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('');
    var a = W.after;
    byId('w-after').innerHTML = [
      'Sales close ' + a.sale_close_minutes + ' minutes before the first departure. An unpaid hold lasts ' + (a.hold_minutes / 60) + ' hours, or until ' + (a.hold_cutoff_minutes / 60) + ' hours before departure.',
      'Changes and cancellations at the travellers\' request close ' + a.change_cutoff_minutes + ' minutes before departure. A change costs the change fee plus the fare difference; a cheaper flight returns the difference.',
      'Cancelled within ' + a.free_cancel_hours + ' hours of ticketing, a ticket issued at least ' + a.free_cancel_min_days_ahead + ' days before departure is refunded in full to the original payment. This is the agency\'s own policy.',
      'Otherwise the fare brand decides: the cancellation fee is kept from the base fare, taxes always come back, and seat, bag and change fees are not returned.',
      'A refund goes to whoever paid for the passenger\'s ticket. Co-payers share a partial refund in proportion to what each paid.',
      'When the airline moves a flight by ' + (a.significant_shift_minutes / 60) + ' hours or more, cancels it, or breaks a connection, the travellers may rebook at no charge or take a full refund. A smaller move can only be accepted.',
      'Free rebooking: same carrier, same two metro areas, the scheduled date or up to ' + a.rebook_window_days + ' day later, any flight with seats left.',
      'No answer by the departure of the first flight: the travellers fly as rescheduled if they can, and are refunded in full if they cannot.',
      'Change offers and cancellation quotes expire after ' + a.quote_ttl_minutes + ' minutes. A change or a cancellation covers a whole order; split the order first for some travellers only.'
    ].map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('');
  }

  renderSearch();
  renderBoard();
  renderMap();
  renderFares();
})();
