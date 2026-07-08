-- E-commerce Analytics Data Warehouse Schema Initialization
-- This script sets up the initial database schema for the e-commerce ETL pipeline

-- Create databases if they don't exist
SELECT 'CREATE DATABASE ecommerce' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ecommerce')\gexec
SELECT 'CREATE DATABASE ecommerce_test' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ecommerce_test')\gexec

-- Connect to the ecommerce database
\c ecommerce;

-- Create schemas for data organization
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Create roles and permissions
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'etl_user') THEN
    CREATE ROLE etl_user LOGIN PASSWORD 'etl_password';
  END IF;
  
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'analytics_user') THEN
    CREATE ROLE analytics_user LOGIN PASSWORD 'analytics_password';
  END IF;
END
$$;

-- Grant permissions
GRANT USAGE ON SCHEMA raw, staging, intermediate, marts, analytics TO etl_user;
GRANT CREATE ON SCHEMA raw, staging, intermediate, marts, analytics TO etl_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA raw, staging, intermediate, marts, analytics TO etl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw, staging, intermediate, marts, analytics GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO etl_user;

GRANT USAGE ON SCHEMA staging, intermediate, marts, analytics TO analytics_user;
GRANT SELECT ON ALL TABLES IN SCHEMA staging, intermediate, marts, analytics TO analytics_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA staging, intermediate, marts, analytics GRANT SELECT ON TABLES TO analytics_user;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create audit logging function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =============================================================================
-- RAW DATA TABLES (LANDING ZONE)
-- =============================================================================
-- These tables store raw, unprocessed data from various source systems

-- Raw Orders Table
-- Stores raw order data from e-commerce platforms, POS systems, etc.
CREATE TABLE IF NOT EXISTS raw.raw_orders (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    order_id VARCHAR(100) NOT NULL,
    customer_id VARCHAR(100),
    order_date TIMESTAMP WITH TIME ZONE,
    order_status VARCHAR(50),
    total_amount DECIMAL(12,2),
    currency VARCHAR(3),
    payment_method VARCHAR(50),
    shipping_address JSONB,
    billing_address JSONB,
    order_items JSONB, -- Array of order items
    discount_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    notes TEXT,
    
    -- Metadata fields
    source_system VARCHAR(50) NOT NULL,
    source_file VARCHAR(255),
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(100),
    record_hash VARCHAR(64), -- For deduplication
    
    -- Data quality fields
    is_valid BOOLEAN DEFAULT TRUE,
    validation_errors JSONB,
    
    CONSTRAINT chk_raw_orders_amount_positive CHECK (total_amount >= 0),
    CONSTRAINT chk_raw_orders_currency_format CHECK (currency ~ '^[A-Z]{3}$')
);

-- Raw Customers Table
-- Stores raw customer data from CRM, registration systems, etc.
CREATE TABLE IF NOT EXISTS raw.raw_customers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    email VARCHAR(320), -- RFC 5321 max email length
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(255),
    phone VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(20),
    registration_date TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    customer_status VARCHAR(30),
    preferred_language VARCHAR(10),
    marketing_consent BOOLEAN,
    
    -- Address information
    addresses JSONB, -- Array of addresses
    
    -- Demographics
    country VARCHAR(2), -- ISO 3166-1 alpha-2
    state_province VARCHAR(100),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    timezone VARCHAR(50),
    
    -- Customer segments and preferences
    customer_segment VARCHAR(50),
    preferences JSONB,
    tags JSONB, -- Array of customer tags
    
    -- Metadata fields
    source_system VARCHAR(50) NOT NULL,
    source_file VARCHAR(255),
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(100),
    record_hash VARCHAR(64),
    
    -- Data quality fields
    is_valid BOOLEAN DEFAULT TRUE,
    validation_errors JSONB,
    
    CONSTRAINT chk_raw_customers_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' OR email IS NULL),
    CONSTRAINT chk_raw_customers_country_format CHECK (country ~ '^[A-Z]{2}$' OR country IS NULL)
);

-- Raw Shipments Table
-- Stores raw shipping and delivery data from logistics providers
CREATE TABLE IF NOT EXISTS raw.raw_shipments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    shipment_id VARCHAR(100) NOT NULL,
    order_id VARCHAR(100) NOT NULL,
    tracking_number VARCHAR(100),
    carrier VARCHAR(100),
    shipping_method VARCHAR(100),
    
    -- Shipment status and timing
    shipment_status VARCHAR(50),
    shipped_date TIMESTAMP WITH TIME ZONE,
    estimated_delivery_date TIMESTAMP WITH TIME ZONE,
    actual_delivery_date TIMESTAMP WITH TIME ZONE,
    
    -- Address information
    origin_address JSONB,
    destination_address JSONB,
    
    -- Package details
    package_count INTEGER,
    total_weight DECIMAL(10,3),
    weight_unit VARCHAR(10) DEFAULT 'kg',
    dimensions JSONB, -- {length, width, height, unit}
    
    -- Costs
    shipping_cost DECIMAL(10,2),
    insurance_cost DECIMAL(10,2),
    currency VARCHAR(3),
    
    -- Delivery details
    delivery_instructions TEXT,
    signature_required BOOLEAN DEFAULT FALSE,
    delivered_to VARCHAR(255),
    delivery_notes TEXT,
    
    -- Return information
    is_return BOOLEAN DEFAULT FALSE,
    return_reason VARCHAR(255),
    return_date TIMESTAMP WITH TIME ZONE,
    
    -- Metadata fields
    source_system VARCHAR(50) NOT NULL,
    source_file VARCHAR(255),
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(100),
    record_hash VARCHAR(64),
    
    -- Data quality fields
    is_valid BOOLEAN DEFAULT TRUE,
    validation_errors JSONB,
    
    CONSTRAINT chk_raw_shipments_package_count_positive CHECK (package_count > 0),
    CONSTRAINT chk_raw_shipments_weight_positive CHECK (total_weight >= 0),
    CONSTRAINT chk_raw_shipments_cost_positive CHECK (shipping_cost >= 0 AND insurance_cost >= 0),
    CONSTRAINT chk_raw_shipments_currency_format CHECK (currency ~ '^[A-Z]{3}$' OR currency IS NULL),
    CONSTRAINT chk_raw_shipments_delivery_logic CHECK (
        (shipment_status = 'delivered' AND actual_delivery_date IS NOT NULL) OR 
        (shipment_status != 'delivered')
    )
);

