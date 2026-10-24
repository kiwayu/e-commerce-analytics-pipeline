// Number and label helpers shared by the dashboard page and its tests.
// Loads as window.fmt in the browser and as a CommonJS module under Node.
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.fmt = factory();
})(this, function () {
  "use strict";

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

  function moneyFull(n) { return "$" + int(n); }

  function day(iso) {
    return new Date(iso + "T00:00:00Z").toLocaleDateString("en-GB", { day: "numeric", month: "short", timeZone: "UTC" });
  }

  function dayLong(iso) {
    return new Date(iso + "T00:00:00Z").toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
  }

  function stamp(iso) {
    return new Date(iso).toLocaleString("en-GB", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit", timeZone: "UTC" }) + " UTC";
  }

  function words(s) {
    if (s === "vip") return "VIP";
    s = String(s).replace(/_/g, " ");
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  // Round axis ticks from zero up to and including the maximum.
  function niceTicks(max, count) {
    if (!(max > 0)) return [0, 1];
    var raw = max / count;
    var mag = Math.pow(10, Math.floor(Math.log10(raw)));
    var step = [1, 2, 2.5, 5, 10].map(function (m) { return m * mag; }).filter(function (s) { return s >= raw; })[0];
    var ticks = [];
    for (var v = 0; v <= max + step * 0.001; v += step) ticks.push(v);
    if (ticks[ticks.length - 1] < max) ticks.push(ticks[ticks.length - 1] + step);
    return ticks;
  }

  // Change from a previous value: percentage by default, percentage points for rates.
  function delta(current, previous, points) {
    var change;
    if (points) {
      change = (current - previous) * 100;
    } else {
      if (!previous) return null;
      change = (current - previous) / previous * 100;
    }
    return {
      text: (change > 0 ? "+" : "") + change.toFixed(1) + (points ? " pts" : "%"),
      dir: change > 0.5 ? "up" : change < -0.5 ? "down" : ""
    };
  }

  return { int: int, pct: pct, compact: compact, money: money, moneyFull: moneyFull, day: day, dayLong: dayLong, stamp: stamp, words: words, niceTicks: niceTicks, delta: delta };
});
