{{
    config(
        materialized='view',
        tags=['staging', 'shipments']
    )
}}

{# 
This model standardizes shipment data and calculates delivery metrics.
Handles various shipment statuses and delivery timeframes.
#}

with

shipments_source as (

    select
        id,
        shipment_id,
        order_id,
        tracking_number,
        carrier,
        shipping_method,
        shipment_status,
        shipped_date,
        estimated_delivery_date,
        actual_delivery_date,
        origin_address,
        destination_address,
        package_count,
        total_weight,
        weight_unit,
        dimensions,
        shipping_cost,
        insurance_cost,
        currency,
        delivery_instructions,
        signature_required,
        delivered_to,
        delivery_notes,
        is_return,
        return_reason,
        return_date,
        source_system,
        source_file,
        ingestion_timestamp,
        batch_id,
        record_hash,
        is_valid,
        validation_errors

    from {{ source('raw', 'raw_shipments') }}

    where is_valid = true

),

cleaned_shipments as (

    select
        id,
        shipment_id,
        order_id,
        tracking_number,
        initcap(trim(carrier)) as carrier,
        lower(trim(shipping_method)) as shipping_method,
        lower(trim(shipment_status)) as shipment_status,
        cast(shipped_date as timestamp) as shipped_date,
        cast(estimated_delivery_date as date) as estimated_delivery_date,
        cast(actual_delivery_date as date) as actual_delivery_date,
        origin_address,
        destination_address,
        coalesce(package_count, 1) as package_count,
        total_weight,
        coalesce(weight_unit, 'kg') as weight_unit,
        dimensions,
        coalesce(shipping_cost, 0.00) as shipping_cost,
        coalesce(insurance_cost, 0.00) as insurance_cost,
        upper(trim(currency)) as currency,
        delivery_instructions,
        coalesce(signature_required, false) as signature_required,
        delivered_to,
        delivery_notes,
        coalesce(is_return, false) as is_return,
        return_reason,
        cast(return_date as date) as return_date,
        source_system,
        source_file,
        ingestion_timestamp,
        batch_id,
        record_hash,

        {# Derived delivery metrics #}
        case
            when actual_delivery_date is not null
                and estimated_delivery_date is not null
                then cast(actual_delivery_date as date) - cast(estimated_delivery_date as date)
            else null
        end as delivery_variance_days,

        case
            when shipped_date is not null
                and actual_delivery_date is not null
                then cast(actual_delivery_date as date) - cast(shipped_date as date)
            else null
        end as total_delivery_days,

        case
            when shipment_status = 'delivered' 
                and actual_delivery_date <= estimated_delivery_date
                then true
            when shipment_status = 'delivered' 
                and actual_delivery_date > estimated_delivery_date
                then false
            else null
        end as delivered_on_time,

        case
            when shipment_status in ('pending', 'processing') then 'preparing'
            when shipment_status in ('shipped', 'in_transit') then 'in_transit'
            when shipment_status = 'delivered' then 'delivered'
            when shipment_status in ('returned', 'lost', 'damaged') then 'exception'
            else 'unknown'
        end as shipment_status_group

    from shipments_source

),

enriched_shipments as (

    select
        *,
        
        {# Performance metrics #}
        case
            when delivered_on_time = true then 'on_time'
            when delivered_on_time = false and delivery_variance_days <= 2 
                then 'slightly_late'
            when delivered_on_time = false and delivery_variance_days > 2 
                then 'significantly_late'
            else 'unknown'
        end as delivery_performance,

        case
            when total_delivery_days <= 1 then 'same_day'
            when total_delivery_days <= 3 then 'fast'
            when total_delivery_days <= 7 then 'standard'
            else 'slow'
        end as delivery_speed_category

    from cleaned_shipments

)

select * from enriched_shipments