-- =============================================================================
-- STAGING TABLES (CLEANED AND TYPED DATA)
-- =============================================================================
-- These tables contain cleaned, validated, and typed data ready for transformation

-- Staging Orders Incremental Table
-- Optimized for incremental loads with change data capture
CREATE TABLE IF NOT EXISTS staging.staging_orders_incremental (
    -- Business keys
    order_id VARCHAR(100) NOT NULL,
    source_system VARCHAR(50) NOT NULL,
    
    -- Order details
    customer_id VARCHAR(100),
    order_date TIMESTAMP WITH TIME ZONE,
    order_status VARCHAR(50),
    total_amount DECIMAL(12,2),
    currency VARCHAR(3),
    payment_method VARCHAR(50),
    payment_status VARCHAR(50),
    
    -- Financial breakdown
    subtotal_amount DECIMAL(12,2),
    discount_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    
    -- Customer information
    customer_email VARCHAR(320),
    customer_phone VARCHAR(20),
    
    -- Address information (denormalized for performance)
    shipping_country VARCHAR(2),
    shipping_state VARCHAR(100),
    shipping_city VARCHAR(100),
    shipping_postal_code VARCHAR(20),
    billing_country VARCHAR(2),
    billing_state VARCHAR(100),
    billing_city VARCHAR(100),
    billing_postal_code VARCHAR(20),
    
    -- Order metadata
    channel VARCHAR(50), -- online, mobile, store, phone
    campaign_id VARCHAR(100),
    referrer_url TEXT,
    device_type VARCHAR(50),
    
    -- Data lineage and quality
    data_quality_score DECIMAL(3,2), -- 0.00 to 1.00
    validation_status VARCHAR(20) DEFAULT 'valid',
    validation_errors JSONB,
    
    -- CDC and versioning fields
    operation_type VARCHAR(10) DEFAULT 'INSERT', -- INSERT, UPDATE, DELETE
    source_timestamp TIMESTAMP WITH TIME ZONE, -- Original timestamp from source
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Partitioning and processing metadata
    processing_date DATE DEFAULT CURRENT_DATE,
    batch_id VARCHAR(100),
    record_version INTEGER DEFAULT 1,
    is_current BOOLEAN DEFAULT TRUE,
    effective_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP WITH TIME ZONE,
    
    -- Primary key for incremental processing
    PRIMARY KEY (order_id, source_system, record_version),
    
    -- Business rules constraints
    CONSTRAINT chk_staging_orders_amount_positive CHECK (total_amount >= 0),
    CONSTRAINT chk_staging_orders_currency_valid CHECK (currency ~ '^[A-Z]{3}$'),
    CONSTRAINT chk_staging_orders_quality_score CHECK (data_quality_score >= 0 AND data_quality_score <= 1),
    CONSTRAINT chk_staging_orders_operation_type CHECK (operation_type IN ('INSERT', 'UPDATE', 'DELETE')),
    CONSTRAINT chk_staging_orders_effective_dates CHECK (effective_from <= COALESCE(effective_to, effective_from)),
    CONSTRAINT chk_staging_orders_country_format CHECK (
        (shipping_country ~ '^[A-Z]{2}$' OR shipping_country IS NULL) AND
        (billing_country ~ '^[A-Z]{2}$' OR billing_country IS NULL)
    )
);

-- Traditional staging tables for other entities
CREATE TABLE IF NOT EXISTS staging.orders (
    order_id VARCHAR(100) NOT NULL,
    customer_id VARCHAR(100),
    order_date TIMESTAMP WITH TIME ZONE,
    total_amount DECIMAL(12,2),
    currency VARCHAR(3),
    status VARCHAR(50),
    source_system VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id, source_system)
);

CREATE TABLE IF NOT EXISTS staging.order_items (
    order_item_id VARCHAR(100) NOT NULL,
    order_id VARCHAR(100) NOT NULL,
    product_id VARCHAR(100),
    product_name VARCHAR(500),
    product_category VARCHAR(100),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(12,2),
    discount_amount DECIMAL(10,2),
    source_system VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_item_id, source_system),
    
    CONSTRAINT chk_staging_order_items_quantity_positive CHECK (quantity > 0),
    CONSTRAINT chk_staging_order_items_prices_positive CHECK (unit_price >= 0 AND total_price >= 0)
);

CREATE TABLE IF NOT EXISTS staging.customers (
    customer_id VARCHAR(100) NOT NULL,
    email VARCHAR(320),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(255),
    phone VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(20),
    registration_date TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    customer_status VARCHAR(30),
    customer_segment VARCHAR(50),
    country VARCHAR(2),
    state_province VARCHAR(100),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    marketing_consent BOOLEAN,
    source_system VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Columns carried over from the raw layer so SELECT * replication from
    -- raw.raw_customers lands without column mapping
    id UUID,
    preferred_language VARCHAR(10),
    addresses JSONB,
    timezone VARCHAR(50),
    preferences JSONB,
    tags JSONB,
    source_file VARCHAR(255),
    ingestion_timestamp TIMESTAMP WITH TIME ZONE,
    batch_id VARCHAR(100),
    record_hash VARCHAR(64),
    is_valid BOOLEAN,
    validation_errors JSONB,
    PRIMARY KEY (customer_id, source_system),
    
    CONSTRAINT chk_staging_customers_email_valid CHECK (
        email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' OR email IS NULL
    ),
    CONSTRAINT chk_staging_customers_country_valid CHECK (country ~ '^[A-Z]{2}$' OR country IS NULL)
);

