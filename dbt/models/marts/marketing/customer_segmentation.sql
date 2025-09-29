{{
    config(
        materialized='table',
        indexes=[
            {'columns': ['customer_segment']},
            {'columns': ['is_marketable']},
            {'columns': ['country']}
        ],
        tags=['marketing', 'segmentation', 'customers']
    )
}}

{# 
Customer segmentation analysis for marketing campaigns and targeting.
Provides detailed customer segments with actionable insights.
#}

with

customers as (

    select
        customer_id,
        email,
        full_name,
        country,
        registration_date,
        total_orders,
        total_order_value,
        average_order_value,
        first_order_date,
        last_order_date,
        days_since_last_order,
        customer_segment,
        customer_frequency_segment,
        customer_value_segment,
        loyalty_segment,
        is_active_buyer,
        is_marketable,
        marketing_consent

    from {{ ref('dim_customers') }}

),

segment_analysis as (

    select
        customer_segment,
        count(*) as customer_count,
        sum(total_order_value) as segment_revenue,
        avg(total_order_value) as avg_customer_value,
        avg(average_order_value) as avg_order_value,
        avg(total_orders) as avg_orders_per_customer,
        avg(days_since_last_order) as avg_days_since_last_order,
        
        {# Marketable customers #}
        count(
            case 
                when is_marketable = true 
                then 1 
            end
        ) as marketable_customers,
        
        {# Active buyers #}
        count(
            case 
                when is_active_buyer = true 
                then 1 
            end
        ) as active_buyers,

        {# Registration timing #}
        avg(
            date_part(
                'day',
                current_date - registration_date
            )
        ) as avg_days_since_registration,

        {# Geographic distribution (top 5 countries) #}
        mode() within group (
            order by country
        ) as primary_country

    from customers

    group by 1

),

customer_segmentation as (

    select
        customers.customer_id,
        customers.email,
        customers.full_name,
        customers.country,
        customers.registration_date,
        customers.customer_segment,
        customers.customer_frequency_segment,
        customers.customer_value_segment,
        customers.loyalty_segment,
        customers.total_orders,
        customers.total_order_value,
        customers.average_order_value,
        customers.days_since_last_order,
        customers.is_active_buyer,
        customers.is_marketable,
        customers.marketing_consent,

        {# Segment context #}
        segment_analysis.customer_count as segment_size,
        segment_analysis.segment_revenue,
        segment_analysis.avg_customer_value as segment_avg_value,
        segment_analysis.marketable_customers as segment_marketable_count,

        {# Relative performance within segment #}
        case
            when customers.total_order_value > segment_analysis.avg_customer_value 
                then 'above_average'
            when customers.total_order_value = segment_analysis.avg_customer_value 
                then 'average'
            else 'below_average'
        end as value_vs_segment,

        {# Marketing recommendations #}
        case
            when customers.customer_segment = 'vip' 
                and customers.is_marketable = true 
                then 'vip_exclusive_offers'
            when customers.customer_segment = 'champion' 
                and customers.is_marketable = true 
                then 'loyalty_rewards'
            when customers.customer_segment = 'loyal_customer' 
                and customers.is_marketable = true 
                then 'retention_campaigns'
            when customers.customer_segment = 'potential_loyalist' 
                and customers.is_marketable = true 
                then 'conversion_campaigns'
            when customers.customer_segment = 'new_customer' 
                and customers.is_marketable = true 
                then 'onboarding_sequence'
            when customers.customer_segment = 'at_risk' 
                and customers.is_marketable = true 
                then 'win_back_campaigns'
            when customers.customer_segment = 'need_attention' 
                and customers.is_marketable = true 
                then 'reactivation_campaigns'
            when customers.customer_segment = 'cannot_lose_them' 
                and customers.is_marketable = true 
                then 'urgent_retention'
            when customers.is_marketable = false 
                then 'not_marketable'
            else 'no_action'
        end as marketing_recommendation,

        {# Communication preferences #}
        case
            when customers.customer_value_segment = 'premium' 
                then 'personalized_high_touch'
            when customers.customer_frequency_segment = 'frequent' 
                then 'regular_engagement'
            when customers.customer_segment = 'new_customer' 
                then 'educational_content'
            else 'standard_communication'
        end as communication_strategy

    from customers

    left join segment_analysis
        on customers.customer_segment = segment_analysis.customer_segment

),

final_customer_segmentation as (

    select
        *,
        
        {# Priority scoring for marketing efforts #}
        case
            when marketing_recommendation = 'urgent_retention' then 10
            when marketing_recommendation = 'vip_exclusive_offers' then 9
            when marketing_recommendation = 'win_back_campaigns' then 8
            when marketing_recommendation = 'loyalty_rewards' then 7
            when marketing_recommendation = 'conversion_campaigns' then 6
            when marketing_recommendation = 'retention_campaigns' then 5
            when marketing_recommendation = 'reactivation_campaigns' then 4
            when marketing_recommendation = 'onboarding_sequence' then 3
            else 1
        end as marketing_priority,

        {# Lifetime value prediction (simplified) #}
        case
            when customer_segment = 'vip' 
                then total_order_value * 2.5
            when customer_segment = 'champion' 
                then total_order_value * 2.0
            when customer_segment = 'loyal_customer' 
                then total_order_value * 1.8
            when customer_segment = 'potential_loyalist' 
                then total_order_value * 1.5
            when customer_segment = 'new_customer' 
                then average_order_value * 3
            else total_order_value * 1.1
        end as predicted_lifetime_value,

        current_timestamp as last_updated_at

    from customer_segmentation

)

select * from final_customer_segmentation
