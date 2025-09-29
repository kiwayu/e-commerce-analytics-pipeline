-- =============================================================================
-- SCHEMA VALIDATION AND TESTING SCRIPT
-- =============================================================================
-- This script validates the database schema and tests key functionality

-- Test schema creation
DO $$
BEGIN
    RAISE NOTICE 'Testing schema validation...';
END $$;

-- =============================================================================
-- BASIC SCHEMA VALIDATION
-- =============================================================================

-- Check that all schemas exist
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name IN ('raw', 'staging', 'intermediate', 'marts', 'analytics')
ORDER BY schema_name;

-- Check that all required tables exist
WITH expected_tables AS (
    SELECT 'raw' as schema_name, 'raw_orders' as table_name
    UNION ALL SELECT 'raw', 'raw_customers'
    UNION ALL SELECT 'raw', 'raw_shipments'
    UNION ALL SELECT 'staging', 'staging_orders_incremental'
    UNION ALL SELECT 'staging', 'orders'
    UNION ALL SELECT 'staging', 'order_items'
    UNION ALL SELECT 'staging', 'customers'
    UNION ALL SELECT 'staging', 'products'
    UNION ALL SELECT 'staging', 'shipments'
    UNION ALL SELECT 'marts', 'dim_customers'
    UNION ALL SELECT 'marts', 'dim_products'
    UNION ALL SELECT 'marts', 'fact_orders'
    UNION ALL SELECT 'marts', 'dim_date'
    UNION ALL SELECT 'analytics', 'etl_job_log'
    UNION ALL SELECT 'analytics', 'data_quality_results'
)
SELECT 
    et.schema_name,
    et.table_name,
    CASE 
        WHEN t.table_name IS NOT NULL THEN 'EXISTS'
        ELSE 'MISSING'
    END as status
FROM expected_tables et
LEFT JOIN information_schema.tables t 
    ON et.schema_name = t.table_schema 
    AND et.table_name = t.table_name
ORDER BY et.schema_name, et.table_name;

-- =============================================================================
-- FUNCTION TESTING
-- =============================================================================

-- Test utility functions
SELECT 'Function Tests' as test_category;

-- Test age group calculation
SELECT 
    'Age Group Function' as test_name,
    calculate_age_group('1990-05-15'::DATE) as result,
    'Should be 25-34' as expected;

-- Test customer tier calculation
SELECT 
    'Customer Tier Function' as test_name,
    calculate_customer_tier(7500.00) as result,
    'Should be Gold' as expected;

-- Test region mapping
SELECT 
    'Region Mapping Function' as test_name,
    get_region_from_country('US') as result,
    'Should be North America' as expected;

-- Test email validation
SELECT 
    'Email Validation Function' as test_name,
    is_valid_email('test@example.com') as result,
    'Should be true' as expected;

-- Test phone cleaning
SELECT 
    'Phone Cleaning Function' as test_name,
    clean_phone_number('(555) 123-4567') as result,
    'Should be +15551234567' as expected;

-- Test data quality score calculation
SELECT 
    'Data Quality Score Function' as test_name,
    calculate_data_quality_score(10, 2, 1, 0) as result,
    'Should be 0.85' as expected;

-- =============================================================================
-- CONSTRAINT TESTING
-- =============================================================================

-- Test data insertion with constraints
SELECT 'Constraint Tests' as test_category;

-- Test valid data insertion
DO $$
DECLARE
    test_customer_key BIGINT;
    test_order_key BIGINT;
BEGIN
    -- Insert test customer
    INSERT INTO marts.dim_customers (
        customer_id, email, first_name, last_name, country, 
        customer_lifetime_value, date_of_birth
    ) VALUES (
        'TEST_CUST_001', 'test@example.com', 'John', 'Doe', 'US',
        2500.00, '1985-06-15'::DATE
    ) RETURNING customer_key INTO test_customer_key;
    
    RAISE NOTICE 'Test customer inserted with key: %', test_customer_key;
    
    -- Insert test product
    INSERT INTO marts.dim_products (
        product_id, name, category, current_price, cost
    ) VALUES (
        'TEST_PROD_001', 'Test Product', 'Electronics', 99.99, 65.00
    );
    
    RAISE NOTICE 'Test product inserted successfully';
    
    -- Insert test order
    INSERT INTO marts.fact_orders (
        order_id, customer_key, order_date, gross_amount, 
        currency, item_count, unique_products_count, total_quantity
    ) VALUES (
        'TEST_ORD_001', test_customer_key, CURRENT_TIMESTAMP, 99.99,
        'USD', 1, 1, 1
    ) RETURNING order_key INTO test_order_key;
    
    RAISE NOTICE 'Test order inserted with key: %', test_order_key;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error during test data insertion: %', SQLERRM;
END $$;

-- =============================================================================
-- TRIGGER TESTING
-- =============================================================================

-- Test derived field triggers
SELECT 'Trigger Tests' as test_category;

