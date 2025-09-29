# E-commerce Analytics Database Schema Documentation

## Overview

This document describes the comprehensive database schema for the e-commerce analytics data warehouse. The schema is designed using dimensional modeling principles and supports both batch and incremental data processing patterns.

## Schema Architecture

### Schema Layers

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Raw Layer     │    │ Staging Layer   │    │  Marts Layer    │
│                 │    │                 │    │                 │
│ - raw_orders    │    │ - staging_*     │    │ - dim_*         │
│ - raw_customers │───▶│ - staging_*_    │───▶│ - fact_*        │
│ - raw_shipments │    │   incremental   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   Landing Zone          Processing Zone           Analytics Zone
```

## Table Descriptions

### Raw Layer Tables

#### `raw.raw_orders`
**Purpose**: Stores unprocessed order data from source systems  
**Key Features**:
- JSONB support for flexible order item storage
- Record hashing for deduplication
- Data quality tracking with validation errors
- Support for multiple source systems

**Important Fields**:
- `order_id`: Business key from source system
- `order_items`: JSONB array of order line items
- `record_hash`: SHA-256 hash for deduplication
- `is_valid`: Data quality flag
- `validation_errors`: JSONB array of validation issues

#### `raw.raw_customers`
**Purpose**: Stores unprocessed customer data from CRM and registration systems  
**Key Features**:
- RFC 5321 compliant email validation
- JSONB support for flexible address storage
- Customer segmentation and preference tracking
- Compliance with data privacy requirements

**Important Fields**:
- `customer_id`: Business key from source system
- `addresses`: JSONB array of customer addresses
- `preferences`: JSONB object for customer preferences
- `marketing_consent`: GDPR compliance tracking

#### `raw.raw_shipments`
**Purpose**: Stores unprocessed shipping and logistics data  
**Key Features**:
- Multi-carrier support with tracking numbers
- Package dimensions and weight tracking
- Return shipment handling
- Delivery confirmation and signature tracking

**Important Fields**:
- `shipment_id`: Business key from logistics provider
- `tracking_number`: Carrier tracking identifier
- `dimensions`: JSONB object for package dimensions
- `is_return`: Flag for return shipments

### Staging Layer Tables

#### `staging.staging_orders_incremental`
**Purpose**: Change Data Capture (CDC) enabled staging table for incremental order processing  
**Key Features**:
- **SCD Type 2**: Full history tracking with versioning
- **CDC Support**: INSERT/UPDATE/DELETE operation tracking
- **Data Quality**: Built-in data quality scoring
- **Incremental Processing**: Optimized for delta loads

**Important Fields**:
- `operation_type`: CDC operation (INSERT, UPDATE, DELETE)
- `record_version`: Version number for the same business key
- `is_current`: Flag indicating the current version
- `effective_from/effective_to`: Validity period
- `data_quality_score`: Automated quality assessment (0.00-1.00)

**Usage Pattern**:
```sql
-- Query current records only
SELECT * FROM staging.staging_orders_incremental 
WHERE is_current = TRUE;

-- Query historical changes for an order
SELECT * FROM staging.staging_orders_incremental 
WHERE order_id = 'ORD123' 
ORDER BY record_version;
```

#### Standard Staging Tables
- `staging.orders`: Traditional staging for orders
- `staging.order_items`: Order line items with product details
- `staging.customers`: Cleaned customer data
- `staging.products`: Product master data
- `staging.shipments`: Shipping information

### Marts Layer (Data Warehouse)

#### `marts.dim_customers` - Customer Dimension
**Purpose**: Slowly Changing Dimension Type 2 for customer master data  
**Key Features**:
- **SCD Type 2**: Track customer changes over time
- **Calculated Fields**: Age groups, customer tiers, regions
- **Business Metrics**: CLV, order counts, segmentation
- **Data Privacy**: Supports anonymization and GDPR compliance

**Derived Fields** (Auto-calculated via triggers):
- `age_group`: Calculated from date_of_birth
- `customer_tier`: Based on customer_lifetime_value
- `region`: Derived from country code
- `full_name`: Concatenated from first/last names

**Business Rules**:
- Customer tier thresholds: Bronze (<$1K), Silver ($1K-$5K), Gold ($5K-$10K), Platinum ($10K+)
- Age groups: Under 18, 18-24, 25-34, 35-44, 45-54, 55-64, 65+
- Region mapping: Automatic geographic region assignment

#### `marts.dim_products` - Product Dimension
**Purpose**: Slowly Changing Dimension Type 2 for product master data  
**Key Features**:
- **Product Hierarchy**: Category, subcategory, brand structure
- **Physical Attributes**: Dimensions, weight, material
- **Lifecycle Management**: Creation, launch, discontinuation dates
- **SEO Support**: Meta fields for e-commerce platforms
- **Inventory Integration**: Stock status and quantity limits

**Derived Fields** (Auto-calculated via triggers):
- `profit_margin_pct`: Calculated from price and cost
- Product categorization and taxonomy

#### `marts.fact_orders` - Orders Fact Table
**Purpose**: Central fact table for order transaction analysis  
**Key Features**:
- **Dimensional References**: Links to customer, product, date dimensions
- **Financial Measures**: Gross, net, tax, shipping, discount amounts
- **Performance Metrics**: Processing times, fulfillment metrics
- **Marketing Attribution**: Campaign tracking, referrer analysis
- **Customer Journey**: Order sequence, repeat customer flags

**Derived Fields** (Auto-calculated via triggers):
- `total_amount`: Calculated from component amounts
- `is_first_order`: Based on customer order sequence
- `is_repeat_customer`: Customer behavior classification

## Indexes and Performance

### Index Strategy

The schema implements a comprehensive indexing strategy:

1. **Primary Keys**: All tables have surrogate key primary keys
2. **Business Keys**: Unique indexes on natural business keys
3. **Foreign Keys**: Indexes on all foreign key relationships
4. **Query Patterns**: Composite indexes for common analytical queries
5. **Full-Text Search**: GIN indexes for product search capabilities
6. **JSONB**: Specialized indexes for semi-structured data queries

### Key Performance Indexes

```sql
-- Fact table performance
idx_fact_orders_customer_date    -- Customer analysis over time
idx_fact_orders_date_status      -- Order status reporting
idx_fact_orders_country_date     -- Geographic analysis

