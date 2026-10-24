# E-commerce Analytics ETL Pipeline

[![CI](https://github.com/kiwayu/e-commerce-analytics-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/kiwayu/e-commerce-analytics-pipeline/actions/workflows/ci.yml)

A local-first ETL pipeline for e-commerce analytics using Apache Airflow, dbt, and PostgreSQL, orchestrated with Docker Compose. The marts feed a small static dashboard that is rebuilt and published on every push: https://kiwayu.github.io/e-commerce-analytics-pipeline/

## Architecture

- **Orchestration**: Apache Airflow 3.3 (CeleryExecutor: API server, scheduler, DAG processor, worker, triggerer, Redis)
- **Transformation**: dbt-core 1.6+ (staging → intermediate → marts, 100+ schema tests). Amounts arrive in five currencies and are converted to USD in staging with the `fx_rates` seed
- **Storage**: PostgreSQL 15 (separate metadata DB and data warehouse)
- **Ingestion**: Custom incremental replication operator (watermark-based upsert), plus optional API/PySpark file ingestion
- **Quality**: dbt tests + SQL business-metric validation (Great Expectations checkpoints are a stretch goal)
- **Dashboard**: plain HTML, CSS and JavaScript over a JSON export of the marts, deployed to GitHub Pages from CI

## Project Structure

```
e-commerce-analytics-pipeline/
├── airflow/
│   ├── dags/                  # daily_etl_pipeline + incremental replication DAGs
│   ├── plugins/               # custom hooks, operators, sensors
│   ├── docker-compose.yml     # full local stack
│   └── .env.example           # environment template
├── dbt/
│   ├── models/
│   │   ├── staging/           # cleaned + typed views over raw
│   │   ├── intermediate/      # business logic building blocks
│   │   └── marts/             # dim_customers, fact_orders, revenue_daily, segmentation
│   ├── macros/
│   ├── profiles.yml           # env-var driven connection profiles
│   └── dbt_project.yml
├── dashboard/
│   ├── export.py              # marts -> data.js
│   └── index.html             # static dashboard (no build step)
├── spark/                     # optional API/file ingestion jobs
├── sql/
│   ├── schema_init.sql        # warehouse schemas + raw/staging tables
│   └── seed_sample_data.sql   # reproducible synthetic sample data
└── requirements.txt
```

## Quick Start

Prerequisites: Docker with Docker Compose, ~6GB free RAM for the stack.

```bash
git clone https://github.com/kiwayu/e-commerce-analytics-pipeline
cd e-commerce-analytics-pipeline/airflow
cp .env.example .env          # adjust passwords if you like

# Start the stack (first run pulls images and pip-installs dbt in the workers)
docker compose up -d

# Seed the raw layer with synthetic sample data
docker exec -i ecommerce-data-warehouse psql -U ecommerce_user -d ecommerce \
  < ../sql/seed_sample_data.sql

# One-time Airflow setup: pools and variables used by the daily DAG
docker exec airflow-apiserver bash -c "
  airflow pools set ingestion_pool 3 'Parallel ingestion tasks' &&
  airflow pools set transformation_pool 2 'dbt transformation tasks' &&
  airflow pools set validation_pool 2 'Data validation tasks' &&
  airflow variables set dbt_profiles_dir /opt/airflow/dbt &&
  airflow variables set ge_config_path /opt/airflow/great_expectations &&
  airflow variables set slack_webhook_url ''
"

# Run the pipeline
docker exec airflow-apiserver airflow dags unpause daily_etl_pipeline
docker exec airflow-apiserver airflow dags trigger daily_etl_pipeline
```

Access:
- Airflow UI: http://localhost:8080 (credentials from `.env`)
- Warehouse: `localhost:5432`, database `ecommerce`
- Flower (optional): `docker compose --profile flower up -d`, then http://localhost:5555
- pgAdmin (optional): `docker compose --profile admin up -d`, then http://localhost:5050

## Running Without Docker

If you have PostgreSQL installed locally, the warehouse and dbt layers run on their own:

```bash
# Schema, roles and sample data (needs a superuser for the CREATE DATABASE step)
psql -U postgres -v ON_ERROR_STOP=1 -f sql/schema_init.sql
psql -U postgres -d ecommerce -v ON_ERROR_STOP=1 -f sql/seed_sample_data.sql

# dbt (Python 3.9 to 3.13)
pip install "dbt-postgres==1.9.1" "psycopg[binary]"
cd dbt
DBT_PROFILES_DIR=. DWH_POSTGRES_USER=postgres DWH_POSTGRES_PASSWORD=<your password> dbt deps
DBT_PROFILES_DIR=. DWH_POSTGRES_USER=postgres DWH_POSTGRES_PASSWORD=<your password> dbt build
cd ..

# Refresh the dashboard from the marts, then open dashboard/index.html
DWH_POSTGRES_USER=postgres DWH_POSTGRES_PASSWORD=<your password> python dashboard/export.py
```

This is the same sequence CI runs against a PostgreSQL service container before deploying the dashboard.

## Dashboard

`dashboard/` is a static page with no framework and no build step. `export.py` reads the marts with the same `DWH_POSTGRES_*` variables dbt uses and writes `data.js`: daily revenue, headline figures for the last 7, 30 and 90 days with the previous period for comparison, breakdowns by status, segment, carrier and country, and the row counts and dbt results for the pipeline strip at the top. The page renders its charts as inline SVG and every chart has a table view.

The committed `data.js` is a snapshot from a local run so the page works straight from a checkout. The `dbt-build` CI job regenerates it and the `deploy-dashboard` job publishes the folder to GitHub Pages on pushes to `main`.

## Data Pipeline

A longer walkthrough of the design is in [docs/how-it-works.md](docs/how-it-works.md).


The `daily_etl_pipeline` DAG runs:

1. **Prerequisite validation**: database connectivity, disk space, required variables
2. **Ingestion**: incremental replication `raw.raw_customers` → `staging.customers` (watermark upsert). API and PySpark file ingestion are optional and skip cleanly when their dependencies aren't installed
3. **Transformation**: dbt staging → intermediate → marts, then `dbt test`
4. **Validation**: SQL business-metric checks against `analytics.fact_orders`
5. **Notifications**: log-based by default; Slack alerts activate with `ENABLE_SLACK_ALERTS=true` and a `slack_webhook` connection

## Running dbt Standalone

```bash
docker run --rm --network ecommerce-etl-network \
  -v "$(pwd)/dbt:/usr/app/dbt" -w /usr/app/dbt \
  -e DBT_PROFILES_DIR=/usr/app/dbt \
  -e DWH_POSTGRES_HOST=postgres-warehouse \
  -e DWH_POSTGRES_PASSWORD=ecommerce123 \
  ghcr.io/dbt-labs/dbt-postgres:1.6.6 build
```

Expected: 9 models built, 107 tests passed.

## Configuration

All configuration lives in `airflow/.env` (see `.env.example`). Key variables:

| Variable | Purpose |
|---|---|
| `DWH_POSTGRES_*` | Warehouse connection (host, port, db, user, password) |
| `AIRFLOW_POSTGRES_PASSWORD` | Airflow metadata DB password |
| `_AIRFLOW_WWW_USER_*` | Airflow UI admin credentials |
| `_PIP_ADDITIONAL_REQUIREMENTS` | Extra packages for Airflow containers (installs dbt) |
| `AWS_*` / `S3_BUCKET` | Optional S3 data lake settings |

## Testing

```bash
# dbt models + schema tests (see "Running dbt Standalone" above)
dbt build

# DAG structure tests
cd airflow && python -m pytest test_dag_structure.py
```

CI runs the Spark unit tests, parses the Airflow DAG folder, and builds the dbt project end to end (schema, seed, `dbt build`, dashboard export) against a PostgreSQL 15 service container.

## Security Notes

- No secrets in version control: `.env` is gitignored, `.env.example` holds placeholders
- Default dev credentials are for local use only; generate proper Fernet/webserver keys for anything shared
- `schema_init.sql` creates the `etl_user` and `analytics_user` roles without login or passwords. Enable them per environment with `ALTER ROLE etl_user LOGIN PASSWORD '...'` rather than committing a password
- Use IAM roles and a secrets manager for production deployments

## Roadmap

- Great Expectations checkpoint suite for the marts layer
- PySpark file ingestion enabled in-container
- External API ingestion with configurable sources
