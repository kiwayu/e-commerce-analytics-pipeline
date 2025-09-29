# E-commerce Analytics ETL Pipeline

#WORK IN PROGRESS

A production-grade ETL pipeline for e-commerce analytics using Apache Airflow, dbt, PySpark, and Great Expectations.

## 🏗️ Architecture Overview

This pipeline implements a modern data architecture with the following components:

- **Orchestration**: Apache Airflow 2.7 for workflow management
- **Transformation**: dbt-core for data modeling and transformations
- **Processing**: PySpark 3.4 for big data processing
- **Quality**: Great Expectations for data validation and monitoring
- **Storage**: PostgreSQL for data warehouse, S3 for data lake
- **Infrastructure**: Docker Compose for local development

## 📁 Project Structure

```
ecommerce-etl-pipeline/
├── airflow/                     # Airflow configuration and DAGs
│   ├── dags/                    # Airflow DAG definitions
│   │   ├── daily_etl_pipeline.py
│   │   └── hourly_stream_ingestion.py
│   ├── plugins/                 # Custom Airflow plugins
│   └── docker-compose.yml       # Airflow Docker setup
├── dbt/                         # dbt project for data transformations
│   ├── models/                  # dbt models
│   │   ├── staging/             # Raw data staging models
│   │   ├── intermediate/        # Intermediate transformation models
│   │   └── marts/               # Business logic and final models
│   ├── tests/                   # dbt data tests
│   └── dbt_project.yml          # dbt configuration
├── spark/                       # PySpark jobs and utilities
│   ├── jobs/                    # Spark job definitions
│   │   ├── incremental_loader.py
│   │   └── deduplication.py
│   └── utils/                   # Spark utility functions
├── great_expectations/          # Data quality validation
│   ├── expectations/            # Data quality expectations
│   └── checkpoints/             # Validation checkpoints
├── infra/                       # Infrastructure as code
│   ├── terraform/               # Terraform configurations (optional)
│   └── docker/                  # Docker configurations
├── sql/                         # SQL scripts and schema definitions
│   └── schema_init.sql
├── notebooks/                   # Jupyter notebooks for exploration
├── tests/                       # Python tests
├── .env.example                 # Environment configuration template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ 
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce-etl-pipeline
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration values
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the infrastructure**
   ```bash
   cd airflow
   docker-compose up -d
   ```

5. **Access the services**
   - Airflow Web UI: http://localhost:8080 (admin/airflow)
   - Flower (Celery monitoring): http://localhost:5555
   - PostgreSQL: localhost:5432

### Development Setup

1. **Initialize the database**
   ```bash
   # Database will be automatically initialized via Docker
   # Check airflow/docker-compose.yml for configuration
   ```

2. **Set up dbt**
   ```bash
   cd dbt
   dbt deps
   dbt debug
   dbt run
   ```

3. **Validate Great Expectations setup**
   ```bash
   cd great_expectations
   great_expectations init
   ```

## 🔧 Configuration

### Environment Variables

Key environment variables to configure (see `.env.example`):

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=ecommerce

# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=your-data-lake-bucket

# Airflow
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=secure_password
```

### Database Setup

The pipeline uses PostgreSQL for both Airflow metadata and the data warehouse. Schema initialization is handled automatically via Docker.

### AWS Configuration

For production deployment, configure:
- S3 buckets for data lake storage
- IAM roles with appropriate permissions
- VPC and security groups for secure access

## 📊 Data Pipeline

### Daily ETL Pipeline

The main ETL pipeline (`daily_etl_pipeline.py`) performs:

1. **Extract**: Pull data from various e-commerce sources
2. **Load**: Store raw data in S3 data lake
3. **Transform**: Process data using PySpark and dbt
4. **Validate**: Run Great Expectations data quality checks
5. **Load**: Store processed data in PostgreSQL warehouse

### Hourly Stream Processing

Real-time data ingestion (`hourly_stream_ingestion.py`) handles:
- Order events
- User behavior tracking
- Inventory updates
- Payment processing events

### Data Quality

Great Expectations ensures data quality through:
- Schema validation
- Data freshness checks
- Business rule validation
- Statistical profiling

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

### dbt Tests

```bash
cd dbt
dbt test
```

### Airflow DAG Tests

```bash
# Test DAG integrity
python -m pytest tests/dags/
```

## 🚀 Deployment

### Local Development

Use Docker Compose for local development:

```bash
cd airflow
docker-compose up -d
```

### Production Deployment

For production, consider:

1. **Kubernetes**: Deploy using Helm charts
2. **AWS**: Use Amazon MWAA (Managed Airflow)
3. **GCP**: Use Cloud Composer
4. **Azure**: Use Azure Data Factory + Airflow

### Infrastructure as Code

Optional Terraform configurations in `infra/terraform/`:

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

## 📈 Monitoring and Observability

### Airflow Monitoring

- Web UI dashboard at http://localhost:8080
- Flower for Celery worker monitoring
- Built-in task logs and metrics

### Data Quality Monitoring

- Great Expectations data docs
- Slack/email alerts for failed validations
- Custom metrics and dashboards

### Application Monitoring

- Structured logging with correlation IDs
- Prometheus metrics (optional)
- Health check endpoints

## 🔒 Security

### Security Best Practices

1. **Environment Variables**: Never commit secrets to version control
2. **IAM Roles**: Use least-privilege access principles
3. **Network Security**: Implement VPC and security groups
4. **Encryption**: Enable encryption at rest and in transit
5. **Access Control**: Implement RBAC for Airflow

### Secrets Management

For production:
- Use AWS Secrets Manager or similar
- Rotate credentials regularly
- Audit access patterns

## 🛠️ Development

### Adding New DAGs

1. Create DAG file in `airflow/dags/`
2. Follow naming convention: `{frequency}_{purpose}_pipeline.py`
3. Include proper documentation and testing
4. Test locally before deployment

### Adding dbt Models

1. Create model in appropriate `dbt/models/` subdirectory
2. Add schema tests in `schema.yml`
3. Document model purpose and columns
4. Run `dbt run` and `dbt test`

### Adding Spark Jobs

1. Create job in `spark/jobs/`
2. Follow PySpark best practices
3. Include error handling and logging
4. Test with sample data

## 📚 Documentation

### Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [dbt Documentation](https://docs.getdbt.com/)
- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [Great Expectations Documentation](https://docs.greatexpectations.io/)

### API Documentation

Auto-generated API docs available at:
- Airflow API: http://localhost:8080/api/v1/
- Custom API endpoints: http://localhost:8080/api/v1/custom/

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use Black for code formatting
- Include type hints where appropriate
- Write comprehensive docstrings

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Docker Permission Issues**: Set AIRFLOW_UID environment variable
2. **Database Connection**: Check PostgreSQL connection parameters
3. **Memory Issues**: Increase Docker memory allocation
4. **Port Conflicts**: Ensure ports 5432, 8080, 6379 are available

### Getting Help

- Check the GitHub Issues for known problems
- Review Airflow logs: `docker-compose logs airflow-scheduler`
- Validate configuration: `airflow config list`

### Performance Tuning

- Adjust worker memory in Docker Compose
- Optimize Spark configurations for your data size
- Monitor and tune database connections
- Consider data partitioning strategies

---

**Note**: This is a template project. Customize the configuration, add your specific business logic, and adapt the infrastructure to your needs.
