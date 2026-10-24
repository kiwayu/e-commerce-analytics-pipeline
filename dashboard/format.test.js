"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const f = require("./format.js");

test("compact shortens large numbers and leaves small ones alone", () => {
  assert.equal(f.compact(1584912.55), "1.58M");
  assert.equal(f.compact(24142), "24K");
  assert.equal(f.compact(2400), "2.4K");
  assert.equal(f.compact(999), "999");
  assert.equal(f.compact(0), "0");
});

test("money prefixes the compact form with a dollar sign", () => {
  assert.equal(f.money(52000), "$52K");
  assert.equal(f.moneyFull(1003.1), "$1,003");
});

test("pct rounds to whole percent", () => {
  assert.equal(f.pct(0.5658), "57%");
  assert.equal(f.pct(0), "0%");
});

test("words turns snake_case labels into sentence case and keeps VIP upper", () => {
  assert.equal(f.words("loyal_customer"), "Loyal customer");
  assert.equal(f.words("vip"), "VIP");
  assert.equal(f.words("FedEx"), "FedEx");
});

test("niceTicks returns round steps from zero that cover the maximum", () => {
  const ticks = f.niceTicks(78900, 4);
  assert.equal(ticks[0], 0);
  assert.ok(ticks[ticks.length - 1] >= 78900);
  assert.deepEqual(ticks, [0, 20000, 40000, 60000, 80000]);
});

test("niceTicks copes with a zero or empty maximum instead of producing NaN", () => {
  assert.deepEqual(f.niceTicks(0, 4), [0, 1]);
  assert.deepEqual(f.niceTicks(-Infinity, 4), [0, 1]);
});

test("delta reports percentage change, points for rates, and nothing without a baseline", () => {
  assert.deepEqual(f.delta(95, 100), { text: "-5.0%", dir: "down" });
  assert.deepEqual(f.delta(100.2, 100), { text: "+0.2%", dir: "" });
  assert.deepEqual(f.delta(0.57, 0.55, true), { text: "+2.0 pts", dir: "up" });
  assert.equal(f.delta(10, 0), null);
});

test("date helpers format ISO input in UTC", () => {
  assert.equal(f.day("2026-10-24"), "24 Oct");
  assert.match(f.dayLong("2026-10-24"), /^Sat,? 24 Oct 2026$/);
  assert.match(f.stamp("2026-10-24T09:51:46+00:00"), /24 Oct 2026, 09:51 UTC$/);
});
