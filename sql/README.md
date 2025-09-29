# E-commerce Analytics Database Schema

## Overview

This directory contains a comprehensive, production-ready database schema for an e-commerce analytics data warehouse. The schema implements modern data engineering best practices including dimensional modeling, change data capture, data quality monitoring, and performance optimization.

## Files

### Core Schema Files

| File | Description |
|------|-------------|
| `schema_init.sql` | **Main DDL script** - Complete database schema creation |
| `validate_schema.sql` | Schema validation and testing script |
| `schema_documentation.md` | Comprehensive documentation and usage guide |

### Schema Components

## 📊 **Database Tables Created**

### Raw Layer (Landing Zone)
- ✅ **`raw.raw_orders`** - Unprocessed order data with JSONB support
- ✅ **`raw.raw_customers`** - Customer data from various source systems  
- ✅ **`raw.raw_shipments`** - Shipping and logistics information

### Staging Layer (Processing Zone)
- ✅ **`staging.staging_orders_incremental`** - CDC-enabled incremental processing table
- ✅ **`staging.orders`** - Cleaned and validated order data
- ✅ **`staging.order_items`** - Order line items with product details
- ✅ **`staging.customers`** - Standardized customer information
- ✅ **`staging.products`** - Product master data
- ✅ **`staging.shipments`** - Processed shipping information

### Marts Layer (Analytics Zone)
- ✅ **`marts.dim_customers`** - Customer dimension (SCD Type 2)
- ✅ **`marts.dim_products`** - Product dimension (SCD Type 2)  
- ✅ **`marts.fact_orders`** - Central orders fact table
- ✅ **`marts.dim_date`** - Date dimension (pre-populated)

### Analytics Layer (Monitoring)
- ✅ **`analytics.etl_job_log`** - ETL process monitoring
- ✅ **`analytics.data_quality_results`** - Data quality tracking

## 🔧 **Advanced Features Implemented**

### Change Data Capture (CDC)
```sql
-- staging_orders_incremental supports full CDC operations
operation_type: INSERT | UPDATE | DELETE
record_version: Auto-incrementing version control
is_current: Current record flag
effective_from/effective_to: Temporal validity
```

### Data Quality Framework
- **Automated Quality Scoring**: 0.00-1.00 scale based on nulls, invalids, duplicates
- **Constraint Validation**: Email formats, currency codes, business rules
- **Error Tracking**: JSONB storage of validation errors
- **Record Hashing**: SHA-256 for deduplication

### Performance Optimization
- **70+ Strategic Indexes**: Covering all query patterns
- **Composite Indexes**: For complex analytical queries
- **Partial Indexes**: For selective filtering
- **JSONB GIN Indexes**: For semi-structured data queries
- **Full-Text Search**: For product name searches

### Business Intelligence Features
- **Slowly Changing Dimensions**: Type 2 SCD for customers and products
- **Calculated Fields**: Age groups, customer tiers, profit margins
- **Geographic Mapping**: Automatic region assignment
- **Customer Analytics**: CLV, segmentation, purchase patterns
- **Marketing Attribution**: Campaign tracking and referrer analysis

## 🛠️ **Utility Functions Created**

### Data Processing Functions
```sql
calculate_age_group(date_of_birth)           -- Age group classification
calculate_customer_tier(clv)                 -- Customer tier assignment  
get_region_from_country(country_code)        -- Geographic region mapping
generate_record_hash(data_text)              -- SHA-256 hashing
is_valid_email(email_address)               -- Email validation
clean_phone_number(phone_input)             -- Phone standardization
calculate_data_quality_score(...)           -- Quality assessment
```

### ETL Integration Functions
```sql
log_etl_job_start(job_name, job_type, ...)  -- Start job logging
log_etl_job_end(job_id, status, ...)        -- Complete job logging
```

## 🔄 **Automated Triggers**

### Data Maintenance Triggers
- **Updated Timestamp**: Auto-update `updated_at` on all staging/marts tables
- **Derived Fields**: Auto-calculate age groups, tiers, regions, profit margins
- **Version Management**: Auto-increment versions in incremental tables
- **Data Validation**: Auto-populate quality scores and validation flags

