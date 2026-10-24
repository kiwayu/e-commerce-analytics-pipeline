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

## Days without orders in revenue_daily

- Added the dbt unit test `revenue_daily_counts_days_without_orders` in `dbt/models/marts/finance/revenue_daily_unit_tests.yml`, which feeds three orders on 1, 2 and 4 January and expects 3 January to appear with zero orders and the 7-day average to count it.
- RED: `dbt test --select unit_test:revenue_daily_counts_days_without_orders` returned `FAIL 1`: 3 January was missing and the 4 January average was 53.33 instead of 40.
- Change: `revenue_daily` now builds a calendar spine with `generate_series` between the first and last order date, left joins the per-day aggregates onto it with zero defaults, and rounds the moving averages to two decimals.
- GREEN: the unit test passes and `dbt build` finished `PASS=128 WARN=0 ERROR=0`.
- Because dbt unit tests need dbt 1.8 or later, the Docker `_PIP_ADDITIONAL_REQUIREMENTS` default and the standalone dbt image in the README moved from 1.6.6 to 1.9.

| # | What is guaranteed | Test | Type | Result |
|---|--------------------|------|------|--------|
| 8 | Every calendar day between the first and last order has a `revenue_daily` row, and the 7-day averages count empty days as zero | `revenue_daily_counts_days_without_orders` | dbt unit test | PASS |

## Dated exchange rates, original_currency, and the export task

- `fx_rates` gained a `valid_from` column. Staging now looks up, per order and per shipment, the latest rate whose `valid_from` is on or before the order date (shipped date for shipments) with a lateral join.
- RED: `dbt test --select unit_test:stg_raw_orders_uses_the_rate_in_force_on_the_order_date` failed at compile time: `Invalid column name: 'valid_from' in unit test fixture for 'fx_rates'`.
- GREEN: the unit test converts two EUR orders either side of a rate change at 1.08 and 1.10 and a USD order at 1.00; `dbt build --full-refresh` finished `PASS=131 WARN=0 ERROR=0`.
- `fact_orders.order_currency` is renamed `original_currency` with a `not_null` test. RED: `column "original_currency" does not exist`. GREEN: passes in the same build.
- The daily DAG gained an `export_dashboard` task between validation and the notifications, the Compose file mounts `dashboard/` into the Airflow containers, and `export.py` falls back to psycopg2 when psycopg 3 is absent. RED: `airflow/test_dag_structure.py` was extended first and the CI job `airflow-dags` failed on the pushed test-only commit with `Missing expected task: export_dashboard`. GREEN: the following CI run passes with the task in place. Airflow does not install on Windows, so this check runs only in CI.

| # | What is guaranteed | Test | Type | Result |
|---|--------------------|------|------|--------|
| 9 | Orders and shipments use the exchange rate in force on their date | `stg_raw_orders_uses_the_rate_in_force_on_the_order_date` | dbt unit test | PASS |
| 10 | `fx_rates` has at most one rate per currency per start date | `dbt_utils.unique_combination_of_columns` in `dbt/seeds/schema.yml` | dbt schema test | PASS |
| 11 | `fact_orders` records the currency each order was placed in | `not_null_fact_orders_original_currency` | dbt schema test | PASS |
| 12 | The daily DAG exports the dashboard after validation and before notifying | `airflow/test_dag_structure.py` | DAG structure check (CI) | PASS |