CREATE TABLE IF NOT EXISTS staging.products (
    product_id VARCHAR(100) NOT NULL,
    name VARCHAR(500),
    description TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    price DECIMAL(10,2),
    cost DECIMAL(10,2),
    weight DECIMAL(10,3),
    dimensions JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP WITH TIME ZONE,
    discontinued_date TIMESTAMP WITH TIME ZONE,
    source_system VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id, source_system),
    
    CONSTRAINT chk_staging_products_price_positive CHECK (price >= 0),
    CONSTRAINT chk_staging_products_cost_positive CHECK (cost >= 0),
    CONSTRAINT chk_staging_products_weight_positive CHECK (weight >= 0 OR weight IS NULL)
);

CREATE TABLE IF NOT EXISTS staging.shipments (
    shipment_id VARCHAR(100) NOT NULL,
    order_id VARCHAR(100) NOT NULL,
    tracking_number VARCHAR(100),
    carrier VARCHAR(100),
    shipping_method VARCHAR(100),
    shipment_status VARCHAR(50),
    shipped_date TIMESTAMP WITH TIME ZONE,
    estimated_delivery_date TIMESTAMP WITH TIME ZONE,
    actual_delivery_date TIMESTAMP WITH TIME ZONE,
    shipping_cost DECIMAL(10,2),
    currency VARCHAR(3),
    source_system VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (shipment_id, source_system),
    
    CONSTRAINT chk_staging_shipments_cost_positive CHECK (shipping_cost >= 0 OR shipping_cost IS NULL),
    CONSTRAINT chk_staging_shipments_currency_valid CHECK (currency ~ '^[A-Z]{3}$' OR currency IS NULL)
);

-- =============================================================================
-- DIMENSION TABLES (BUSINESS-READY REFERENCE DATA)
-- =============================================================================
-- These tables contain master data and reference information

-- Customer Dimension Table
-- Slowly Changing Dimension Type 2 for tracking customer changes over time
CREATE TABLE IF NOT EXISTS marts.dim_customers (
    customer_key BIGSERIAL PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    
    -- Customer demographics
    email VARCHAR(320),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(255),
    phone VARCHAR(20),
    date_of_birth DATE,
    age_group VARCHAR(20), -- Calculated field: '18-25', '26-35', etc.
    gender VARCHAR(20),
    
    -- Geographic information
    country VARCHAR(2),
    country_name VARCHAR(100),
    state_province VARCHAR(100),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    timezone VARCHAR(50),
    region VARCHAR(50), -- North America, Europe, Asia, etc.
    
    -- Customer status and segmentation
    customer_status VARCHAR(30), -- active, inactive, suspended
    customer_segment VARCHAR(50), -- VIP, regular, new, at_risk
    customer_tier VARCHAR(20), -- bronze, silver, gold, platinum
    registration_date DATE,
    first_order_date DATE,
    last_order_date DATE,
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Customer value metrics
    total_orders INTEGER DEFAULT 0,
    total_order_value DECIMAL(12,2) DEFAULT 0,
    average_order_value DECIMAL(10,2) DEFAULT 0,
    customer_lifetime_value DECIMAL(12,2) DEFAULT 0,
    days_since_last_order INTEGER,
    
    -- Marketing and preferences
    marketing_consent BOOLEAN DEFAULT FALSE,
    email_opt_in BOOLEAN DEFAULT FALSE,
    sms_opt_in BOOLEAN DEFAULT FALSE,
    preferred_communication_channel VARCHAR(20), -- email, sms, phone, none
    preferred_language VARCHAR(10) DEFAULT 'en',
    
    -- SCD Type 2 fields
    effective_date DATE DEFAULT CURRENT_DATE,
    end_date DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE,
    
    -- Data lineage
    source_system VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Business rules
    CONSTRAINT chk_dim_customers_email_valid CHECK (
        email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' OR email IS NULL
    ),
    CONSTRAINT chk_dim_customers_country_valid CHECK (country ~ '^[A-Z]{2}$' OR country IS NULL),
    CONSTRAINT chk_dim_customers_dates_logical CHECK (
        effective_date <= end_date AND
        (first_order_date >= registration_date OR first_order_date IS NULL) AND
        (last_order_date >= first_order_date OR last_order_date IS NULL)
    ),
    CONSTRAINT chk_dim_customers_metrics_positive CHECK (
        total_orders >= 0 AND 
        total_order_value >= 0 AND 
        average_order_value >= 0 AND
        customer_lifetime_value >= 0
    )
);

