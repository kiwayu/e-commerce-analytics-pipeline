(function () {
  "use strict";

  var DATA = window.DASHBOARD_DATA;
  var SVG = "http://www.w3.org/2000/svg";
  var tooltip = document.getElementById("tooltip");
  var currentWindow = "30";

  // Formatting ---------------------------------------------------------------

  var nf = new Intl.NumberFormat("en-GB");
  function int(n) { return nf.format(Math.round(n)); }
  function pct(n) { return Math.round(n * 100) + "%"; }
  function compact(n) {
    var a = Math.abs(n);
    if (a >= 1e6) return (n / 1e6).toFixed(2) + "M";
    if (a >= 1e4) return (n / 1e3).toFixed(0) + "K";
    if (a >= 1e3) return (n / 1e3).toFixed(1) + "K";
    return int(n);
  }
  function money(n) { return "$" + compact(n); }
  function moneyFull(n) { return "$" + nf.format(Math.round(n)); }
  function day(iso) {
    var d = new Date(iso + "T00:00:00Z");
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", timeZone: "UTC" });
  }
  function dayLong(iso) {
    var d = new Date(iso + "T00:00:00Z");
    return d.toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
  }
  function stamp(iso) {
    var d = new Date(iso);
    return d.toLocaleString("en-GB", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit", timeZone: "UTC" }) + " UTC";
  }
  function words(s) {
    if (s === "vip") return "VIP";
    s = String(s).replace(/_/g, " ");
    return s.charAt(0).toUpperCase() + s.slice(1);
  }
  function widthOf(id, fallback) {
    var w = document.getElementById(id).clientWidth;
    return w > 200 ? w : fallback;
  }

  // DOM helpers ----------------------------------------------------------------

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    setAttrs(node, attrs);
    append(node, children);
    return node;
  }
  function svg(tag, attrs, children) {
    var node = document.createElementNS(SVG, tag);
    setAttrs(node, attrs);
    append(node, children);
    return node;
  }
  function setAttrs(node, attrs) {
    if (!attrs) return;
    Object.keys(attrs).forEach(function (k) {
      if (k === "text") node.textContent = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
  }
  function append(node, children) {
    if (!children) return;
    (Array.isArray(children) ? children : [children]).forEach(function (c) {
      if (c) node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
  }
  function replace(id, child) {
    var host = document.getElementById(id);
    while (host.firstChild) host.removeChild(host.firstChild);
    if (child) host.appendChild(child);
    return host;
  }

  function table(columns, rows) {
    return el("table", null, [
      el("thead", null, el("tr", null, columns.map(function (c) {
        return el("th", { scope: "col", "class": c.num ? "num" : "" }, c.label);
      }))),
      el("tbody", null, rows.map(function (r) {
        return el("tr", null, columns.map(function (c) {
          return el("td", { "class": c.num ? "num" : "" }, c.render ? c.render(r) : String(r[c.key]));
        }));
      }))
    ]);
  }

  // Tooltip ------------------------------------------------------------------

  function showTip(title, lines, x, y) {
    while (tooltip.firstChild) tooltip.removeChild(tooltip.firstChild);
    tooltip.appendChild(el("div", { "class": "t" }, title));
    lines.forEach(function (l) {
      tooltip.appendChild(el("div", { "class": "r" }, [
        l.cls ? el("i", { "class": "key line " + l.cls }) : null,
        el("b", null, l.value),
        el("span", null, l.label)
      ]));
    });
    tooltip.hidden = false;
    var w = tooltip.offsetWidth, h = tooltip.offsetHeight;
    var left = x + 14, top = y + 14;
    if (left + w > window.innerWidth - 8) left = x - w - 14;
    if (top + h > window.innerHeight - 8) top = y - h - 14;
    tooltip.style.left = left + "px";
    tooltip.style.top = top + "px";
  }
  function hideTip() { tooltip.hidden = true; }

  function niceTicks(max, count) {
    var raw = max / count;
    var mag = Math.pow(10, Math.floor(Math.log10(raw)));
    var step = [1, 2, 2.5, 5, 10].map(function (m) { return m * mag; }).filter(function (s) { return s >= raw; })[0];
    var ticks = [];
    for (var v = 0; v <= max + step * 0.001; v += step) ticks.push(v);
    if (ticks[ticks.length - 1] < max) ticks.push(ticks[ticks.length - 1] + step);
    return ticks;
  }

  // Pipeline strip -----------------------------------------------------------

  function renderPipeline() {
    var p = DATA.pipeline;
    var list = replace("layers", null);
    p.layers.forEach(function (layer) {
      var rows = layer.tables.reduce(function (s, t) { return s + t.rows; }, 0);
      var kind = layer.layer === "raw" || layer.layer === "marts" ? "table" : "view";
      list.appendChild(el("li", { title: layer.tables.map(function (t) { return t.name + ": " + int(t.rows) + " rows"; }).join("\n") }, [
        el("div", { "class": "name" }, words(layer.layer)),
        el("div", { "class": "rows" }, int(rows) + " rows"),
        el("div", { "class": "objects" }, layer.tables.length + " " + kind + (layer.tables.length === 1 ? "" : "s"))
      ]));
    });

    var run = replace("run", null);
    var d = p.dbt;
    var items = [
      ["Last dbt build", stamp(p.last_run), "ok"],
      ["Raw data loaded", stamp(p.raw_loaded_at)]
    ];
    if (d) {
      items.push(["Models built", String(d.models)]);
      items.push(["Tests passed", d.tests_passed + " of " + d.tests]);
    }
    items.forEach(function (it) {
      run.appendChild(el("dt", null, it[0]));
      run.appendChild(el("dd", { "class": it[2] || "" }, it[1]));
    });
  }

  // Stat tiles ---------------------------------------------------------------

  function renderTiles(w) {
    var cur = w.metrics.current, prev = w.metrics.previous;
    var days = Number(currentWindow);
    var tiles = [
      { label: "Gross revenue", value: money(cur.revenue), cur: cur.revenue, prev: prev.revenue },
      { label: "Orders", value: int(cur.orders), cur: cur.orders, prev: prev.orders },
      { label: "Average order value", value: moneyFull(cur.aov), cur: cur.aov, prev: prev.aov },
      { label: "Orders fulfilled", value: pct(cur.fulfillment_rate), cur: cur.fulfillment_rate, prev: prev.fulfillment_rate, points: true }
    ];
    var host = replace("tiles", null);
    tiles.forEach(function (t) {
      var delta, cls = "", text;
      if (!prev.orders) {
        text = "No earlier period to compare";
      } else if (t.points) {
        delta = (t.cur - t.prev) * 100;
        cls = delta > 0.5 ? "up" : delta < -0.5 ? "down" : "";
        text = (delta > 0 ? "+" : "") + delta.toFixed(1) + " pts";
      } else {
        delta = t.prev ? (t.cur - t.prev) / t.prev * 100 : 0;
        cls = delta > 0.5 ? "up" : delta < -0.5 ? "down" : "";
        text = (delta > 0 ? "+" : "") + delta.toFixed(1) + "%";
      }
      host.appendChild(el("div", { "class": "tile" }, [
        el("div", { "class": "label" }, t.label),
        el("div", { "class": "value" }, t.value),
        el("div", { "class": "delta " + cls }, delta === undefined ? text : [el("b", null, text), " vs previous " + days + " days"])
      ]));
    });
    document.getElementById("compare").textContent = "Changes compare with the " + days + " days before";
  }

  // Line chart ---------------------------------------------------------------

  function renderRevenue() {
    var days = Number(currentWindow);
    var rows = DATA.daily.slice(-days);
    var W = widthOf("revenue-chart", 1100), H = W < 600 ? 220 : 300, L = 44, R = 16, T = 12, B = 28;
    var pw = W - L - R, ph = H - T - B;
    var max = Math.max.apply(null, rows.map(function (r) { return Math.max(r.gross_revenue, r.gross_revenue_7d_ma); }));
    var ticks = niceTicks(max, 4);
    var top = ticks[ticks.length - 1];
    var x = function (i) { return L + (rows.length === 1 ? pw / 2 : i / (rows.length - 1) * pw); };
    var y = function (v) { return T + ph - v / top * ph; };

    var grid = svg("g", { "class": "grid" }, ticks.map(function (v) {
      return svg("line", { x1: L, x2: W - R, y1: y(v), y2: y(v) });
    }));
    var yLabels = svg("g", null, ticks.map(function (v) {
      return svg("text", { x: L - 8, y: y(v) + 4, "text-anchor": "end", text: v === 0 ? "0" : compact(v) });
    }));
    var every = Math.max(1, Math.round(rows.length / (W < 600 ? 3 : 6)));
    var xLabels = svg("g", null, rows.map(function (r, i) {
      if (i % every !== 0 && i !== rows.length - 1) return null;
      if (i !== rows.length - 1 && rows.length - 1 - i < every / 2) return null;
      return svg("text", { x: x(i), y: H - 8, "text-anchor": i === 0 ? "start" : i === rows.length - 1 ? "end" : "middle", text: day(r.date_day) });
    }));
    var axis = svg("g", { "class": "axis" }, svg("line", { x1: L, x2: W - R, y1: y(0), y2: y(0) }));

    var line = function (key) {
      return rows.map(function (r, i) { return (i ? "L" : "M") + x(i).toFixed(1) + " " + y(r[key]).toFixed(1); }).join(" ");
    };
    var wash = svg("path", { "class": "wash", d: line("gross_revenue") + " L" + x(rows.length - 1).toFixed(1) + " " + y(0) + " L" + x(0).toFixed(1) + " " + y(0) + " Z" });
    var gross = svg("path", { "class": "series s1", d: line("gross_revenue") });
    var avg = svg("path", { "class": "series s2", d: line("gross_revenue_7d_ma") });

    var cross = svg("line", { "class": "cross", y1: T, y2: T + ph, visibility: "hidden" });
    var dot1 = svg("circle", { "class": "dot s1", r: 4, visibility: "hidden" });
    var dot2 = svg("circle", { "class": "dot s2", r: 4, visibility: "hidden" });
    var hit = svg("rect", { "class": "hit", x: L, y: T, width: pw, height: ph });

    var root = svg("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": "Daily gross revenue with 7-day average, last " + days + " days" },
      [grid, yLabels, xLabels, axis, wash, gross, avg, cross, dot1, dot2, hit]);

    function point(evt) {
      var rect = root.getBoundingClientRect();
      var px = (evt.clientX - rect.left) / rect.width * W;
      var i = Math.round((px - L) / pw * (rows.length - 1));
      return Math.max(0, Math.min(rows.length - 1, i));
    }
    function focusAt(i, evt) {
      var r = rows[i];
      cross.setAttribute("x1", x(i)); cross.setAttribute("x2", x(i));
      dot1.setAttribute("cx", x(i)); dot1.setAttribute("cy", y(r.gross_revenue));
      dot2.setAttribute("cx", x(i)); dot2.setAttribute("cy", y(r.gross_revenue_7d_ma));
      [cross, dot1, dot2].forEach(function (n) { n.setAttribute("visibility", "visible"); });
      showTip(dayLong(r.date_day), [
        { cls: "s1", value: moneyFull(r.gross_revenue), label: "gross revenue" },
        { cls: "s2", value: moneyFull(r.gross_revenue_7d_ma), label: "7-day average" },
        { value: int(r.total_orders), label: "orders" }
      ], evt.clientX, evt.clientY);
    }
    function leave() {
      [cross, dot1, dot2].forEach(function (n) { n.setAttribute("visibility", "hidden"); });
      hideTip();
    }
    hit.addEventListener("pointermove", function (evt) { focusAt(point(evt), evt); });
    hit.addEventListener("pointerleave", leave);

    replace("revenue-chart", root);
    replace("revenue-table", table([
      { label: "Day", render: function (r) { return day(r.date_day); } },
      { label: "Orders", num: true, render: function (r) { return int(r.total_orders); } },
      { label: "Gross revenue", num: true, render: function (r) { return moneyFull(r.gross_revenue); } },
      { label: "7-day average", num: true, render: function (r) { return moneyFull(r.gross_revenue_7d_ma); } },
      { label: "Fulfilled", num: true, render: function (r) { return pct(r.fulfillment_rate); } }
    ], rows.slice().reverse()));
  }

  // Horizontal bars ----------------------------------------------------------

  function renderBars(chartId, tableId, rows, opts) {
    var W = widthOf(chartId, 540), rowH = 34, L = W < 420 ? 118 : 150, R = 72, T = 4;
    var H = T + rows.length * rowH + 4;
    var pw = W - L - R;
    var max = Math.max.apply(null, rows.map(function (r) { return r[opts.key]; }));
    var root = svg("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": opts.aria });
    root.appendChild(svg("g", { "class": "axis" }, svg("line", { x1: L, x2: L, y1: T, y2: H - 4 })));

    rows.forEach(function (r, i) {
      var yy = T + i * rowH;
      var w = max ? r[opts.key] / max * pw : 0;
      var g = svg("g", { "class": "bar-row", tabindex: 0 }, [
        svg("rect", { "class": "hit", x: 0, y: yy, width: W, height: rowH }),
        svg("text", { "class": "cat", x: L - 12, y: yy + rowH / 2 + 4, "text-anchor": "end", text: words(r.label) }),
        svg("rect", { "class": "bar", x: L, y: yy + (rowH - 20) / 2, width: Math.max(w, 0), height: 20 }),
        svg("text", { "class": "val", x: L + w + 8, y: yy + rowH / 2 + 4, text: opts.format(r[opts.key]) })
      ]);
      function show(evt) {
        var p = evt.clientX !== undefined ? evt : { clientX: root.getBoundingClientRect().left + L, clientY: root.getBoundingClientRect().top + yy };
        showTip(words(r.label), opts.tip(r), p.clientX, p.clientY);
      }
      g.addEventListener("pointermove", show);
      g.addEventListener("focus", show);
      g.addEventListener("pointerleave", hideTip);
      g.addEventListener("blur", hideTip);
      root.appendChild(g);
    });

    replace(chartId, root);
    replace(tableId, table(opts.columns, rows));
  }

  function renderStatus(w) {
    renderBars("status-chart", "status-table", w.status, {
      key: "orders",
      format: int,
      aria: "Orders by status",
      tip: function (r) { return [{ value: int(r.orders), label: "orders" }, { value: moneyFull(r.revenue), label: "gross revenue" }]; },
      columns: [
        { label: "Status", render: function (r) { return words(r.label); } },
        { label: "Orders", num: true, render: function (r) { return int(r.orders); } },
        { label: "Gross revenue", num: true, render: function (r) { return moneyFull(r.revenue); } }
      ]
    });
  }

  function renderSegments(w) {
    renderBars("segment-chart", "segment-table", w.segments, {
      key: "revenue",
      format: money,
      aria: "Revenue by customer segment",
      tip: function (r) { return [{ value: moneyFull(r.revenue), label: "gross revenue" }, { value: int(r.orders), label: "orders" }, { value: int(r.customers), label: "customers" }]; },
      columns: [
        { label: "Segment", render: function (r) { return words(r.label); } },
        { label: "Customers", num: true, render: function (r) { return int(r.customers); } },
        { label: "Orders", num: true, render: function (r) { return int(r.orders); } },
        { label: "Gross revenue", num: true, render: function (r) { return moneyFull(r.revenue); } }
      ]
    });
  }

  // Tables -------------------------------------------------------------------

  function renderCarriers(w) {
    replace("carrier-table", table([
      { label: "Carrier", key: "label" },
      { label: "Delivered orders", num: true, render: function (r) { return int(r.shipments); } },
      { label: "On time", render: function (r) {
        return el("span", null, [el("span", { "class": "rate", "aria-hidden": "true" }, el("i", { style: "width:" + Math.round(r.on_time_rate * 100) + "%" })), pct(r.on_time_rate)]);
      } },
      { label: "Days to deliver", num: true, render: function (r) { return r.avg_days.toFixed(1); } }
    ], w.carriers.slice().sort(function (a, b) { return b.on_time_rate - a.on_time_rate; })));
  }

  function renderCountries(w) {
    replace("country-table", table([
      { label: "Country", key: "label" },
      { label: "Orders", num: true, render: function (r) { return int(r.orders); } },
      { label: "Gross revenue", num: true, render: function (r) { return moneyFull(r.revenue); } },
      { label: "Average order", num: true, render: function (r) { return moneyFull(r.aov); } }
    ], w.countries));
  }

  // Wiring -------------------------------------------------------------------

  function render() {
    var w = DATA.windows[currentWindow];
    renderTiles(w);
    renderRevenue();
    renderStatus(w);
    renderSegments(w);
    renderCarriers(w);
    renderCountries(w);
  }

  document.querySelectorAll(".controls button").forEach(function (b) {
    b.addEventListener("click", function () {
      currentWindow = b.getAttribute("data-window");
      document.querySelectorAll(".controls button").forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
      hideTip();
      render();
    });
  });

  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(render, 150);
  });

  document.getElementById("as-of").textContent = dayLong(DATA.as_of);
  document.getElementById("generated").textContent = stamp(DATA.generated_at);
  renderPipeline();
  render();
})();
