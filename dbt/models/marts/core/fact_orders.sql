{{
    config(
        materialized='table',
        indexes=[
            {'columns': ['order_id'], 'unique': True},
            {'columns': ['customer_id']},
            {'columns': ['order_date']},
            {'columns': ['order_status_group']},
            {'columns': ['order_value_tier']}
        ],
        tags=['core', 'fact', 'orders']
    )
}}

{# 
Core orders fact table combining order, customer, and shipment data
for comprehensive order analytics and reporting.
#}

with

orders_with_shipments as (

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
        order_currency,
        payment_method,
        total_shipments,
        delivered_shipments,
        exception_shipments,
        return_shipments,
        total_shipping_cost,
        total_insurance_cost,
        first_shipment_date,
        last_shipment_date,
        first_delivery_date,
        last_delivery_date,
        avg_delivery_variance_days,
        avg_total_delivery_days,
        on_time_delivery_rate,
        primary_carrier,
        primary_shipping_method,
        primary_delivery_speed,
        days_to_first_shipment,
        days_to_complete_delivery,
        fulfillment_status,
        has_returns,
        shipping_cost_ratio

    from {{ ref('int_order_shipment_combined') }}

),

customers as (

    select
        customer_id,
        customer_segment,
        customer_frequency_segment,
        customer_value_segment,
        loyalty_segment,
        is_active_buyer,
        country

    from {{ ref('dim_customers') }}

),

fact_orders as (

    select
        orders_with_shipments.order_id,
        orders_with_shipments.customer_id,
        orders_with_shipments.order_date,
        extract(year from orders_with_shipments.order_date) as order_year,
        extract(quarter from orders_with_shipments.order_date) as order_quarter,
        extract(month from orders_with_shipments.order_date) as order_month,
        extract(week from orders_with_shipments.order_date) as order_week,
        extract(dow from orders_with_shipments.order_date) as order_day_of_week,
        
        {# Order attributes #}
        orders_with_shipments.order_status,
        orders_with_shipments.order_status_group,
        orders_with_shipments.order_value_tier,
        orders_with_shipments.payment_method,
        orders_with_shipments.order_currency,
        
        {# Customer attributes #}
        customers.customer_segment,
        customers.customer_frequency_segment,
        customers.customer_value_segment,
        customers.loyalty_segment,
        customers.is_active_buyer,
        customers.country as customer_country,
        
        {# Financial metrics #}
        orders_with_shipments.total_amount,
        orders_with_shipments.net_amount,
        orders_with_shipments.gross_amount,
        orders_with_shipments.total_shipping_cost,
        orders_with_shipments.total_insurance_cost,
        orders_with_shipments.shipping_cost_ratio,
        
        {# Fulfillment metrics #}
        orders_with_shipments.total_shipments,
        orders_with_shipments.delivered_shipments,
        orders_with_shipments.exception_shipments,
        orders_with_shipments.return_shipments,
        orders_with_shipments.fulfillment_status,
        orders_with_shipments.has_returns,
        orders_with_shipments.primary_carrier,
        orders_with_shipments.primary_shipping_method,
        orders_with_shipments.primary_delivery_speed,
        
        {# Timing metrics #}
        orders_with_shipments.first_shipment_date,
        orders_with_shipments.last_shipment_date,
        orders_with_shipments.first_delivery_date,
        orders_with_shipments.last_delivery_date,
        orders_with_shipments.days_to_first_shipment,
        orders_with_shipments.days_to_complete_delivery,
        orders_with_shipments.avg_delivery_variance_days,
        orders_with_shipments.avg_total_delivery_days,
        orders_with_shipments.on_time_delivery_rate,

        {# Derived business metrics #}
        case
            when orders_with_shipments.order_status_group = 'fulfilled' 
                then orders_with_shipments.total_amount
            else 0
        end as fulfilled_revenue,

        case
            when orders_with_shipments.order_status_group = 'cancelled' 
                then orders_with_shipments.total_amount
            else 0
        end as cancelled_revenue,

        case
            when orders_with_shipments.has_returns = true 
                then orders_with_shipments.total_amount
            else 0
        end as returned_revenue,

        case
            when orders_with_shipments.on_time_delivery_rate >= 1.0 
                then true
            else false
        end as delivered_on_time,

        case
            when orders_with_shipments.days_to_first_shipment <= 1 
                then 'same_day'
            when orders_with_shipments.days_to_first_shipment <= 3 
                then 'fast'
            when orders_with_shipments.days_to_first_shipment <= 7 
                then 'standard'
            else 'slow'
        end as fulfillment_speed,

        {# Profitability estimates (simplified) #}
        orders_with_shipments.net_amount - 
        coalesce(orders_with_shipments.total_shipping_cost, 0) - 
        coalesce(orders_with_shipments.total_insurance_cost, 0) as estimated_profit,

        {# Quality flags #}
        case
            when orders_with_shipments.exception_shipments = 0 
                and orders_with_shipments.return_shipments = 0 
                then true
            else false
        end as clean_order,

        current_timestamp as last_updated_at

    from orders_with_shipments

    left join customers
        on orders_with_shipments.customer_id = customers.customer_id

),

final_fact_orders as (

    select
        *,
        
        {# Order sequence numbers for customer analysis #}
        row_number() over (
            partition by customer_id 
            order by order_date asc
        ) as customer_order_sequence,

        {# Days since previous order #}
        coalesce(
            date_part(
                'day',
                order_date - lag(order_date) over (
                    partition by customer_id 
                    order by order_date asc
                )
            ),
            0
        ) as days_since_previous_order,

        {# Cumulative customer metrics #}
        sum(total_amount) over (
            partition by customer_id 
            order by order_date asc 
            rows unbounded preceding
        ) as cumulative_customer_value,

        count(*) over (
            partition by customer_id 
            order by order_date asc 
            rows unbounded preceding
        ) as cumulative_order_count

    from fact_orders

)

select * from final_fact_orders