### Business Logic Triggers
- **Customer Dimension**: Auto-calculate tier, age group, region, full name
- **Product Dimension**: Auto-calculate profit margins
- **Orders Fact**: Auto-calculate totals and customer flags
- **Incremental Staging**: Auto-manage record versioning and current flags

## 📈 **Key Business Metrics Supported**

### Customer Analytics
- Customer Lifetime Value (CLV)
- Customer Segmentation (New, Bronze, Silver, Gold, Platinum)
- Age Group Analysis
- Geographic Distribution
- Purchase Behavior Patterns

### Product Analytics  
- Profit Margin Analysis
- Category Performance
- Product Lifecycle Tracking
- Inventory Status Monitoring

### Order Analytics
- Revenue Tracking
- Order Value Trends
- Channel Performance
- Geographic Sales Analysis
- Customer Journey Mapping

## 🔍 **Data Quality & Monitoring**

### Built-in Quality Checks
- Email format validation (RFC 5321 compliant)
- Currency code validation (ISO 4217)
- Country code validation (ISO 3166-1)
- Positive amount constraints
- Date logic validation
- Record deduplication via hashing

### Monitoring Capabilities
- ETL job execution tracking
- Data quality score monitoring
- Constraint violation logging
- Performance metrics collection

## 🚀 **Usage Instructions**

### 1. Schema Deployment
```bash
# Deploy to data warehouse
psql -h localhost -p 5432 -U ecommerce_user -d ecommerce -f schema_init.sql

# Validate deployment
psql -h localhost -p 5432 -U ecommerce_user -d ecommerce -f validate_schema.sql
```

### 2. Docker Integration
The schema is automatically initialized when using the Docker Compose setup:
```bash
cd airflow
docker-compose up -d
# Schema is automatically applied to postgres-warehouse container
```

### 3. Common Query Patterns
```sql
-- Customer lifetime value analysis
SELECT customer_tier, COUNT(*), AVG(customer_lifetime_value)
FROM marts.dim_customers 
WHERE is_current = TRUE
GROUP BY customer_tier;

-- Incremental processing
SELECT * FROM staging.staging_orders_incremental 
WHERE updated_at > '2024-01-01' AND is_current = TRUE;

-- Order trends analysis  
SELECT d.year, d.month_name, COUNT(*), SUM(total_amount)
FROM marts.fact_orders fo
JOIN marts.dim_date d ON fo.order_date_key = d.date_key
GROUP BY d.year, d.month, d.month_name;
```

## 📋 **Schema Statistics**

| Component | Count | Description |
|-----------|-------|-------------|
| **Schemas** | 5 | raw, staging, intermediate, marts, analytics |
| **Tables** | 14 | Complete data pipeline tables |
| **Indexes** | 70+ | Performance-optimized indexes |
| **Functions** | 12 | Utility and business logic functions |
| **Triggers** | 15+ | Automated data maintenance |
| **Constraints** | 50+ | Data quality and business rules |

## 🔒 **Security & Compliance**

### Role-Based Access Control
- **etl_user**: Full read/write access to raw and staging layers
- **analytics_user**: Read-only access to marts layer  
- **Schema-level permissions**: Granular access control

### Data Privacy Features
- Marketing consent tracking
- Email opt-in management
- GDPR compliance ready
- Data anonymization support

## 🔧 **Maintenance & Operations**

### Regular Maintenance
- Date dimension: Pre-populated with 3 years of dates
- Statistics: Auto-updated via triggers
- Constraints: Comprehensive validation rules
- Monitoring: Built-in ETL and quality tracking

### Performance Recommendations
- Use business keys for inter-layer joins
- Leverage built-in quality functions
- Monitor incremental processing patterns
- Implement data retention policies
- Regular index maintenance

## 📚 **Additional Resources**

- **Full Documentation**: See `schema_documentation.md`
- **Validation Script**: Run `validate_schema.sql` for testing
- **Docker Setup**: Use `../airflow/docker-compose.yml` for local deployment
- **dbt Integration**: Compatible with dbt transformations

---

This schema provides a robust foundation for enterprise-grade e-commerce analytics with production-ready features for data quality, performance, and operational monitoring.
