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

    from {{ source('raw', 'raw_orders') }}

    where is_valid = true

),

converted_orders as (

    {# Express every amount in the base currency (vars.base_currency) #}
    select
        orders_source.*,
        orders_source.total_amount as total_amount_original,
        fx.rate_to_base as fx_rate,
        round(orders_source.total_amount * fx.rate_to_base, 2) as total_amount_base,
        round(coalesce(orders_source.discount_amount, 0.00) * fx.rate_to_base, 2) as discount_amount_base,
        round(coalesce(orders_source.tax_amount, 0.00) * fx.rate_to_base, 2) as tax_amount_base,
        round(coalesce(orders_source.shipping_cost, 0.00) * fx.rate_to_base, 2) as shipping_cost_base

    from orders_source

    left join {{ ref('fx_rates') }} as fx
        on fx.currency = upper(trim(orders_source.currency))

),

cleaned_orders as (

    select
        id,
        order_id,
        customer_id,
        cast(order_date as timestamp) as order_date,
        lower(trim(order_status)) as order_status,
        total_amount_base as total_amount,
        total_amount_original,
        fx_rate,
        upper(trim(currency)) as currency,
        lower(trim(payment_method)) as payment_method,
        shipping_address,
        billing_address,
        order_items,
        discount_amount_base as discount_amount,
        tax_amount_base as tax_amount,
        shipping_cost_base as shipping_cost,
        notes,
        source_system,
        source_file,
        ingestion_timestamp,
        batch_id,
        record_hash,

        {# Derived fields #}
        case
            when total_amount_base >= 1000 then 'high_value'
            when total_amount_base >= 100 then 'medium_value'
            else 'low_value'
        end as order_value_tier,

        case
            when order_status in ('pending', 'processing') then 'active'
            when order_status in ('shipped', 'delivered') then 'fulfilled'
            when order_status in ('cancelled', 'refunded') then 'cancelled'
            else 'unknown'
        end as order_status_group,

        total_amount_base - discount_amount_base as net_amount,
        total_amount_base + tax_amount_base + shipping_cost_base as gross_amount

    from converted_orders

)

select * from cleaned_orders