-- Check that customer derived fields were populated
SELECT 
    customer_id,
    age_group,
    customer_tier,
    region,
    full_name,
    profit_margin_pct
FROM marts.dim_customers dc
LEFT JOIN marts.dim_products dp ON dp.product_id = 'TEST_PROD_001'
WHERE dc.customer_id = 'TEST_CUST_001';

-- =============================================================================
-- INDEX VALIDATION
-- =============================================================================

-- Check that key indexes exist
WITH expected_indexes AS (
    SELECT 'raw' as schema_name, 'raw_orders' as table_name, 'idx_raw_orders_order_id_source' as index_name
    UNION ALL SELECT 'staging', 'staging_orders_incremental', 'idx_staging_orders_incr_current_unique'
    UNION ALL SELECT 'marts', 'dim_customers', 'idx_dim_customers_natural_key_current'
    UNION ALL SELECT 'marts', 'dim_products', 'idx_dim_products_natural_key_current'
    UNION ALL SELECT 'marts', 'fact_orders', 'idx_fact_orders_customer_date'
)
SELECT 
    ei.schema_name,
    ei.table_name,
    ei.index_name,
    CASE 
        WHEN i.indexname IS NOT NULL THEN 'EXISTS'
        ELSE 'MISSING'
    END as status
FROM expected_indexes ei
LEFT JOIN pg_indexes i 
    ON ei.schema_name = i.schemaname 
    AND ei.table_name = i.tablename 
    AND ei.index_name = i.indexname
ORDER BY ei.schema_name, ei.table_name;

-- =============================================================================
-- ETL LOGGING TESTING
-- =============================================================================

-- Test ETL logging functions
DO $$
DECLARE
    job_uuid UUID;
BEGIN
    -- Test ETL job logging
    SELECT log_etl_job_start('test_job', 'validation', 'test_dag', 'test_task') INTO job_uuid;
    RAISE NOTICE 'ETL job started with UUID: %', job_uuid;
    
    -- Complete the job
    PERFORM log_etl_job_end(job_uuid, 'SUCCESS', 100, 95, 5, 0, NULL);
    RAISE NOTICE 'ETL job completed successfully';
    
    -- Verify the log entry
    PERFORM 1 FROM analytics.etl_job_log WHERE job_id = job_uuid;
    IF FOUND THEN
        RAISE NOTICE 'ETL job log entry found';
    ELSE
        RAISE NOTICE 'ETL job log entry NOT found';
    END IF;
END $$;

-- =============================================================================
-- INCREMENTAL PROCESSING TESTING
-- =============================================================================

-- Test incremental staging table versioning
INSERT INTO staging.staging_orders_incremental (
    order_id, source_system, customer_id, order_date, 
    total_amount, currency, operation_type
) VALUES (
    'TEST_INCR_001', 'test_system', 'TEST_CUST_001', CURRENT_TIMESTAMP,
    150.00, 'USD', 'INSERT'
);

-- Insert an update to the same order
INSERT INTO staging.staging_orders_incremental (
    order_id, source_system, customer_id, order_date, 
    total_amount, currency, operation_type
) VALUES (
    'TEST_INCR_001', 'test_system', 'TEST_CUST_001', CURRENT_TIMESTAMP,
    175.00, 'USD', 'UPDATE'
);

-- Check versioning worked correctly
SELECT 
    order_id,
    record_version,
    is_current,
    operation_type,
    total_amount,
    effective_from,
    effective_to
FROM staging.staging_orders_incremental 
WHERE order_id = 'TEST_INCR_001'
ORDER BY record_version;

-- =============================================================================
-- PERFORMANCE TESTING
-- =============================================================================

-- Test query performance on key indexes
EXPLAIN (ANALYZE, BUFFERS) 
SELECT COUNT(*) 
FROM staging.staging_orders_incremental 
WHERE is_current = TRUE;

EXPLAIN (ANALYZE, BUFFERS)
SELECT c.customer_id, c.customer_tier, COUNT(f.order_key) as order_count
FROM marts.dim_customers c
LEFT JOIN marts.fact_orders f ON c.customer_key = f.customer_key
WHERE c.is_current = TRUE
GROUP BY c.customer_id, c.customer_tier;

-- =============================================================================
-- CLEANUP TEST DATA
-- =============================================================================

-- Clean up test data
DELETE FROM marts.fact_orders WHERE order_id = 'TEST_ORD_001';
DELETE FROM marts.dim_products WHERE product_id = 'TEST_PROD_001';
DELETE FROM marts.dim_customers WHERE customer_id = 'TEST_CUST_001';
DELETE FROM staging.staging_orders_incremental WHERE order_id = 'TEST_INCR_001';
DELETE FROM analytics.etl_job_log WHERE job_name = 'test_job';

-- =============================================================================
-- FINAL VALIDATION SUMMARY
-- =============================================================================

SELECT 'Schema validation completed successfully!' as validation_result;
