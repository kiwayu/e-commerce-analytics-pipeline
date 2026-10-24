"""Export dashboard data from the analytics marts to dashboard/data.js.

Reads the same DWH_POSTGRES_* variables as dbt/profiles.yml, so it works
against the Docker warehouse, a local Postgres, or the CI service container.

    python dashboard/export.py
"""

import json
import os
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg

HERE = Path(__file__).resolve().parent
RUN_RESULTS = HERE.parent / "dbt" / "target" / "run_results.json"
WINDOWS = (7, 30, 90)


def connect():
    return psycopg.connect(
        host=os.environ.get("DWH_POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("DWH_POSTGRES_PORT", "5432")),
        user=os.environ.get("DWH_POSTGRES_USER", "ecommerce_user"),
        password=os.environ.get("DWH_POSTGRES_PASSWORD", "ecommerce123"),
        dbname=os.environ.get("DWH_POSTGRES_DB", "ecommerce"),
    )


def rows(cur, sql, params=None):
    cur.execute(sql, params)
    cols = [c.name for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def one(cur, sql, params=None):
    cur.execute(sql, params)
    return cur.fetchone()[0]


def window_metrics(cur, as_of, days):
    """Headline numbers for the last `days` days and the equal period before."""
    sql = """
        select count(*) as orders,
               coalesce(sum(total_amount), 0) as revenue,
               coalesce(avg(total_amount), 0) as aov,
               coalesce(avg(case when order_status_group = 'fulfilled' then 1.0 else 0.0 end), 0) as fulfillment_rate,
               count(distinct customer_id) as customers
        from analytics.fact_orders
        where order_date >= %(start)s and order_date < %(end)s
    """
    cur.execute(sql, {"start": as_of - timedelta(days=days - 1), "end": as_of + timedelta(days=1)})
    current = dict(zip([c.name for c in cur.description], cur.fetchone()))
    cur.execute(sql, {"start": as_of - timedelta(days=2 * days - 1), "end": as_of - timedelta(days=days - 1)})
    previous = dict(zip([c.name for c in cur.description], cur.fetchone()))
    return {"current": current, "previous": previous}


def window_breakdowns(cur, as_of, days):
    params = {"start": as_of - timedelta(days=days - 1), "end": as_of + timedelta(days=1)}
    where = "where order_date >= %(start)s and order_date < %(end)s"
    return {
        "status": rows(cur, f"""
            select order_status as label, count(*) as orders, sum(total_amount) as revenue
            from analytics.fact_orders {where}
            group by 1 order by 2 desc""", params),
        "segments": rows(cur, f"""
            select coalesce(customer_segment, 'unknown') as label,
                   count(*) as orders, sum(total_amount) as revenue,
                   count(distinct customer_id) as customers
            from analytics.fact_orders {where}
            group by 1 order by 3 desc""", params),
        "countries": rows(cur, f"""
            select coalesce(customer_country, 'unknown') as label,
                   count(*) as orders, sum(total_amount) as revenue,
                   avg(total_amount) as aov
            from analytics.fact_orders {where}
            group by 1 order by 3 desc""", params),
        "carriers": rows(cur, f"""
            select primary_carrier as label, count(*) as shipments,
                   avg(case when delivered_on_time then 1.0 else 0.0 end) as on_time_rate,
                   avg(days_to_complete_delivery) as avg_days
            from analytics.fact_orders {where} and delivered_shipments > 0
            group by 1 order by 2 desc""", params),
        "payment": rows(cur, f"""
            select payment_method as label, count(*) as orders, sum(total_amount) as revenue
            from analytics.fact_orders {where}
            group by 1 order by 2 desc""", params),
    }


def layer_counts(cur):
    """Row counts per pipeline layer, raw through marts."""
    layers = [
        ("raw", [("raw", t) for t in ("raw_customers", "raw_orders", "raw_shipments")]),
        ("staging", [("analytics", t) for t in ("stg_raw_customers", "stg_raw_orders", "stg_raw_shipments")]),
        ("intermediate", [("analytics", t) for t in ("int_customer_order_metrics", "int_order_shipment_combined")]),
        ("marts", [("analytics", t) for t in ("dim_customers", "fact_orders", "revenue_daily", "customer_segmentation")]),
    ]
    out = []
    for name, tables in layers:
        entries = []
        for schema, table in tables:
            cur.execute(f"select count(*) from {schema}.{table}")
            entries.append({"name": table, "rows": cur.fetchone()[0]})
        out.append({"layer": name, "tables": entries})
    return out


def dbt_summary():
    """Model and test counts from the last dbt build, if its artifacts exist."""
    if not RUN_RESULTS.exists():
        return None
    results = json.loads(RUN_RESULTS.read_text(encoding="utf-8"))["results"]
    tests = [r for r in results if r["unique_id"].startswith("test.")]
    models = [r for r in results if r["unique_id"].startswith("model.")]
    return {
        "models": len(models),
        "tests": len(tests),
        "tests_passed": sum(1 for r in tests if r["status"] == "pass"),
        "elapsed_seconds": round(sum(r["execution_time"] for r in results), 1),
    }


def plain(value):
    """JSON encoder for the database types json.dumps does not know."""
    if isinstance(value, Decimal):
        return float(value)
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def main():
    with connect() as conn, conn.cursor() as cur:
        as_of = one(cur, "select max(order_date)::date from analytics.fact_orders")
        daily = rows(cur, """
            select date_day, total_orders, gross_revenue, net_revenue,
                   average_order_value, fulfillment_rate, cancellation_rate,
                   gross_revenue_7d_ma, total_orders_7d_ma
            from analytics.revenue_daily
            where date_day > %s
            order by date_day""", (as_of - timedelta(days=90),))
        data = {
            "as_of": as_of.isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "pipeline": {
                "last_run": one(cur, "select max(end_time) from analytics_logs.dbt_run_log"),
                "raw_loaded_at": one(cur, "select max(ingestion_timestamp) from raw.raw_orders"),
                "layers": layer_counts(cur),
                "dbt": dbt_summary(),
            },
            "daily": daily,
            "windows": {
                str(d): {"metrics": window_metrics(cur, as_of, d), **window_breakdowns(cur, as_of, d)}
                for d in WINDOWS
            },
        }

    out = HERE / "data.js"
    out.write_text("window.DASHBOARD_DATA = " + json.dumps(data, default=plain, indent=1) + ";\n", encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KB, as of {as_of})")


if __name__ == "__main__":
    main()
