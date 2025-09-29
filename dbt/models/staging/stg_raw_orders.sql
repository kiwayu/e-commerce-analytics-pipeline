{{
    config(
        materialized='view',
        tags=['staging', 'orders']
    )
}}

{# 
This model standardizes and cleans raw order data from the source system.
It applies consistent data types, handles null values, and adds derived fields.
#}

with

orders_source as (

    select
        id,
        order_id,
        customer_id,
        order_date,
        order_status,
        total_amount,
        currency,
        payment_method,
        shipping_address,
        billing_address,
        order_items,
        discount_amount,
        tax_amount,
        shipping_cost,
        notes,
        source_system,
        source_file,
        ingestion_timestamp,
        batch_id,
        record_hash,
        is_valid,
        validation_errors

    from {{ ref('raw_orders') }}

    where is_valid = true

),

cleaned_orders as (

    select
        id,
        order_id,
        customer_id,
        cast(order_date as timestamp) as order_date,
        lower(trim(order_status)) as order_status,
        total_amount,
        upper(trim(currency)) as currency,
        lower(trim(payment_method)) as payment_method,
        shipping_address,
        billing_address,
        order_items,
        coalesce(discount_amount, 0.00) as discount_amount,
        coalesce(tax_amount, 0.00) as tax_amount,
        coalesce(shipping_cost, 0.00) as shipping_cost,
        notes,
        source_system,
        source_file,
        ingestion_timestamp,
        batch_id,
        record_hash,

        {# Derived fields #}
        case
            when total_amount >= 1000 then 'high_value'
            when total_amount >= 100 then 'medium_value'
            else 'low_value'
        end as order_value_tier,

        case
            when order_status in ('pending', 'processing') then 'active'
            when order_status in ('shipped', 'delivered') then 'fulfilled'
            when order_status in ('cancelled', 'refunded') then 'cancelled'
            else 'unknown'
        end as order_status_group,

        total_amount - discount_amount as net_amount,
        total_amount + tax_amount + shipping_cost as gross_amount

    from orders_source

)

select * from cleaned_orders
