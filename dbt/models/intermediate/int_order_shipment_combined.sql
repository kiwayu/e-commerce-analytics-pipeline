{{
    config(
        materialized='view',
        tags=['intermediate', 'orders', 'shipments']
    )
}}

{# 
This model combines order and shipment data to create a complete view 
of the order fulfillment process from purchase to delivery.
#}

with

orders as (

    select
        order_id,
        customer_id,
        order_date,
        order_status,
        order_status_group,
        order_value_tier,
        total_amount,
        net_amount,
        gross_amount,
        currency as order_currency,
        payment_method

    from {{ ref('stg_raw_orders') }}

),

shipments as (

    select
        order_id,
        shipment_id,
        tracking_number,
        carrier,
        shipping_method,
        shipment_status,
        shipment_status_group,
        shipped_date,
        estimated_delivery_date,
        actual_delivery_date,
        package_count,
        total_weight,
        weight_unit,
        shipping_cost,
        insurance_cost,
        currency as shipment_currency,
        signature_required,
        delivered_to,
        is_return,
        return_reason,
        return_date,
        delivery_variance_days,
        total_delivery_days,
        delivered_on_time,
        delivery_performance,
        delivery_speed_category

    from {{ ref('stg_raw_shipments') }}

),

{# Aggregate shipments by order (in case of multiple shipments per order) #}
order_shipment_summary as (

    select
        order_id,
        count(*) as total_shipments,
        count(
            case 
                when shipment_status_group = 'delivered' 
                then 1 
            end
        ) as delivered_shipments,
        count(
            case 
                when shipment_status_group = 'exception' 
                then 1 
            end
        ) as exception_shipments,
        count(
            case 
                when is_return = true 
                then 1 
            end
        ) as return_shipments,
        
        {# Aggregate shipping costs #}
        sum(shipping_cost) as total_shipping_cost,
        sum(insurance_cost) as total_insurance_cost,
        
        {# Date aggregations #}
        min(shipped_date) as first_shipment_date,
        max(shipped_date) as last_shipment_date,
        min(estimated_delivery_date) as earliest_estimated_delivery,
        max(estimated_delivery_date) as latest_estimated_delivery,
        min(actual_delivery_date) as first_delivery_date,
        max(actual_delivery_date) as last_delivery_date,
        
        {# Performance aggregations #}
        avg(delivery_variance_days) as avg_delivery_variance_days,
        avg(total_delivery_days) as avg_total_delivery_days,
        count(
            case 
                when delivered_on_time = true 
                then 1 
            end
        )::decimal / nullif(
            count(
                case 
                    when delivered_on_time is not null 
                    then 1 
                end
            ), 0
        ) as on_time_delivery_rate,
        
        {# Most common values #}
        mode() within group (
            order by carrier
        ) as primary_carrier,
        mode() within group (
            order by shipping_method
        ) as primary_shipping_method,
        mode() within group (
            order by delivery_speed_category
        ) as primary_delivery_speed

    from shipments

    group by 1

),

orders_with_shipments as (

    select
        orders.order_id,
        orders.customer_id,
        orders.order_date,
        orders.order_status,
        orders.order_status_group,
        orders.order_value_tier,
        orders.total_amount,
        orders.net_amount,
        orders.gross_amount,
        orders.order_currency,
        orders.payment_method,
        
        {# Shipment data #}
        coalesce(
            order_shipment_summary.total_shipments, 
            0
        ) as total_shipments,
        coalesce(
            order_shipment_summary.delivered_shipments, 
            0
        ) as delivered_shipments,
        coalesce(
            order_shipment_summary.exception_shipments, 
            0
        ) as exception_shipments,
        coalesce(
            order_shipment_summary.return_shipments, 
            0
        ) as return_shipments,
        order_shipment_summary.total_shipping_cost,
        order_shipment_summary.total_insurance_cost,
        order_shipment_summary.first_shipment_date,
        order_shipment_summary.last_shipment_date,
        order_shipment_summary.earliest_estimated_delivery,
        order_shipment_summary.latest_estimated_delivery,
        order_shipment_summary.first_delivery_date,
        order_shipment_summary.last_delivery_date,
        order_shipment_summary.avg_delivery_variance_days,
        order_shipment_summary.avg_total_delivery_days,
        order_shipment_summary.on_time_delivery_rate,
        order_shipment_summary.primary_carrier,
        order_shipment_summary.primary_shipping_method,
        order_shipment_summary.primary_delivery_speed

    from orders

    left join order_shipment_summary
        on orders.order_id = order_shipment_summary.order_id

),

enriched_orders as (

    select
        *,
        
        {# Derived fulfillment metrics #}
        case
            when first_shipment_date is not null 
                and order_date is not null
                then date_part(
                    'day',
                    first_shipment_date - order_date
                )
            else null
        end as days_to_first_shipment,

        case
            when last_delivery_date is not null 
                and order_date is not null
                then date_part(
                    'day',
                    last_delivery_date - order_date
                )
            else null
        end as days_to_complete_delivery,

        case
            when total_shipments = 0 then 'not_shipped'
            when delivered_shipments = total_shipments then 'fully_delivered'
            when delivered_shipments > 0 then 'partially_delivered'
            when exception_shipments > 0 then 'delivery_issues'
            else 'in_transit'
        end as fulfillment_status,

        case
            when return_shipments > 0 then true
            else false
        end as has_returns,

        case
            when total_shipping_cost > 0 
                and total_amount > 0
                then total_shipping_cost / total_amount
            else 0
        end as shipping_cost_ratio

    from orders_with_shipments

)

select * from enriched_orders
