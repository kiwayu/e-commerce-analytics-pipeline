# E-commerce ETL Pipeline - Docker Setup Script for Windows
# This script sets up the required environment for running the Airflow Docker Compose

Write-Host "Setting up E-commerce ETL Pipeline environment..." -ForegroundColor Green

# Create required directories
Write-Host "Creating volume directories..." -ForegroundColor Yellow
$directories = @(
    "volumes\postgres-airflow-data",
    "volumes\postgres-warehouse-data", 
    "volumes\redis-data",
    "volumes\airflow-data",
    "volumes\pgadmin-data"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Cyan
    } else {
        Write-Host "Directory already exists: $dir" -ForegroundColor Gray
    }
}

# Set permissions (Windows equivalent)
Write-Host "Setting up permissions..." -ForegroundColor Yellow

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    
    $envContent = @"
# E-commerce ETL Pipeline - Environment Configuration
AIRFLOW_UID=50000
AIRFLOW_PROJ_DIR=.

# Airflow Web UI
AIRFLOW_WEBSERVER_PORT=8080
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=airflow123

# Security (Generate proper keys for production)
AIRFLOW_FERNET_KEY=
AIRFLOW_WEBSERVER_SECRET_KEY=

# Database Passwords
AIRFLOW_POSTGRES_PASSWORD=airflow123
DWH_POSTGRES_PASSWORD=ecommerce123

# Ports
AIRFLOW_POSTGRES_PORT=5433
DWH_POSTGRES_PORT=5432
REDIS_PORT=6379
FLOWER_PORT=5555
PGADMIN_PORT=5050

# Admin Tools
FLOWER_BASIC_AUTH=admin:flower123
PGADMIN_EMAIL=admin@ecommerce.com
PGADMIN_PASSWORD=admin123

# Data Warehouse
DWH_POSTGRES_DB=ecommerce
DWH_POSTGRES_USER=ecommerce_user

# AWS (Update with your credentials)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET=ecommerce-data-lake

# Spark
SPARK_MASTER_URL=local[*]
SPARK_DRIVER_MEMORY=2g
SPARK_EXECUTOR_MEMORY=2g

# Environment
LOG_LEVEL=INFO
ENVIRONMENT=development
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "Created .env file. Please review and update the values as needed." -ForegroundColor Green
} else {
    Write-Host ".env file already exists" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review and update the .env file with your configuration"
Write-Host "2. Generate Fernet key: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
Write-Host "3. Start services: docker-compose up -d"
Write-Host "4. Access Airflow UI: http://localhost:8080 (admin/airflow123)"
Write-Host "5. Access PgAdmin: docker-compose --profile admin up -d && http://localhost:5050"
Write-Host "6. Access Flower: docker-compose --profile flower up -d && http://localhost:5555"
Write-Host ""
Write-Host "For more information, see the README.md file" -ForegroundColor Cyan
