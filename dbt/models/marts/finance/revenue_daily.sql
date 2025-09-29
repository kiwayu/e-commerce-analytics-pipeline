{{
    config(
        materialized='table',
        indexes=[
            {'columns': ['date_day'], 'unique': True},
            {'columns': ['order_month']},
            {'columns': ['order_quarter']}
        ],
        tags=['finance', 'revenue', 'daily']
    )
}}

{# 
Daily revenue aggregations for financial reporting and analysis.
Includes revenue by status, returns, and key business metrics.
#}

with

orders as (

    select
        order_date,
        order_status_group,
        total_amount,
        fulfilled_revenue,
        cancelled_revenue,
        returned_revenue,
        has_returns,
        clean_order,
        customer_segment,
        customer_country

    from {{ ref('fact_orders') }}

),

daily_revenue as (

    select
        cast(order_date as date) as date_day,
        extract(year from order_date) as order_year,
        extract(quarter from order_date) as order_quarter,
        extract(month from order_date) as order_month,
        extract(week from order_date) as order_week,
        extract(dow from order_date) as day_of_week,
        
        {# Order counts #}
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
        count(
            case 
                when has_returns = true 
                then 1 
            end
        ) as returned_orders,
        count(
            case 
                when clean_order = true 
                then 1 
            end
        ) as clean_orders,

        {# Revenue metrics #}
        sum(total_amount) as gross_revenue,
        sum(fulfilled_revenue) as net_revenue,
        sum(cancelled_revenue) as cancelled_revenue,
        sum(returned_revenue) as returned_revenue,
        avg(total_amount) as average_order_value,
        
        {# Customer segment revenue #}
        sum(
            case 
                when customer_segment = 'vip' 
                then total_amount 
                else 0 
            end
        ) as vip_revenue,
        sum(
            case 
                when customer_segment = 'champion' 
                then total_amount 
                else 0 
            end
        ) as champion_revenue,
        sum(
            case 
                when customer_segment = 'new_customer' 
                then total_amount 
                else 0 
            end
        ) as new_customer_revenue

    from orders

    group by 1, 2, 3, 4, 5, 6

),

final_revenue_daily as (

    select
        date_day,
        order_year,
        order_quarter,
        order_month,
        order_week,
        day_of_week,
        total_orders,
        fulfilled_orders,
        cancelled_orders,
        returned_orders,
        clean_orders,
        gross_revenue,
        net_revenue,
        cancelled_revenue,
        returned_revenue,
        average_order_value,
        vip_revenue,
        champion_revenue,
        new_customer_revenue,

        {# Calculated metrics #}
        case
            when total_orders > 0 
                then fulfilled_orders::decimal / total_orders::decimal
            else 0
        end as fulfillment_rate,

        case
            when total_orders > 0 
                then cancelled_orders::decimal / total_orders::decimal
            else 0
        end as cancellation_rate,

        case
            when total_orders > 0 
                then returned_orders::decimal / total_orders::decimal
            else 0
        end as return_rate,

        case
            when gross_revenue > 0 
                then net_revenue / gross_revenue
            else 0
        end as revenue_realization_rate,

        {# Moving averages (7-day) #}
        avg(gross_revenue) over (
            order by date_day 
            rows between 6 preceding and current row
        ) as gross_revenue_7d_ma,

        avg(total_orders) over (
            order by date_day 
            rows between 6 preceding and current row
        ) as total_orders_7d_ma,

        {# Year-over-year comparison #}
        lag(gross_revenue, 365) over (
            order by date_day
        ) as gross_revenue_yoy,

        current_timestamp as last_updated_at

    from daily_revenue

)

select * from final_revenue_daily