-- Product Dimension Table
-- Slowly Changing Dimension Type 2 for tracking product changes over time
CREATE TABLE IF NOT EXISTS marts.dim_products (
    product_key BIGSERIAL PRIMARY KEY,
    product_id VARCHAR(100) NOT NULL,
    
    -- Product identification
    sku VARCHAR(100),
    upc VARCHAR(20),
    isbn VARCHAR(20),
    
    -- Product details
    name VARCHAR(500),
    description TEXT,
    short_description VARCHAR(1000),
    
    -- Product hierarchy
    category VARCHAR(100),
    subcategory VARCHAR(100),
    product_line VARCHAR(100),
    brand VARCHAR(100),
    manufacturer VARCHAR(100),
    supplier VARCHAR(100),
    
    -- Physical attributes
    weight DECIMAL(10,3),
    weight_unit VARCHAR(10) DEFAULT 'kg',
    length DECIMAL(8,2),
    width DECIMAL(8,2),
    height DECIMAL(8,2),
    dimension_unit VARCHAR(10) DEFAULT 'cm',
    color VARCHAR(50),
    size VARCHAR(50),
    material VARCHAR(100),
    
    -- Pricing and cost
    current_price DECIMAL(10,2),
    original_price DECIMAL(10,2),
    cost DECIMAL(10,2),
    profit_margin_pct DECIMAL(5,2),
    tax_category VARCHAR(50),
    
    -- Product lifecycle
    created_date DATE,
    launch_date DATE,
    discontinued_date DATE,
    end_of_life_date DATE,
    
    -- Status and flags
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_digital BOOLEAN DEFAULT FALSE,
    requires_shipping BOOLEAN DEFAULT TRUE,
    age_restricted BOOLEAN DEFAULT FALSE,
    minimum_age INTEGER,
    
    -- Inventory and availability
    stock_status VARCHAR(20), -- in_stock, low_stock, out_of_stock
    min_quantity INTEGER DEFAULT 1,
    max_quantity INTEGER,
    backorder_allowed BOOLEAN DEFAULT FALSE,
    
    -- SEO and marketing
    meta_title VARCHAR(255),
    meta_description VARCHAR(500),
    keywords TEXT,
    tags JSONB,
    
    -- Ratings and reviews
    average_rating DECIMAL(3,2),
    review_count INTEGER DEFAULT 0,
    
    -- SCD Type 2 fields
    effective_date DATE DEFAULT CURRENT_DATE,
    end_date DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE,
    
    -- Data lineage
    source_system VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Business rules
    CONSTRAINT chk_dim_products_prices_positive CHECK (
        (current_price >= 0 OR current_price IS NULL) AND
        (original_price >= 0 OR original_price IS NULL) AND
        (cost >= 0 OR cost IS NULL)
    ),
    CONSTRAINT chk_dim_products_dimensions_positive CHECK (
        (weight >= 0 OR weight IS NULL) AND
        (length >= 0 OR length IS NULL) AND
        (width >= 0 OR width IS NULL) AND
        (height >= 0 OR height IS NULL)
    ),
    CONSTRAINT chk_dim_products_dates_logical CHECK (
        effective_date <= end_date AND
        (launch_date >= created_date OR launch_date IS NULL) AND
        (discontinued_date >= launch_date OR discontinued_date IS NULL)
    ),
    CONSTRAINT chk_dim_products_rating_valid CHECK (
        (average_rating >= 0 AND average_rating <= 5) OR average_rating IS NULL
    ),
    CONSTRAINT chk_dim_products_quantities_valid CHECK (
        (min_quantity >= 0 OR min_quantity IS NULL) AND
        (max_quantity >= min_quantity OR max_quantity IS NULL)
    )
);

-- =============================================================================
-- FACT TABLES (TRANSACTION DATA)
-- =============================================================================
-- These tables contain measurable business events and metrics

-- Orders Fact Table
-- Central fact table for order transactions
CREATE TABLE IF NOT EXISTS marts.fact_orders (
    order_key BIGSERIAL PRIMARY KEY,
    
    -- Business keys
    order_id VARCHAR(100) NOT NULL,
    source_system VARCHAR(50),
    
    -- Foreign keys to dimensions
    customer_key BIGINT REFERENCES marts.dim_customers(customer_key),
    order_date_key INTEGER REFERENCES marts.dim_date(date_key),
    shipping_date_key INTEGER,
    delivery_date_key INTEGER,
    
    -- Order details
    order_date TIMESTAMP WITH TIME ZONE,
    order_status VARCHAR(50),
    payment_method VARCHAR(50),
    payment_status VARCHAR(50),
    channel VARCHAR(50), -- online, mobile, store, phone
    device_type VARCHAR(50),
    
    -- Geographic dimensions (denormalized for performance)
    shipping_country VARCHAR(2),
    shipping_state VARCHAR(100),
    shipping_city VARCHAR(100),
    billing_country VARCHAR(2),
    billing_state VARCHAR(100),
    billing_city VARCHAR(100),
    
    -- Financial measures
    gross_amount DECIMAL(12,2),
    discount_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    total_amount DECIMAL(12,2),
    currency VARCHAR(3),
    
    -- Order composition
    item_count INTEGER,
    unique_products_count INTEGER,
    total_quantity INTEGER,
    
    -- Timing measures (in hours for analysis)
    processing_time_hours DECIMAL(8,2),
    fulfillment_time_hours DECIMAL(8,2),
    delivery_time_hours DECIMAL(8,2),
    
    -- Customer metrics (denormalized for performance)
    customer_order_number INTEGER, -- 1st, 2nd, 3rd order for this customer
    days_since_previous_order INTEGER,
    is_first_order BOOLEAN,
    is_repeat_customer BOOLEAN,
    
    -- Marketing attribution
    campaign_id VARCHAR(100),
    referrer_source VARCHAR(100),
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    
    -- Data quality and lineage
    data_quality_score DECIMAL(3,2),
    batch_id VARCHAR(100),
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Business rules
    CONSTRAINT chk_fact_orders_amounts_valid CHECK (
        gross_amount >= 0 AND
        discount_amount >= 0 AND
        tax_amount >= 0 AND
        shipping_cost >= 0 AND
        total_amount >= 0
    ),
    CONSTRAINT chk_fact_orders_counts_positive CHECK (
        item_count > 0 AND
        unique_products_count > 0 AND
        total_quantity > 0
    ),
    CONSTRAINT chk_fact_orders_currency_valid CHECK (currency ~ '^[A-Z]{3}$'),
    CONSTRAINT chk_fact_orders_data_quality CHECK (
        data_quality_score >= 0 AND data_quality_score <= 1
    )
);

CREATE TABLE IF NOT EXISTS marts.dim_date (
    date_key INTEGER PRIMARY KEY,
    date_actual DATE UNIQUE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    week INTEGER,
    day_of_year INTEGER,
    day_of_month INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20),
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

-- ETL metadata and monitoring tables
CREATE TABLE IF NOT EXISTS analytics.etl_job_log (
    job_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    job_type VARCHAR(50),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'RUNNING',
    records_processed INTEGER,
    records_inserted INTEGER,
    records_updated INTEGER,
    records_failed INTEGER,
    error_message TEXT,
    dag_id VARCHAR(100),
    task_id VARCHAR(100),
    execution_date TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS analytics.data_quality_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    expectation_suite_name VARCHAR(100),
    expectation_type VARCHAR(100),
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    success BOOLEAN,
    result_details JSONB,
    run_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(100)
);

-- =============================================================================
-- UTILITY FUNCTIONS AND PROCEDURES
-- =============================================================================

