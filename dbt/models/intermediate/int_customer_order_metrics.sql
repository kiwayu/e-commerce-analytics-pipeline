{{
    config(
        materialized='view',
        tags=['intermediate', 'customers', 'metrics']
    )
}}

{# 
This model calculates customer-level order metrics and behaviors.
Aggregates order data to create customer insights and segmentation data.
#}

with

orders as (

    select
        customer_id,
        order_id,
        order_date,
        order_status,
        order_status_group,
        order_value_tier,
        total_amount,
        net_amount,
        gross_amount

    from {{ ref('stg_raw_orders') }}

    where customer_id is not null

),

customer_order_summary as (

    select
        customer_id,
        
        {# Order counts by status #}
        count(*) as total_orders,
        count(
            case 
                when order_status_group = 'fulfilled' 
                then 1 
            end
        ) as fulfilled_orders,
        count(
            case 
                when order_status_group = 'cancelled' 
                then 1 
            end
        ) as cancelled_orders,

        {# Order values #}
        sum(total_amount) as total_order_value,
        sum(net_amount) as total_net_value,
        sum(gross_amount) as total_gross_value,
        avg(total_amount) as average_order_value,
        max(total_amount) as highest_order_value,
        min(total_amount) as lowest_order_value,

        {# Order timing #}
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        
        {# Value tier distribution #}
        count(
            case 
                when order_value_tier = 'high_value' 
                then 1 
            end
        ) as high_value_orders,
        count(
            case 
                when order_value_tier = 'medium_value' 
                then 1 
            end
        ) as medium_value_orders,
        count(
            case 
                when order_value_tier = 'low_value' 
                then 1 
            end
        ) as low_value_orders

    from orders

    group by 1

),

customer_behavior_metrics as (

    select
        customer_id,
        total_orders,
        fulfilled_orders,
        cancelled_orders,
        total_order_value,
        total_net_value,
        total_gross_value,
        average_order_value,
        highest_order_value,
        lowest_order_value,
        first_order_date,
        last_order_date,
        high_value_orders,
        medium_value_orders,
        low_value_orders,

        {# Calculated metrics #}
        case
            when total_orders > 0 
                then cancelled_orders::decimal / total_orders::decimal
            else 0
        end as cancellation_rate,

        case
            when total_orders > 0 
                then fulfilled_orders::decimal / total_orders::decimal
            else 0
        end as fulfillment_rate,

        date_part(
            'day',
            current_date - last_order_date
        ) as days_since_last_order,

        date_part(
            'day',
            last_order_date - first_order_date
        ) as customer_lifetime_days,

        case
            when total_orders = 1 then 'one_time'
            when total_orders between 2 and 5 then 'occasional'
            when total_orders between 6 and 20 then 'regular'
            else 'frequent'
        end as customer_frequency_segment,

        case
            when average_order_value >= 500 then 'premium'
            when average_order_value >= 100 then 'standard'
            else 'budget'
        end as customer_value_segment

    from customer_order_summary

),

final_customer_metrics as (

    select
        *,
        
        {# RFM-style segmentation components #}
        case
            when days_since_last_order <= 30 then 'recent'
            when days_since_last_order <= 90 then 'lapsing'
            when days_since_last_order <= 365 then 'dormant'
            else 'lost'
        end as recency_segment,

        case
            when customer_lifetime_days > 0 
                then total_order_value / (customer_lifetime_days / 365.0)
            else total_order_value
        end as annual_order_value,

        case
            when fulfilled_orders >= 10 and cancellation_rate < 0.1 
                then 'loyal'
            when fulfilled_orders >= 5 and cancellation_rate < 0.2 
                then 'engaged'
            when fulfilled_orders >= 2 and cancellation_rate < 0.3 
                then 'developing'
            else 'new_or_risky'
        end as loyalty_segment

    from customer_behavior_metrics

)

select * from final_customer_metrics
