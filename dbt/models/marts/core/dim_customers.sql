{{
    config(
        materialized='table',
        indexes=[
            {'columns': ['customer_id'], 'unique': True},
            {'columns': ['email']},
            {'columns': ['customer_segment']},
            {'columns': ['is_active_buyer']}
        ],
        tags=['core', 'dimension', 'customers']
    )
}}

{# 
Core customer dimension table combining customer attributes with 
calculated metrics and segmentation for analytics and reporting.
#}

with

customers as (

    select
        customer_id,
        email,
        first_name,
        last_name,
        full_name,
        phone_cleaned,
        country,
        registration_date,
        last_login_date,
        marketing_consent,
        has_valid_email,
        customer_tenure,
        days_since_last_login,
        passes_quality_checks

    from {{ ref('stg_raw_customers') }}

    where passes_quality_checks = true

),

customer_metrics as (

    select
        customer_id,
        total_orders,
        fulfilled_orders,
        cancelled_orders,
        total_order_value,
        average_order_value,
        first_order_date,
        last_order_date,
        cancellation_rate,
        fulfillment_rate,
        days_since_last_order,
        customer_lifetime_days,
        customer_frequency_segment,
        customer_value_segment,
        recency_segment,
        annual_order_value,
        loyalty_segment

    from {{ ref('int_customer_order_metrics') }}

),

customer_dimension as (

    select
        customers.customer_id,
        customers.email,
        customers.first_name,
        customers.last_name,
        customers.full_name,
        customers.phone_cleaned as phone,
        customers.country,
        customers.registration_date,
        customers.last_login_date,
        customers.marketing_consent,
        customers.has_valid_email,
        customers.customer_tenure,
        customers.days_since_last_login,
        
        {# Order metrics (with defaults for new customers) #}
        coalesce(customer_metrics.total_orders, 0) as total_orders,
        coalesce(customer_metrics.fulfilled_orders, 0) as fulfilled_orders,
        coalesce(customer_metrics.cancelled_orders, 0) as cancelled_orders,
        coalesce(customer_metrics.total_order_value, 0.00) as total_order_value,
        coalesce(customer_metrics.average_order_value, 0.00) as average_order_value,
        customer_metrics.first_order_date,
        customer_metrics.last_order_date,
        coalesce(customer_metrics.cancellation_rate, 0.00) as cancellation_rate,
        coalesce(customer_metrics.fulfillment_rate, 0.00) as fulfillment_rate,
        customer_metrics.days_since_last_order,
        customer_metrics.customer_lifetime_days,
        coalesce(customer_metrics.annual_order_value, 0.00) as annual_order_value,

        {# Segmentation (with defaults for new customers) #}
        coalesce(
            customer_metrics.customer_frequency_segment, 
            'new'
        ) as customer_frequency_segment,
        coalesce(
            customer_metrics.customer_value_segment, 
            'new'
        ) as customer_value_segment,
        coalesce(
            customer_metrics.recency_segment, 
            'new'
        ) as recency_segment,
        coalesce(
            customer_metrics.loyalty_segment, 
            'new_or_risky'
        ) as loyalty_segment

    from customers

    left join customer_metrics
        on customers.customer_id = customer_metrics.customer_id

),

final_customer_dimension as (

    select
        *,
        
        {# Composite customer segment #}
        case
            when total_orders = 0 then 'prospect'
            when loyalty_segment = 'loyal' 
                and customer_value_segment = 'premium' 
                then 'vip'
            when loyalty_segment = 'loyal' 
                and customer_value_segment in ('standard', 'premium') 
                then 'champion'
            when recency_segment = 'recent' 
                and customer_frequency_segment in ('regular', 'frequent') 
                then 'loyal_customer'
            when recency_segment = 'recent' 
                and total_orders >= 2 
                then 'potential_loyalist'
            when recency_segment = 'recent' 
                and total_orders = 1 
                then 'new_customer'
            when recency_segment in ('lapsing', 'dormant') 
                and customer_value_segment = 'premium' 
                then 'at_risk'
            when recency_segment in ('lapsing', 'dormant') 
                then 'need_attention'
            when recency_segment = 'lost' 
                then 'cannot_lose_them'
            else 'other'
        end as customer_segment,

        {# Activity flags #}
        case
            when days_since_last_login <= 30 then true
            else false
        end as is_active_user,

        case
            when days_since_last_order <= 90 then true
            else false
        end as is_active_buyer,

        case
            when total_orders > 0 then true
            else false
        end as has_purchased,

        case
            when marketing_consent = true 
                and has_valid_email = true 
                then true
            else false
        end as is_marketable,

        {# Calculated fields #}
        current_timestamp as last_updated_at

    from customer_dimension

)

select * from final_customer_dimension
