# How the pipeline works

This is the design behind the repository, written for someone who wants to understand the moving parts before reading the code.

## The shape of it

One Airflow DAG, `daily_etl_pipeline`, runs at 02:00 UTC and walks a dataset from raw landing tables to analytics marts in PostgreSQL. The stages are:

1. **Prerequisite checks.** A Python task confirms the warehouse is reachable, there is disk to work with, and the environment variables the run needs are present. A missing prerequisite fails fast rather than halfway through a load.
2. **Ingestion, in parallel.** Three tasks run side by side inside a task group: an API ingestion job that pages through an orders endpoint with rate limiting and retries, a file ingestion job for CSV and Parquet drops (PySpark when it is installed, skipped cleanly when it is not), and an incremental database replication from `raw.raw_customers` into `staging.customers`.
3. **Transformation with dbt.** Three Bash tasks run `dbt run` for the staging, intermediate and marts layers in turn, then `dbt test` runs the schema and data tests.
4. **Validation.** A Python task runs the data quality checks, and a SQL task runs business metric assertions against `analytics.fact_orders`, for example that yesterday's order count sits inside an expected band.
5. **Notification.** On success a summary is logged, and Slack alerts fire if a webhook connection is configured.

The DAG carries a four hour SLA for the whole run.

## Incremental replication

The replication operator is the part of the project with the most engineering in it. It copies rows from a source table into a target table using a watermark column, by default `ingestion_timestamp`:

- The last watermark is read from an Airflow Variable keyed by table and column, so each run only asks the source for rows newer than the previous run saw.
- Rows are pulled in batches and upserted into the target on its primary key, so re-running a day is safe and idempotent.
- When the batch succeeds the watermark advances. A failed batch leaves the watermark where it was, so the next run picks up the same rows again.
- A validation operator runs before and after the copy, comparing row counts and checking for nulls in key columns, and the DAG fails if the numbers do not line up.

The hook, operator and sensors live under `airflow/plugins/` and are plain Airflow provider code: the hook wraps the Postgres provider's hook, the operator extends `BaseOperator`, and the sensors extend `BaseSensorOperator`.

## Warehouse layout

`sql/schema_init.sql` creates five schemas that mirror the dbt layers:

| Schema | Holds |
|---|---|
| `raw` | Landed records exactly as received, with a record hash, a batch id and an ingestion timestamp on every row |
| `staging` | Typed, deduplicated copies of the raw tables |
| `intermediate` | Joins and per-customer rollups |
| `marts` | Dimensional models for finance and marketing |
| `analytics` | The fact table the validation checks read |

The dbt project has staging models for orders, customers and shipments, two intermediate models (customer order metrics, and orders joined to shipments), and marts for `dim_customers`, `fact_orders`, daily revenue and customer segmentation.

## Running it

Everything runs from one Docker Compose file under `airflow/`: PostgreSQL for the Airflow metadata database, a second PostgreSQL for the warehouse, Redis as the Celery broker, and the Airflow 3 services (API server, scheduler, DAG processor, Celery worker and triggerer). Optional profiles add Flower and pgAdmin.

## Testing

- `spark/tests` unit tests the API client configuration, rate limiting and retry maths, order validation, and the ingestion service with the database mocked. CI runs these on every push.
- `airflow/test_dag_structure.py` imports the DAG with the operators patched out and checks the task graph, schedule and configuration.
- CI also installs Airflow 3.3 on Ubuntu and parses the DAG folder, so a broken import never reaches `main`.

## Decisions worth knowing

- **Watermarks live in Airflow Variables**, not in a control table, so the replication state is visible and editable from the Airflow UI without touching the warehouse.
- **dbt runs as Bash tasks** rather than through an integration package, which keeps the Airflow image small and the dbt invocation identical to what you run locally.
- **Optional dependencies skip rather than fail.** PySpark and the Slack provider are detected at import time so the pipeline runs on a laptop without either.