-- Function to calculate age group from date of birth
CREATE OR REPLACE FUNCTION calculate_age_group(date_of_birth DATE)
RETURNS VARCHAR(20) AS $$
BEGIN
    IF date_of_birth IS NULL THEN
        RETURN 'Unknown';
    END IF;
    
    CASE 
        WHEN AGE(date_of_birth) < INTERVAL '18 years' THEN RETURN 'Under 18'
        WHEN AGE(date_of_birth) < INTERVAL '25 years' THEN RETURN '18-24'
        WHEN AGE(date_of_birth) < INTERVAL '35 years' THEN RETURN '25-34'
        WHEN AGE(date_of_birth) < INTERVAL '45 years' THEN RETURN '35-44'
        WHEN AGE(date_of_birth) < INTERVAL '55 years' THEN RETURN '45-54'
        WHEN AGE(date_of_birth) < INTERVAL '65 years' THEN RETURN '55-64'
        ELSE RETURN '65+'
    END CASE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to determine customer tier based on lifetime value
CREATE OR REPLACE FUNCTION calculate_customer_tier(clv DECIMAL(12,2))
RETURNS VARCHAR(20) AS $$
BEGIN
    IF clv IS NULL OR clv = 0 THEN
        RETURN 'New';
    END IF;
    
    CASE 
        WHEN clv >= 10000 THEN RETURN 'Platinum'
        WHEN clv >= 5000 THEN RETURN 'Gold'
        WHEN clv >= 1000 THEN RETURN 'Silver'
        ELSE RETURN 'Bronze'
    END CASE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to determine geographic region from country code
CREATE OR REPLACE FUNCTION get_region_from_country(country_code VARCHAR(2))
RETURNS VARCHAR(50) AS $$
BEGIN
    CASE UPPER(country_code)
        WHEN 'US', 'CA', 'MX' THEN RETURN 'North America'
        WHEN 'GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'CH', 'SE', 'NO', 'DK', 'FI' THEN RETURN 'Europe'
        WHEN 'JP', 'KR', 'CN', 'IN', 'SG', 'TH', 'MY', 'ID', 'PH', 'VN' THEN RETURN 'Asia Pacific'
        WHEN 'AU', 'NZ' THEN RETURN 'Oceania'
        WHEN 'BR', 'AR', 'CL', 'CO', 'PE', 'VE' THEN RETURN 'South America'
        WHEN 'ZA', 'NG', 'EG', 'KE', 'MA' THEN RETURN 'Africa'
        ELSE RETURN 'Other'
    END CASE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to generate record hash for deduplication
