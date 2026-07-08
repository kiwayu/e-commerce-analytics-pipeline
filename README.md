# E-commerce Analytics ETL Pipeline

A local-first ETL pipeline for e-commerce analytics using Apache Airflow, dbt, and PostgreSQL, orchestrated with Docker Compose.

## Architecture

- **Orchestration**: Apache Airflow 2.7 (CeleryExecutor: webserver, scheduler, worker, triggerer, Redis)
- **Transformation**: dbt-core 1.6 (staging → intermediate → marts, 100+ schema tests)
- **Storage**: PostgreSQL 15 (separate metadata DB and data warehouse)
- **Ingestion**: Custom incremental replication operator (watermark-based upsert), plus optional API/PySpark file ingestion
- **Quality**: dbt tests + SQL business-metric validation (Great Expectations checkpoints are a stretch goal)

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
docker exec airflow-webserver bash -c "
  airflow pools set ingestion_pool 3 'Parallel ingestion tasks' &&
  airflow pools set transformation_pool 2 'dbt transformation tasks' &&
  airflow pools set validation_pool 2 'Data validation tasks' &&
  airflow variables set dbt_profiles_dir /opt/airflow/dbt &&
  airflow variables set ge_config_path /opt/airflow/great_expectations &&
  airflow variables set slack_webhook_url ''
"

# Run the pipeline
docker exec airflow-webserver airflow dags unpause daily_etl_pipeline
docker exec airflow-webserver airflow dags trigger daily_etl_pipeline
```

Access:
- Airflow UI: http://localhost:8080 (credentials from `.env`)
- Warehouse: `localhost:5432`, database `ecommerce`
- Flower (optional): `docker compose --profile flower up -d`, then http://localhost:5555
- pgAdmin (optional): `docker compose --profile admin up -d`, then http://localhost:5050

## Data Pipeline

The `daily_etl_pipeline` DAG runs:

1. **Prerequisite validation** — database connectivity, disk space, required variables
2. **Ingestion** — incremental replication `raw.raw_customers` → `staging.customers` (watermark upsert). API and PySpark file ingestion are optional and skip cleanly when their dependencies aren't installed
3. **Transformation** — dbt staging → intermediate → marts, then `dbt test`
4. **Validation** — SQL business-metric checks against `analytics.fact_orders`
5. **Notifications** — log-based by default; Slack alerts activate with `ENABLE_SLACK_ALERTS=true` and a `slack_webhook` connection

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

## Security Notes

- No secrets in version control — `.env` is gitignored, `.env.example` holds placeholders
- Default dev credentials are for local use only; generate proper Fernet/webserver keys for anything shared
- Use IAM roles and a secrets manager for production deployments

## Roadmap

- Great Expectations checkpoint suite for the marts layer
- PySpark file ingestion enabled in-container
- External API ingestion with configurable sources
- CI: dbt build + DAG import checks on pull requests
