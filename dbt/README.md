# 📊 E-commerce Analytics dbt Project

A production-grade dbt project for e-commerce analytics following dbt Labs style guide and best practices. This project transforms raw e-commerce data into business-ready analytics models for reporting, segmentation, and insights.

## 🏗️ Project Structure

### Data Architecture

```
Raw Data → Staging → Intermediate → Marts
    ↓         ↓          ↓           ↓
 Source    Clean &   Business    Analytics
Systems   Validate   Logic      Ready Data
```

### Model Organization

```
models/
├── staging/           # Cleaned, standardized data from sources
│   ├── stg_raw_orders.sql
│   ├── stg_raw_customers.sql  
│   ├── stg_raw_shipments.sql
│   ├── sources.yml
│   └── staging.yml
├── intermediate/      # Business logic transformations
│   ├── int_customer_order_metrics.sql
│   └── int_order_shipment_combined.sql
├── marts/            # Analytics-ready dimensional models
│   ├── core/         # Core business entities
│   │   ├── dim_customers.sql
│   │   ├── fact_orders.sql
│   │   └── core.yml
│   ├── finance/      # Finance-specific models
│   │   └── revenue_daily.sql
│   └── marketing/    # Marketing-specific models
│       └── customer_segmentation.sql
└── schema.yml        # Project-wide documentation
```

## 🎯 Model Descriptions

### Staging Layer (`staging/`)

**Purpose**: Clean, standardize, and validate raw data
**Materialization**: Views (for development speed)
**Refresh**: Real-time (as source data changes)

- **`stg_raw_orders`**: Standardized order data with derived business fields
- **`stg_raw_customers`**: Cleaned customer data with validation flags  
- **`stg_raw_shipments`**: Enriched shipment data with delivery metrics

### Intermediate Layer (`intermediate/`)

**Purpose**: Implement complex business logic and prepare data for marts
**Materialization**: Views
**Refresh**: Daily

- **`int_customer_order_metrics`**: Customer-level behavioral metrics and segmentation
- **`int_order_shipment_combined`**: Complete order fulfillment view with shipment data

### Marts Layer (`marts/`)

**Purpose**: Analytics-ready dimensional models for reporting
**Materialization**: Tables (for query performance)
**Refresh**: Nightly

#### Core (`marts/core/`)
- **`dim_customers`**: Customer dimension with segmentation and metrics
- **`fact_orders`**: Orders fact table with customer and shipment context

#### Finance (`marts/finance/`)
- **`revenue_daily`**: Daily revenue aggregations and financial metrics

#### Marketing (`marts/marketing/`)
- **`customer_segmentation`**: Detailed customer segments with marketing recommendations

## 📏 Style Guide Compliance