CREATE OR REPLACE FUNCTION generate_record_hash(data_text TEXT)
RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(digest(data_text, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to validate email format
CREATE OR REPLACE FUNCTION is_valid_email(email_address VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN email_address ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to clean and standardize phone numbers
CREATE OR REPLACE FUNCTION clean_phone_number(phone_input VARCHAR)
RETURNS VARCHAR AS $$
BEGIN
    IF phone_input IS NULL THEN
        RETURN NULL;
    END IF;
    
    -- Remove all non-digit characters except +
    RETURN regexp_replace(phone_input, '[^\d+]', '', 'g');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to log ETL job execution
CREATE OR REPLACE FUNCTION log_etl_job_start(
    p_job_name VARCHAR,
    p_job_type VARCHAR DEFAULT NULL,
    p_dag_id VARCHAR DEFAULT NULL,
    p_task_id VARCHAR DEFAULT NULL,
    p_execution_date TIMESTAMP WITH TIME ZONE DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    job_uuid UUID;
BEGIN
    INSERT INTO analytics.etl_job_log (
        job_name, job_type, start_time, status, dag_id, task_id, execution_date
    ) VALUES (
        p_job_name, p_job_type, CURRENT_TIMESTAMP, 'RUNNING', p_dag_id, p_task_id, p_execution_date
    ) RETURNING job_id INTO job_uuid;
    
    RETURN job_uuid;
END;
$$ LANGUAGE plpgsql;

-- Function to log ETL job completion
CREATE OR REPLACE FUNCTION log_etl_job_end(
    p_job_id UUID,
    p_status VARCHAR,
    p_records_processed INTEGER DEFAULT NULL,
    p_records_inserted INTEGER DEFAULT NULL,
    p_records_updated INTEGER DEFAULT NULL,
    p_records_failed INTEGER DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE analytics.etl_job_log 
    SET 
        end_time = CURRENT_TIMESTAMP,
        status = p_status,
        records_processed = p_records_processed,
        records_inserted = p_records_inserted,
        records_updated = p_records_updated,
        records_failed = p_records_failed,
        error_message = p_error_message
    WHERE job_id = p_job_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate data quality score
CREATE OR REPLACE FUNCTION calculate_data_quality_score(
    p_total_fields INTEGER,
    p_null_fields INTEGER DEFAULT 0,
    p_invalid_fields INTEGER DEFAULT 0,
    p_duplicate_fields INTEGER DEFAULT 0
) RETURNS DECIMAL(3,2) AS $$
DECLARE
    quality_score DECIMAL(3,2);
BEGIN
    IF p_total_fields = 0 THEN
        RETURN 0.00;
    END IF;
    
    quality_score := 1.0 - (
        (p_null_fields * 0.3 + p_invalid_fields * 0.5 + p_duplicate_fields * 0.2) 
        / p_total_fields::DECIMAL
    );
    
    -- Ensure score is between 0 and 1
    RETURN GREATEST(0.00, LEAST(1.00, quality_score));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- =============================================================================
-- TRIGGERS FOR AUTOMATED MAINTENANCE
-- =============================================================================

-- Trigger function to auto-populate age group in customer dimension
CREATE OR REPLACE FUNCTION trigger_update_customer_derived_fields()
RETURNS TRIGGER AS $$
BEGIN
    -- Update age group based on date of birth
    NEW.age_group := calculate_age_group(NEW.date_of_birth);
    
    -- Update customer tier based on lifetime value
    NEW.customer_tier := calculate_customer_tier(NEW.customer_lifetime_value);
    
    -- Update region based on country
    NEW.region := get_region_from_country(NEW.country);
    
    -- Update full name if individual names are provided
    IF NEW.first_name IS NOT NULL OR NEW.last_name IS NOT NULL THEN
        NEW.full_name := TRIM(COALESCE(NEW.first_name, '') || ' ' || COALESCE(NEW.last_name, ''));
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger function to auto-populate profit margin in product dimension
CREATE OR REPLACE FUNCTION trigger_update_product_derived_fields()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate profit margin percentage
    IF NEW.current_price IS NOT NULL AND NEW.cost IS NOT NULL AND NEW.current_price > 0 THEN
        NEW.profit_margin_pct := ((NEW.current_price - NEW.cost) / NEW.current_price) * 100;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger function to auto-populate derived fields in fact_orders
CREATE OR REPLACE FUNCTION trigger_update_order_derived_fields()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate net amount if individual components are provided
    IF NEW.gross_amount IS NOT NULL THEN
        NEW.total_amount := NEW.gross_amount - COALESCE(NEW.discount_amount, 0) + 
                           COALESCE(NEW.tax_amount, 0) + COALESCE(NEW.shipping_cost, 0);
    END IF;
    
    -- Set is_first_order flag (this would typically be calculated during ETL)
    -- This is a simplified version - in practice, you'd check against existing orders
    IF NEW.customer_order_number = 1 THEN
        NEW.is_first_order := TRUE;
        NEW.is_repeat_customer := FALSE;
    ELSE
        NEW.is_first_order := FALSE;
        NEW.is_repeat_customer := TRUE;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger function for staging incremental table to manage versioning
CREATE OR REPLACE FUNCTION trigger_manage_incremental_versioning()
RETURNS TRIGGER AS $$
BEGIN
    -- Auto-increment version for updates to the same record
    IF TG_OP = 'INSERT' THEN
        -- Check if this is an update to an existing record
        SELECT COALESCE(MAX(record_version), 0) + 1 
        INTO NEW.record_version
        FROM staging.staging_orders_incremental 
        WHERE order_id = NEW.order_id AND source_system = NEW.source_system;
        
        -- Mark previous versions as not current
        IF NEW.record_version > 1 THEN
            UPDATE staging.staging_orders_incremental 
            SET is_current = FALSE, effective_to = NEW.effective_from
            WHERE order_id = NEW.order_id 
            AND source_system = NEW.source_system 
            AND record_version < NEW.record_version;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER trigger_dim_customers_derived_fields
    BEFORE INSERT OR UPDATE ON marts.dim_customers
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_customer_derived_fields();

CREATE TRIGGER trigger_dim_products_derived_fields
    BEFORE INSERT OR UPDATE ON marts.dim_products
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_product_derived_fields();

CREATE TRIGGER trigger_fact_orders_derived_fields
    BEFORE INSERT OR UPDATE ON marts.fact_orders
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_order_derived_fields();

CREATE TRIGGER trigger_staging_orders_incremental_versioning
    BEFORE INSERT ON staging.staging_orders_incremental
    FOR EACH ROW
    EXECUTE FUNCTION trigger_manage_incremental_versioning();

-- Add triggers for updated_at columns
CREATE TRIGGER update_staging_orders_updated_at 
    BEFORE UPDATE ON staging.orders 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_staging_order_items_updated_at 
    BEFORE UPDATE ON staging.order_items 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_staging_customers_updated_at 
    BEFORE UPDATE ON staging.customers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_staging_products_updated_at 
    BEFORE UPDATE ON staging.products 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_staging_shipments_updated_at 
    BEFORE UPDATE ON staging.shipments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_staging_orders_incremental_updated_at 
    BEFORE UPDATE ON staging.staging_orders_incremental 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_marts_fact_orders_updated_at 
    BEFORE UPDATE ON marts.fact_orders 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_marts_dim_customers_updated_at 
    BEFORE UPDATE ON marts.dim_customers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_marts_dim_products_updated_at 
    BEFORE UPDATE ON marts.dim_products 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- PERFORMANCE INDEXES
-- =============================================================================
-- Strategic indexes for query performance optimization

-- Raw Tables Indexes
-- Optimized for data ingestion and initial processing
CREATE INDEX IF NOT EXISTS idx_raw_orders_ingestion_ts ON raw.raw_orders(ingestion_timestamp);
CREATE INDEX IF NOT EXISTS idx_raw_orders_batch_id ON raw.raw_orders(batch_id);
CREATE INDEX IF NOT EXISTS idx_raw_orders_source_system ON raw.raw_orders(source_system);
CREATE INDEX IF NOT EXISTS idx_raw_orders_order_id_source ON raw.raw_orders(order_id, source_system);
CREATE INDEX IF NOT EXISTS idx_raw_orders_customer_id ON raw.raw_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_raw_orders_order_date ON raw.raw_orders(order_date) WHERE order_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_raw_orders_record_hash ON raw.raw_orders(record_hash);
CREATE INDEX IF NOT EXISTS idx_raw_orders_is_valid ON raw.raw_orders(is_valid);

CREATE INDEX IF NOT EXISTS idx_raw_customers_ingestion_ts ON raw.raw_customers(ingestion_timestamp);
CREATE INDEX IF NOT EXISTS idx_raw_customers_batch_id ON raw.raw_customers(batch_id);
CREATE INDEX IF NOT EXISTS idx_raw_customers_source_system ON raw.raw_customers(source_system);
CREATE INDEX IF NOT EXISTS idx_raw_customers_customer_id_source ON raw.raw_customers(customer_id, source_system);
CREATE INDEX IF NOT EXISTS idx_raw_customers_email ON raw.raw_customers(email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_raw_customers_record_hash ON raw.raw_customers(record_hash);
CREATE INDEX IF NOT EXISTS idx_raw_customers_is_valid ON raw.raw_customers(is_valid);

CREATE INDEX IF NOT EXISTS idx_raw_shipments_ingestion_ts ON raw.raw_shipments(ingestion_timestamp);
CREATE INDEX IF NOT EXISTS idx_raw_shipments_batch_id ON raw.raw_shipments(batch_id);
CREATE INDEX IF NOT EXISTS idx_raw_shipments_source_system ON raw.raw_shipments(source_system);
CREATE INDEX IF NOT EXISTS idx_raw_shipments_shipment_id_source ON raw.raw_shipments(shipment_id, source_system);
CREATE INDEX IF NOT EXISTS idx_raw_shipments_order_id ON raw.raw_shipments(order_id);
CREATE INDEX IF NOT EXISTS idx_raw_shipments_tracking_number ON raw.raw_shipments(tracking_number) WHERE tracking_number IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_raw_shipments_status ON raw.raw_shipments(shipment_status);
CREATE INDEX IF NOT EXISTS idx_raw_shipments_shipped_date ON raw.raw_shipments(shipped_date) WHERE shipped_date IS NOT NULL;

-- Staging Tables Indexes
-- Optimized for data transformation and incremental processing
CREATE INDEX IF NOT EXISTS idx_staging_orders_incr_updated_at ON staging.staging_orders_incremental(updated_at);
CREATE INDEX IF NOT EXISTS idx_staging_orders_incr_processing_date ON staging.staging_orders_incremental(processing_date);
CREATE INDEX IF NOT EXISTS idx_staging_orders_incr_source_timestamp ON staging.staging_orders_incremental(source_timestamp);
CREATE INDEX IF NOT EXISTS idx_staging_orders_incr_batch_id ON staging.staging_orders_incremental(batch_id);
CREATE INDEX IF NOT EXISTS idx_staging_orders_incr_is_current ON staging.staging_orders_incremental(is_current);
CREATE INDEX IF NOT EXISTS idx_staging_orders_incr_operation_type ON staging.staging_orders_incremental(operation_type);
CREATE INDEX IF NOT EXISTS idx_staging_orders_incr_customer_id ON staging.staging_orders_incremental(customer_id) WHERE customer_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_staging_orders_incr_order_date ON staging.staging_orders_incremental(order_date) WHERE order_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_staging_orders_incr_order_status ON staging.staging_orders_incremental(order_status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_staging_orders_incr_current_unique ON staging.staging_orders_incremental(order_id, source_system) WHERE is_current = TRUE;

CREATE INDEX IF NOT EXISTS idx_staging_orders_order_date ON staging.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_staging_orders_customer_id ON staging.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_staging_orders_updated_at ON staging.orders(updated_at);
CREATE INDEX IF NOT EXISTS idx_staging_orders_status ON staging.orders(status);

CREATE INDEX IF NOT EXISTS idx_staging_order_items_order_id ON staging.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_staging_order_items_product_id ON staging.order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_staging_order_items_updated_at ON staging.order_items(updated_at);

CREATE INDEX IF NOT EXISTS idx_staging_customers_email ON staging.customers(email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_staging_customers_updated_at ON staging.customers(updated_at);
CREATE INDEX IF NOT EXISTS idx_staging_customers_country ON staging.customers(country) WHERE country IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_staging_customers_registration_date ON staging.customers(registration_date);

CREATE INDEX IF NOT EXISTS idx_staging_products_name ON staging.products USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_staging_products_category ON staging.products(category);
CREATE INDEX IF NOT EXISTS idx_staging_products_brand ON staging.products(brand);
CREATE INDEX IF NOT EXISTS idx_staging_products_updated_at ON staging.products(updated_at);
CREATE INDEX IF NOT EXISTS idx_staging_products_is_active ON staging.products(is_active);

CREATE INDEX IF NOT EXISTS idx_staging_shipments_order_id ON staging.shipments(order_id);
CREATE INDEX IF NOT EXISTS idx_staging_shipments_tracking_number ON staging.shipments(tracking_number) WHERE tracking_number IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_staging_shipments_status ON staging.shipments(shipment_status);
CREATE INDEX IF NOT EXISTS idx_staging_shipments_shipped_date ON staging.shipments(shipped_date) WHERE shipped_date IS NOT NULL;

-- Dimension Tables Indexes
-- Optimized for lookup performance and SCD operations
CREATE UNIQUE INDEX IF NOT EXISTS idx_dim_customers_natural_key_current ON marts.dim_customers(customer_id) WHERE is_current = TRUE;
CREATE INDEX IF NOT EXISTS idx_dim_customers_email ON marts.dim_customers(email) WHERE email IS NOT NULL AND is_current = TRUE;
CREATE INDEX IF NOT EXISTS idx_dim_customers_country ON marts.dim_customers(country) WHERE country IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_dim_customers_segment ON marts.dim_customers(customer_segment);
CREATE INDEX IF NOT EXISTS idx_dim_customers_status ON marts.dim_customers(customer_status);
CREATE INDEX IF NOT EXISTS idx_dim_customers_tier ON marts.dim_customers(customer_tier);
CREATE INDEX IF NOT EXISTS idx_dim_customers_registration_date ON marts.dim_customers(registration_date);
CREATE INDEX IF NOT EXISTS idx_dim_customers_effective_date ON marts.dim_customers(effective_date);
CREATE INDEX IF NOT EXISTS idx_dim_customers_end_date ON marts.dim_customers(end_date);
CREATE INDEX IF NOT EXISTS idx_dim_customers_is_current ON marts.dim_customers(is_current);
CREATE INDEX IF NOT EXISTS idx_dim_customers_clv ON marts.dim_customers(customer_lifetime_value) WHERE customer_lifetime_value > 0;

CREATE UNIQUE INDEX IF NOT EXISTS idx_dim_products_natural_key_current ON marts.dim_products(product_id) WHERE is_current = TRUE;
CREATE INDEX IF NOT EXISTS idx_dim_products_name ON marts.dim_products USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_dim_products_category ON marts.dim_products(category);
CREATE INDEX IF NOT EXISTS idx_dim_products_subcategory ON marts.dim_products(category, subcategory);
CREATE INDEX IF NOT EXISTS idx_dim_products_brand ON marts.dim_products(brand);
CREATE INDEX IF NOT EXISTS idx_dim_products_price_range ON marts.dim_products(current_price) WHERE current_price IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_dim_products_is_active ON marts.dim_products(is_active);
CREATE INDEX IF NOT EXISTS idx_dim_products_effective_date ON marts.dim_products(effective_date);
CREATE INDEX IF NOT EXISTS idx_dim_products_end_date ON marts.dim_products(end_date);
CREATE INDEX IF NOT EXISTS idx_dim_products_is_current ON marts.dim_products(is_current);
CREATE INDEX IF NOT EXISTS idx_dim_products_stock_status ON marts.dim_products(stock_status);

-- Fact Tables Indexes
-- Optimized for analytical queries and aggregations
CREATE INDEX IF NOT EXISTS idx_fact_orders_order_date ON marts.fact_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_fact_orders_order_date_key ON marts.fact_orders(order_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_orders_customer_key ON marts.fact_orders(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_orders_order_status ON marts.fact_orders(order_status);
CREATE INDEX IF NOT EXISTS idx_fact_orders_channel ON marts.fact_orders(channel);
CREATE INDEX IF NOT EXISTS idx_fact_orders_payment_method ON marts.fact_orders(payment_method);
CREATE INDEX IF NOT EXISTS idx_fact_orders_shipping_country ON marts.fact_orders(shipping_country);
CREATE INDEX IF NOT EXISTS idx_fact_orders_total_amount ON marts.fact_orders(total_amount);
CREATE INDEX IF NOT EXISTS idx_fact_orders_currency ON marts.fact_orders(currency);
CREATE INDEX IF NOT EXISTS idx_fact_orders_is_first_order ON marts.fact_orders(is_first_order);
CREATE INDEX IF NOT EXISTS idx_fact_orders_campaign_id ON marts.fact_orders(campaign_id) WHERE campaign_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_fact_orders_data_quality ON marts.fact_orders(data_quality_score);
CREATE INDEX IF NOT EXISTS idx_fact_orders_batch_id ON marts.fact_orders(batch_id);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_fact_orders_customer_date ON marts.fact_orders(customer_key, order_date);
CREATE INDEX IF NOT EXISTS idx_fact_orders_date_status ON marts.fact_orders(order_date, order_status);
CREATE INDEX IF NOT EXISTS idx_fact_orders_country_date ON marts.fact_orders(shipping_country, order_date);
CREATE INDEX IF NOT EXISTS idx_fact_orders_channel_date ON marts.fact_orders(channel, order_date);

-- Date dimension indexes
CREATE INDEX IF NOT EXISTS idx_dim_date_year_month ON marts.dim_date(year, month);
CREATE INDEX IF NOT EXISTS idx_dim_date_quarter ON marts.dim_date(year, quarter);
CREATE INDEX IF NOT EXISTS idx_dim_date_week ON marts.dim_date(year, week);
CREATE INDEX IF NOT EXISTS idx_dim_date_is_weekend ON marts.dim_date(is_weekend);
CREATE INDEX IF NOT EXISTS idx_dim_date_is_holiday ON marts.dim_date(is_holiday);

-- ETL metadata indexes
CREATE INDEX IF NOT EXISTS idx_etl_job_log_job_name ON analytics.etl_job_log(job_name);
CREATE INDEX IF NOT EXISTS idx_etl_job_log_start_time ON analytics.etl_job_log(start_time);
CREATE INDEX IF NOT EXISTS idx_etl_job_log_status ON analytics.etl_job_log(status);
CREATE INDEX IF NOT EXISTS idx_etl_job_log_dag_id ON analytics.etl_job_log(dag_id) WHERE dag_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_data_quality_results_suite_name ON analytics.data_quality_results(expectation_suite_name);
CREATE INDEX IF NOT EXISTS idx_data_quality_results_table_name ON analytics.data_quality_results(table_name);
CREATE INDEX IF NOT EXISTS idx_data_quality_results_success ON analytics.data_quality_results(success);
CREATE INDEX IF NOT EXISTS idx_data_quality_results_run_time ON analytics.data_quality_results(run_time);

-- JSONB indexes for semi-structured data
CREATE INDEX IF NOT EXISTS idx_raw_orders_order_items_gin ON raw.raw_orders USING gin(order_items);
CREATE INDEX IF NOT EXISTS idx_raw_customers_addresses_gin ON raw.raw_customers USING gin(addresses);
CREATE INDEX IF NOT EXISTS idx_staging_orders_incr_validation_errors_gin ON staging.staging_orders_incremental USING gin(validation_errors);
CREATE INDEX IF NOT EXISTS idx_dim_products_tags_gin ON marts.dim_products USING gin(tags);

-- Populate date dimension (example for current year + next year)
INSERT INTO marts.dim_date (date_key, date_actual, year, quarter, month, month_name, week, day_of_year, day_of_month, day_of_week, day_name, is_weekend, is_holiday)
SELECT 
    TO_CHAR(date_actual, 'YYYYMMDD')::INTEGER as date_key,
    date_actual,
    EXTRACT(YEAR FROM date_actual)::INTEGER as year,
    EXTRACT(QUARTER FROM date_actual)::INTEGER as quarter,
    EXTRACT(MONTH FROM date_actual)::INTEGER as month,
    TO_CHAR(date_actual, 'Month') as month_name,
    EXTRACT(WEEK FROM date_actual)::INTEGER as week,
    EXTRACT(DOY FROM date_actual)::INTEGER as day_of_year,
    EXTRACT(DAY FROM date_actual)::INTEGER as day_of_month,
    EXTRACT(DOW FROM date_actual)::INTEGER as day_of_week,
    TO_CHAR(date_actual, 'Day') as day_name,
    CASE WHEN EXTRACT(DOW FROM date_actual) IN (0, 6) THEN TRUE ELSE FALSE END as is_weekend,
    FALSE as is_holiday -- Can be updated with actual holiday logic
FROM generate_series('2024-01-01'::DATE, '2026-12-31'::DATE, '1 day'::INTERVAL) date_actual
ON CONFLICT (date_key) DO NOTHING;

-- Grant permissions on newly created tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA raw, staging, intermediate, marts, analytics TO etl_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA raw, staging, intermediate, marts, analytics TO etl_user;
GRANT SELECT ON ALL TABLES IN SCHEMA staging, intermediate, marts, analytics TO analytics_user;

COMMIT;
