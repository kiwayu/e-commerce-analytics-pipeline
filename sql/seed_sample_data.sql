-- Synthetic sample data for local development and prototyping.
-- Populates the raw layer with reproducible, realistic-looking data so the
-- full pipeline (dbt staging -> intermediate -> marts) has something to chew on.
--
-- Usage (against the warehouse database):
--   psql -U ecommerce_user -d ecommerce -f seed_sample_data.sql
--
-- Re-runnable: truncates the raw tables before inserting.

\set ON_ERROR_STOP on

BEGIN;

SELECT setseed(0.42);

TRUNCATE raw.raw_shipments, raw.raw_orders, raw.raw_customers;

-- ---------------------------------------------------------------------------
-- Customers (500)
-- ---------------------------------------------------------------------------
INSERT INTO raw.raw_customers (
    customer_id, email, first_name, last_name, full_name, phone,
    date_of_birth, gender, registration_date, last_login, customer_status,
    preferred_language, marketing_consent, country, state_province, city,
    postal_code, timezone, customer_segment, source_system, source_file,
    batch_id, record_hash, is_valid
)
SELECT
    'CUST-' || lpad(i::text, 5, '0'),
    'customer' || i || '@example.com',
    first_names.n,
    last_names.n,
    first_names.n || ' ' || last_names.n,
    '+1555' || lpad((1000000 + floor(random() * 8999999))::text, 7, '0'),
    (date '1960-01-01' + (floor(random() * 15000))::int),
    (ARRAY['male', 'female', 'other', 'undisclosed'])[1 + floor(random() * 4)::int],
    now() - (random() * interval '730 days'),
    now() - (random() * interval '30 days'),
    (ARRAY['active', 'active', 'active', 'inactive', 'churned'])[1 + floor(random() * 5)::int],
    (ARRAY['en', 'en', 'en', 'de', 'fr', 'es'])[1 + floor(random() * 6)::int],
    random() < 0.6,
    (ARRAY['US', 'US', 'GB', 'DE', 'CA', 'AU', 'FR'])[1 + floor(random() * 7)::int],
    (ARRAY['California', 'Texas', 'New York', 'Ontario', 'Bavaria', 'Nowhere'])[1 + floor(random() * 6)::int],
    (ARRAY['San Francisco', 'Austin', 'New York', 'Toronto', 'Munich', 'London'])[1 + floor(random() * 6)::int],
    lpad((10000 + floor(random() * 89999))::text, 5, '0'),
    (ARRAY['America/Los_Angeles', 'America/New_York', 'Europe/London', 'Europe/Berlin'])[1 + floor(random() * 4)::int],
    (ARRAY['vip', 'champion', 'loyal_customer', 'potential_loyalist', 'new_customer', 'at_risk'])[1 + floor(random() * 6)::int],
    'seed_generator',
    'seed_sample_data.sql',
    'seed_batch_001',
    md5('customer' || i),
    TRUE
FROM generate_series(1, 500) AS s(i)
CROSS JOIN LATERAL (
    SELECT (ARRAY['Alex', 'Sam', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley',
                  'Jamie', 'Avery', 'Quinn', 'Emma', 'Liam', 'Olivia', 'Noah',
                  'Sophia', 'Mason', 'Isabella', 'Lucas', 'Mia', 'Ethan'])[1 + floor(random() * 20)::int] AS n
) AS first_names
CROSS JOIN LATERAL (
    SELECT (ARRAY['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
                  'Miller', 'Davis', 'Martinez', 'Lopez', 'Wilson', 'Anderson',
                  'Thomas', 'Moore', 'Jackson', 'Martin', 'Lee', 'Walker',
                  'Hall', 'Young'])[1 + floor(random() * 20)::int] AS n
) AS last_names;