-- Dimension lookups
idx_dim_customers_natural_key_current  -- Current customer lookup
idx_dim_products_natural_key_current   -- Current product lookup

-- Incremental processing
idx_staging_orders_incr_updated_at     -- CDC processing
idx_staging_orders_incr_is_current     -- Current record queries
```

## Data Quality Framework

### Built-in Data Quality Features

1. **Constraint Validation**: 
   - Email format validation
   - Currency code validation (ISO 4217)
   - Country code validation (ISO 3166-1)
   - Positive amount checks
   - Date logic validation

2. **Data Quality Scoring**:
   - Automated calculation of data quality scores (0.00-1.00)
   - Factors: null fields, invalid values, duplicates
   - Configurable quality thresholds

3. **Validation Error Tracking**:
   - JSONB storage of validation errors
   - Granular error categorization
   - Data lineage and audit trail

### Quality Functions

```sql
-- Calculate data quality score
SELECT calculate_data_quality_score(10, 2, 1, 0); -- Returns 0.85

-- Validate email format
SELECT is_valid_email('user@example.com'); -- Returns true

-- Clean phone numbers
SELECT clean_phone_number('(555) 123-4567'); -- Returns '+15551234567'
```

## ETL Integration Features

### Change Data Capture (CDC)

The `staging_orders_incremental` table supports full CDC operations:

- **INSERT**: New records
- **UPDATE**: Modified records with versioning
- **DELETE**: Logical deletion tracking
- **History**: Complete audit trail of changes

### ETL Logging

Built-in ETL job tracking:

```sql
-- Start ETL job
SELECT log_etl_job_start('daily_orders_load', 'batch', 'orders_dag', 'extract_task');

-- Complete ETL job
SELECT log_etl_job_end(job_uuid, 'SUCCESS', 1000, 950, 50, 0, NULL);
```

### Utility Functions

- **Geographic Functions**: Region mapping, country validation
- **Customer Analytics**: Age grouping, tier calculation
- **Data Processing**: Hashing, cleaning, standardization

## Monitoring and Maintenance

### Built-in Monitoring

1. **ETL Job Logging**: `analytics.etl_job_log`
2. **Data Quality Results**: `analytics.data_quality_results`
3. **Performance Metrics**: Automated statistics collection
4. **Constraint Violations**: Comprehensive error reporting

### Maintenance Procedures

1. **Date Dimension**: Pre-populated with 3 years of dates
2. **Statistics**: Automatic update via triggers
3. **Partitioning**: Ready for date-based partitioning
4. **Archival**: Built-in retention policies

## Security and Compliance

### Role-Based Access Control

- **etl_user**: Full read/write access to raw and staging layers
- **analytics_user**: Read-only access to marts layer
- **Schema separation**: Logical isolation of data layers

### Data Privacy Features

- Email validation and opt-in tracking
- Marketing consent management
- GDPR compliance support
- Data anonymization ready

## Usage Examples

### Common Query Patterns

```sql
-- Customer lifetime value analysis
SELECT 
    customer_tier,
    COUNT(*) as customer_count,
    AVG(customer_lifetime_value) as avg_clv
FROM marts.dim_customers 
WHERE is_current = TRUE
GROUP BY customer_tier;

-- Monthly order trends
SELECT 
    d.year,
    d.month_name,
    COUNT(*) as order_count,
    SUM(total_amount) as revenue
FROM marts.fact_orders fo
JOIN marts.dim_date d ON fo.order_date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- Product performance by category
SELECT 
    p.category,
    COUNT(DISTINCT fo.order_key) as orders,
    SUM(fo.total_amount) as revenue,
    AVG(p.profit_margin_pct) as avg_margin
FROM marts.fact_orders fo
JOIN marts.dim_products p ON fo.product_key = p.product_key
WHERE p.is_current = TRUE
GROUP BY p.category;
```

### Incremental Processing

```sql
-- Process only changed orders since last run
SELECT * 
FROM staging.staging_orders_incremental 
WHERE updated_at > '2024-01-01 00:00:00'
AND is_current = TRUE;

-- Get full history for data lineage
SELECT 
    order_id,
    record_version,
    operation_type,
    effective_from,
    effective_to
FROM staging.staging_orders_incremental 
WHERE order_id = 'ORD123'
ORDER BY record_version;
```

## Best Practices

### Development Guidelines

1. **Always use business keys** for joins between layers
2. **Leverage built-in functions** for data quality and standardization
3. **Follow SCD patterns** for dimension updates
4. **Use incremental tables** for high-volume change tracking
5. **Monitor data quality scores** and set up alerts

### Performance Recommendations

1. **Use appropriate indexes** for your query patterns
2. **Consider partitioning** for large fact tables
3. **Implement data retention** policies for raw data
4. **Monitor query execution plans** regularly
5. **Use JSONB queries efficiently** with GIN indexes

### Data Quality

1. **Set up data quality monitoring** with Great Expectations
2. **Define quality thresholds** for each data source
3. **Implement data validation** in ETL pipelines
4. **Track data lineage** through all processing stages
5. **Monitor constraint violations** and failed validations

---

This schema provides a robust foundation for e-commerce analytics with built-in data quality, performance optimization, and operational monitoring capabilities.
