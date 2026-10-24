# Test evidence: base-currency amounts and dashboard helpers

Journeys derived during this change, no separate plan file.

## Journeys

1. As an analyst, I want every amount in the marts expressed in one currency, so that revenue totals across USD, EUR, GBP, CAD and AUD orders are comparable.
2. As a reader of the dashboard, I want a period with no orders to say so, so that the page never renders a broken chart.

## Task report

### Convert amounts to the base currency

- Added `dbt/seeds/fx_rates.csv` and the singular test `dbt/tests/assert_order_amounts_in_base_currency.sql`, which joins raw orders to staged orders and the seed and returns any order whose staged amount is not the raw amount times the rate.
- RED: `dbt test -s assert_order_amounts_in_base_currency` returned `FAIL 2777` (every non-USD order).
- Change: `stg_raw_orders` gained a `converted_orders` CTE that multiplies total, discount, tax and shipping amounts by `fx_rates.rate_to_base`; `stg_raw_shipments` converts shipping and insurance cost the same way. Both keep the original currency code and expose `fx_rate`, which has a `not_null` test so an unknown currency fails the build instead of silently passing through.
- GREEN: `dbt build` finished `PASS=127 WARN=0 ERROR=0`, including the new test.
- Dashboard gross revenue for the last 30 days moved from $1.58M (naive sum) to $1.51M (converted).

### Dashboard helpers and empty periods

- Moved the number and label helpers out of `dashboard/app.js` into `dashboard/format.js`, which loads as `window.fmt` in the page and as a CommonJS module under Node.
- RED: `node --test dashboard/format.test.js` failed with `Cannot find module './format.js'`.
- Change: wrote the module, added `delta()` for the stat tiles, made `niceTicks()` return `[0, 1]` for a zero or empty maximum, and made the chart renderers show "No orders in this period." when a window has no rows.
- GREEN: `node --test dashboard/format.test.js` reports `pass 8, fail 0`. The same command runs in the `dbt-build` CI job before the export.

## Guarantees

| # | What is guaranteed | Test | Type | Result |
|---|--------------------|------|------|--------|
| 1 | Every staged order amount equals the raw amount converted with the seed rate | `dbt/tests/assert_order_amounts_in_base_currency.sql` | dbt data test | PASS |
| 2 | An order in a currency missing from the seed fails the build | `fx_rate` not_null in `dbt/models/staging/staging.yml` | dbt schema test | PASS |
| 3 | The seed has one rate per currency | `unique`, `not_null` in `dbt/seeds/schema.yml` | dbt schema test | PASS |
| 4 | Compact, money, percent and label formatting match the page copy | `dashboard/format.test.js` | unit | PASS |
| 5 | Axis ticks are round numbers that cover the maximum, and never NaN | `dashboard/format.test.js` | unit | PASS |
| 6 | Period deltas report percent, points for rates, and nothing without a baseline | `dashboard/format.test.js` | unit | PASS |
| 7 | Date helpers render ISO input in UTC | `dashboard/format.test.js` | unit | PASS |

## Coverage and gaps

- `node --test --experimental-test-coverage dashboard/format.test.js` reports 98.6% line coverage for `format.js`; the uncovered line is the browser branch of the module wrapper.
- `app.js` (DOM and SVG rendering) has no unit tests. The empty state was verified by hand in a headless browser with the data arrays cleared; a browser-level test is the next step if the page grows.
- Rates in the seed are fixed. Dated rates would need a date-aware join in staging.
