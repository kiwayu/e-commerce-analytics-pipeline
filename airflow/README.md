# Airflow Docker Compose Setup

This directory contains a production-ready Docker Compose configuration for Apache Airflow with separate PostgreSQL databases for metadata and data warehouse, Redis for message brokering, and optional monitoring tools.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Airflow Web   │    │  Airflow Sched  │    │ Airflow Worker  │
│   (Port 8080)   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────────────────────┼─────────────────────────────────┐
│                    Airflow Network                                │
├─────────────────┬───────────────┼───────────────┬─────────────────┤
│ PostgreSQL Meta │   Redis       │               │ PostgreSQL DWH  │
│ (Port 5433)     │ (Port 6379)   │               │ (Port 5432)     │
│ airflow_meta    │ Celery Broker │               │ ecommerce       │
└─────────────────┴───────────────┘               └─────────────────┘
```

## 🚀 Quick Start

### 1. Setup Environment

**Windows:**
```powershell
.\setup.ps1
```

**Linux/Mac:**
```bash
# Create directories
mkdir -p volumes/{postgres-airflow-data,postgres-warehouse-data,redis-data,airflow-data,pgadmin-data}

# Set permissions
chmod 777 volumes/*

# Copy environment file
cp .env.example .env
```

### 2. Configure Environment

Edit the `.env` file with your configuration:

```bash
# Required: Generate Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Update .env with the generated key
AIRFLOW_FERNET_KEY=your_generated_key_here
```

### 3. Start Services

```bash
# Start core services
docker-compose up -d

# Start with monitoring (optional)
docker-compose --profile flower up -d

# Start with database admin (optional)
docker-compose --profile admin up -d
```

### 4. Access Services

| Service | URL | Credentials |
|---------|-----|------------|
| Airflow Web UI | http://localhost:8080 | admin / airflow123 |
| PgAdmin | http://localhost:5050 | admin@ecommerce.com / admin123 |
| Flower (Celery) | http://localhost:5555 | admin / flower123 |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AIRFLOW_UID` | User ID for file permissions | 50000 |
| `AIRFLOW_WEBSERVER_PORT` | Airflow web UI port | 8080 |
| `AIRFLOW_POSTGRES_PASSWORD` | Metadata DB password | airflow123 |
| `DWH_POSTGRES_PASSWORD` | Data warehouse password | ecommerce123 |
| `REDIS_PASSWORD` | Redis password (optional) | (empty) |

### Database Connections

The compose file automatically creates Airflow connections:

```python
# In your DAGs, use these connection IDs:
postgres_dwh_conn = "postgres_dwh"  # Data warehouse
redis_conn = "redis_default"        # Redis cache
```

### Persistent Volumes

All data is persisted in local volumes:

```
volumes/
├── postgres-airflow-data/    # Airflow metadata
├── postgres-warehouse-data/  # Data warehouse
├── redis-data/              # Redis cache
├── airflow-data/            # Shared Airflow data
└── pgadmin-data/            # PgAdmin settings
```

## 🗄️ Database Setup

### Automatic Initialization

The data warehouse PostgreSQL instance automatically:
1. Creates the `ecommerce` database
2. Runs `../sql/schema_init.sql` to set up schemas and tables
3. Creates roles: `etl_user` and `analytics_user`

### Manual Connection

Connect to databases directly:

```bash
# Airflow metadata
docker exec -it airflow-postgres-metadata psql -U airflow -d airflow

# Data warehouse
docker exec -it ecommerce-data-warehouse psql -U ecommerce_user -d ecommerce
```

## 🔍 Monitoring

### Health Checks

All services include health checks:
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- Airflow services: HTTP endpoints

### Logs

View service logs:

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs airflow-scheduler
docker-compose logs postgres-warehouse

# Follow logs
docker-compose logs -f airflow-webserver
```

### Flower (Celery Monitoring)

Enable Celery worker monitoring:

```bash
docker-compose --profile flower up -d
```

Access at http://localhost:5555

## 🛠️ Management Commands

### Airflow CLI

```bash
# Access Airflow CLI
docker-compose run --rm airflow-cli bash

# Run specific commands
docker exec airflow-webserver airflow dags list
docker exec airflow-webserver airflow tasks test my_dag my_task 2023-01-01
```

### Database Management

```bash
# Backup data warehouse
docker exec ecommerce-data-warehouse pg_dump -U ecommerce_user ecommerce > backup.sql

# Restore data warehouse
docker exec -i ecommerce-data-warehouse psql -U ecommerce_user ecommerce < backup.sql
```

### Scaling Workers

```bash
# Scale Celery workers
docker-compose up -d --scale airflow-worker=3
```

## 🔒 Security

### Production Considerations

1. **Change default passwords** in `.env`
2. **Generate strong Fernet key**
3. **Enable Redis password**
4. **Use SSL/TLS termination**
5. **Implement network policies**
6. **Use external secret management**

### Network Security

The setup uses a custom Docker network with subnet isolation:
- Network: `ecommerce-etl-network`
- Subnet: `172.20.0.0/16`

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Update ports in `.env`
2. **Permission errors**: Check `AIRFLOW_UID` setting
3. **Database connection**: Verify network connectivity
4. **Memory issues**: Increase Docker memory limits

### Reset Environment

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove containers and networks
docker-compose down --remove-orphans

# Restart fresh
docker-compose up -d
```

### Debug Mode

```bash
# Start with debug profile
docker-compose --profile debug up -d

# Access CLI for debugging
docker-compose run --rm airflow-cli bash
```

## 📝 Development

### Adding Custom Plugins

Place plugins in `./plugins/` directory:

```
plugins/
├── operators/
├── sensors/
└── hooks/
```

### Custom DAGs

Place DAGs in `./dags/` directory:

```
dags/
├── extract/
├── transform/
└── load/
```

### Environment-Specific Configs

Use different `.env` files for environments:

```bash
# Development
cp .env.dev .env

# Staging
cp .env.staging .env

# Production
cp .env.production .env
```

## 📚 Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Redis Docker Image](https://hub.docker.com/_/redis)

---

For project-wide documentation, see the main [README.md](../README.md) file.