-- ---------------------------------------------------------------------------
-- Orders (5000, spread over the last 90 days)
-- ---------------------------------------------------------------------------
INSERT INTO raw.raw_orders (
    order_id, customer_id, order_date, order_status, total_amount, currency,
    payment_method, shipping_address, billing_address, order_items,
    discount_amount, tax_amount, shipping_cost, source_system, source_file,
    batch_id, record_hash, is_valid
)
SELECT
    'ORD-' || lpad(i::text, 6, '0'),
    'CUST-' || lpad((1 + floor(random() * 500))::text, 5, '0'),
    now() - (random() * interval '90 days'),
    (ARRAY['pending', 'processing', 'shipped', 'delivered', 'delivered',
           'delivered', 'delivered', 'cancelled', 'refunded'])[1 + floor(random() * 9)::int],
    t.amt,
    (ARRAY['USD', 'USD', 'USD', 'EUR', 'GBP', 'CAD', 'AUD'])[1 + floor(random() * 7)::int],
    (ARRAY['credit_card', 'credit_card', 'paypal', 'apple_pay', 'bank_transfer'])[1 + floor(random() * 5)::int],
    jsonb_build_object('street', floor(random() * 9999)::int || ' Main St', 'city', 'Springfield', 'zip', lpad((10000 + floor(random() * 89999))::text, 5, '0')),
    jsonb_build_object('street', floor(random() * 9999)::int || ' Main St', 'city', 'Springfield', 'zip', lpad((10000 + floor(random() * 89999))::text, 5, '0')),
    jsonb_build_array(jsonb_build_object(
        'sku', 'SKU-' || lpad((1 + floor(random() * 200))::text, 4, '0'),
        'quantity', 1 + floor(random() * 4)::int,
        'unit_price', round((5 + random() * 495)::numeric, 2)
    )),
    round((t.amt * random() * 0.3)::numeric, 2),
    round((t.amt * 0.08)::numeric, 2),
    round((random() * 25)::numeric, 2),
    'seed_generator',
    'seed_sample_data.sql',
    'seed_batch_001',
    md5('order' || i),
    random() > 0.02
FROM (
    SELECT i, round((5 + random() * 1995)::numeric, 2) AS amt
    FROM generate_series(1, 5000) AS s(i)
) AS t;

-- ---------------------------------------------------------------------------
-- Shipments (for ~85% of shipped/delivered orders)
-- ---------------------------------------------------------------------------
INSERT INTO raw.raw_shipments (
    shipment_id, order_id, tracking_number, carrier, shipping_method,
    shipment_status, shipped_date, estimated_delivery_date, actual_delivery_date,
    package_count, total_weight, weight_unit, shipping_cost, insurance_cost,
    currency, signature_required, is_return, source_system, source_file,
    batch_id, record_hash, is_valid
)
SELECT
    'SHIP-' || lpad(row_number() OVER ()::text, 6, '0'),
    o.order_id,
    'TRK' || lpad((100000000 + floor(random() * 899999999))::text, 9, '0'),
    (ARRAY['UPS', 'FedEx', 'DHL', 'USPS'])[1 + floor(random() * 4)::int],
    (ARRAY['standard', 'standard', 'express', 'overnight'])[1 + floor(random() * 4)::int],
    CASE WHEN o.order_status = 'delivered' THEN 'delivered' ELSE 'in_transit' END,
    o.order_date + interval '1 day' + (random() * interval '1 day'),
    o.order_date + interval '4 days' + (random() * interval '2 days'),
    CASE WHEN o.order_status = 'delivered'
         THEN o.order_date + interval '3 days' + (random() * interval '4 days')
         ELSE NULL END,
    1 + floor(random() * 3)::int,
    round((0.1 + random() * 24.9)::numeric, 3),
    'kg',
    round((random() * 25)::numeric, 2),
    round((random() * 10)::numeric, 2),
    o.currency,
    random() < 0.2,
    FALSE,
    'seed_generator',
    'seed_sample_data.sql',
    'seed_batch_001',
    md5('shipment' || o.order_id),
    TRUE
FROM raw.raw_orders o
WHERE o.order_status IN ('shipped', 'delivered')
  AND random() < 0.85;

COMMIT;

-- Quick sanity report
SELECT 'raw_customers' AS table_name, count(*) AS rows FROM raw.raw_customers
UNION ALL
SELECT 'raw_orders', count(*) FROM raw.raw_orders
UNION ALL
SELECT 'raw_shipments', count(*) FROM raw.raw_shipments;
