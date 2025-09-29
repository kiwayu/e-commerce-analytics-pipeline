# E-commerce Analytics ETL Pipeline

WORK IN PROGRESS

A production-grade ETL pipeline for e-commerce analytics using Apache Airflow, dbt, PySpark, and Great Expectations.

## Architecture

- Orchestration: Apache Airflow 2.7
- Transformation: dbt-core
- Processing: PySpark 3.4
- Quality: Great Expectations
- Storage: PostgreSQL (warehouse), S3 (data lake)
- Infrastructure: Docker Compose

## Project Structure

```
ecommerce-etl-pipeline/
├── airflow/
│   ├── dags/
│   ├── plugins/
│   └── docker-compose.yml
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── tests/
│   └── dbt_project.yml
├── spark/
│   ├── jobs/
│   └── utils/
├── great_expectations/
│   ├── expectations/
│   └── checkpoints/
├── infra/
│   ├── terraform/
│   └── docker/
├── sql/
├── notebooks/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Quick Start

Prerequisites: Python 3.9+, Docker, Docker Compose, Git

```bash
# Clone and setup
git clone <repository-url>
cd ecommerce-etl-pipeline
cp .env.example .env
pip install -r requirements.txt

# Start services
cd airflow
docker-compose up -d

# Setup dbt
cd ../dbt
dbt deps
dbt debug
dbt run
```

Access: Airflow UI (http://localhost:8080, admin/airflow), Flower (http://localhost:5555), PostgreSQL (localhost:5432)

## Configuration

Key environment variables (.env):
```bash
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=ecommerce
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=your-data-lake-bucket
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=secure_password
```

## Data Pipeline

Daily ETL: Extract from sources, load to S3, transform with PySpark/dbt, validate with Great Expectations, load to PostgreSQL

Hourly Stream: Real-time ingestion of order events, user behavior, inventory updates, payment events

Data Quality: Schema validation, freshness checks, business rule validation, statistical profiling

## Testing

```bash
# Python tests
pytest
pytest --cov=src --cov-report=html

# dbt tests
cd dbt && dbt test

# DAG tests
python -m pytest tests/dags/
```

## Deployment

Local: Use Docker Compose

Production: Kubernetes (Helm), AWS MWAA, GCP Cloud Composer, or Azure Data Factory

Infrastructure as Code:
```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

## Monitoring

- Airflow Web UI and Flower for workflow monitoring
- Great Expectations data docs for quality monitoring
- Structured logging with correlation IDs
- Health check endpoints

## Security

- Never commit secrets to version control
- Use IAM roles with least-privilege access
- Implement VPC and security groups
- Enable encryption at rest and in transit
- Use AWS Secrets Manager for production credentials
- Implement RBAC for Airflow

## Development

Adding DAGs: Create in airflow/dags/, follow naming convention, test locally

Adding dbt Models: Create in dbt/models/, add schema tests, document columns, run dbt test

Adding Spark Jobs: Create in spark/jobs/, follow best practices, include error handling

## Documentation

- Apache Airflow: https://airflow.apache.org/docs/
- dbt: https://docs.getdbt.com/
- PySpark: https://spark.apache.org/docs/latest/api/python/
- Great Expectations: https://docs.greatexpectations.io/