This project follows [dbt Labs SQL style guide](https://docs.getdbt.com/guides/best-practices/how-we-style/0-how-we-style-our-dbt-projects):

### SQL Formatting
- ✅ **Lowercase**: All keywords, field names, and functions in lowercase
- ✅ **Trailing commas**: Used consistently throughout
- ✅ **4-space indentation**: Standard indentation for readability
- ✅ **80-character lines**: SQL lines kept under 80 characters
- ✅ **Explicit AS**: Always use `as` keyword for aliases
- ✅ **Explicit JOINs**: Always specify `inner join`, `left join`, etc.

### Model Structure
- ✅ **Import CTEs**: All `{{ ref() }}` statements at top of file
- ✅ **Functional CTEs**: Single logical unit of work per CTE
- ✅ **Descriptive naming**: Clear, verbose CTE names
- ✅ **Final select**: Last line selects from final CTE

### Configuration
- ✅ **Model config**: Specified in model files for readability
- ✅ **Directory config**: Applied in `dbt_project.yml`
- ✅ **Explicit materialization**: Clear materialization strategy per layer

## 🔧 Configuration

### Materializations by Layer

```yaml
staging:
  +materialized: view      # Fast development, real-time data
  
intermediate:  
  +materialized: view      # Business logic, daily refresh

marts:
  +materialized: table     # Performance optimized, nightly refresh
```

### Performance Optimizations

- **Indexes**: Defined on key lookup columns
- **Partitioning**: Date-based partitioning on fact tables
- **Incremental models**: For large, growing datasets
- **Selective refreshing**: Layer-based refresh strategies

## 🧪 Data Quality & Testing

### Test Coverage

```yaml
# Source data tests
- unique
- not_null  
- relationships
- accepted_values
- data_type_validation

# Business logic tests
- custom_business_rules
- referential_integrity
- data_freshness
- volume_validation
```

### Data Quality Checks

- **Staging layer**: Data validation and quality flags
- **Intermediate layer**: Business rule validation
- **Marts layer**: Comprehensive data tests and metrics

## 🚀 Getting Started

### Prerequisites

```bash
# Install dbt
pip install dbt-postgres>=1.6.0

# Install dependencies
dbt deps
```

### Setup

1. **Configure Profile** (`~/.dbt/profiles.yml`):
```yaml
ecommerce:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: dbt_user
      password: your_password
      port: 5432
      dbname: ecommerce
      schema: dbt_dev
    prod:
      type: postgres
      host: prod-host
      user: dbt_prod_user
      password: prod_password
      port: 5432
      dbname: ecommerce
      schema: analytics
```

2. **Test Connection**:
```bash
dbt debug
```

3. **Run Initial Build**:
```bash
# Build staging layer first
dbt run --select staging

# Build intermediate layer
dbt run --select intermediate  

# Build marts layer
dbt run --select marts

# Run all tests
dbt test
```

## 🔄 Development Workflow

### Daily Development

```bash
# Run models you're working on
dbt run --select +my_model+

# Test your changes
dbt test --select +my_model+

# Generate documentation
dbt docs generate && dbt docs serve
```

### Production Deployment

```bash
# Full refresh for schema changes
dbt run --full-refresh --target prod

# Regular incremental run
dbt run --target prod

# Run all tests in production
dbt test --target prod

# Update production docs
dbt docs generate --target prod
```

## 📊 Business Logic

### Customer Segmentation

The project implements a comprehensive customer segmentation strategy:

```sql
-- RFM-based segmentation
- VIP: High value, frequent, recent customers
- Champion: Loyal customers with good value
- Loyal Customer: Regular purchasers
- Potential Loyalist: Recent customers with potential
- New Customer: First-time buyers
- At Risk: Valuable customers who haven't purchased recently
- Need Attention: Customers requiring reactivation
- Cannot Lose Them: Previously valuable customers at risk
```

### Revenue Metrics

```sql
-- Key financial metrics
- Gross Revenue: Total order value
- Net Revenue: Fulfilled order value only
- Average Order Value: Mean order value
- Customer Lifetime Value: Predicted total customer value
- Revenue Realization Rate: Net/Gross revenue ratio
```

### Operational Metrics

```sql
-- Fulfillment and delivery metrics
- Order Fulfillment Rate: % orders successfully fulfilled
- Delivery Performance: On-time delivery tracking
- Return Rate: % orders with returns
- Clean Order Rate: % orders without issues
```

## 🧩 Custom Macros

Located in `macros/business_logic.sql`:

- **`calculate_customer_lifetime_value()`**: LTV prediction by segment
- **`calculate_order_value_tier()`**: Order value categorization
- **`calculate_rfm_score()`**: RFM segmentation scoring
- **`safe_divide()`**: Division with zero-handling
- **`standardize_currency()`**: Currency code standardization

## 📈 Metrics & Exposures

### Defined Metrics

- **Daily Revenue**: Sum of daily fulfilled order revenue
- **Average Order Value**: Mean order value for fulfilled orders
- **Customer Lifetime Value**: Predicted CLV by segment
- **Order Fulfillment Rate**: Percentage of successfully fulfilled orders

### Dashboard Exposures

- **Finance Dashboard**: Executive financial metrics and trends
- **Marketing Analytics**: Customer segmentation and campaign insights  
- **Operations Monitoring**: Fulfillment and delivery performance

## 🔍 Monitoring & Alerting

### Data Freshness

```yaml
# Automated freshness checks
sources:
  freshness:
    warn_after: {count: 6, period: hour}
    error_after: {count: 12, period: hour}
```

### Volume Validation

```yaml
# Row count validation
models:
  tests:
    - dbt_expectations.expect_table_row_count_to_be_between:
        min_value: 1000
        max_value: 10000000
```

## 🛠️ Troubleshooting

### Common Issues

**1. Model Build Failures**
```bash
# Check for syntax errors
dbt parse

# Run with debug logging
dbt --debug run --select failing_model
```

**2. Test Failures**
```bash
# Run specific test with details
dbt test --select test_name --store-failures

# View failed test results
select * from <target_schema>.dbt_test_failures
```

**3. Performance Issues**
```bash
# Check query performance
dbt run --select slow_model --profiles-dir ./profiles

# Use explain plans
dbt show --select model_name --limit 0
```

### Performance Tuning

- **Incremental Models**: For large, growing fact tables
- **Partitioning**: Date-based partitioning on large tables
- **Indexing**: Strategic indexes on lookup columns
- **Selective Builds**: Target specific model subsets

## 📚 Documentation

### Auto-Generated Docs

```bash
# Generate and serve documentation
dbt docs generate
dbt docs serve --port 8080
```

### Model Documentation

Each model includes:
- Comprehensive description of purpose and business logic
- Column-level documentation with business definitions
- Data quality tests and validation rules
- Dependencies and lineage information

## 🔐 Security & Governance

### Access Control

```sql
-- Role-based permissions
GRANT SELECT ON schema.dim_customers TO analytics_team;
GRANT SELECT ON schema.revenue_daily TO finance_team;
GRANT SELECT ON schema.customer_segmentation TO marketing_team;
```

### Data Classification

- **Public**: Aggregated metrics and trends
- **Internal**: Customer segments and business metrics  
- **Restricted**: PII and sensitive customer data
- **Confidential**: Financial and strategic metrics

---

This dbt project provides a robust foundation for e-commerce analytics with production-grade data modeling, comprehensive testing, and clear documentation following industry best practices.
