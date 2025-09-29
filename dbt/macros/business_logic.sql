{# 
Business logic macros for consistent calculations across models.
These macros ensure standardized business rules and calculations.
#}

{% macro calculate_customer_lifetime_value(
    total_order_value,
    customer_segment,
    multiplier_vip=2.5,
    multiplier_champion=2.0,
    multiplier_loyal=1.8,
    multiplier_potential=1.5,
    multiplier_default=1.1
) %}
    {# 
    Calculate predicted customer lifetime value based on segment and historical value.
    
    Args:
        total_order_value: Historical total order value for customer
        customer_segment: Customer segment classification
        multiplier_*: Segment-specific multipliers for LTV calculation
    
    Returns:
        Predicted lifetime value as decimal
    #}
    
    case
        when {{ customer_segment }} = 'vip' 
            then {{ total_order_value }} * {{ multiplier_vip }}
        when {{ customer_segment }} = 'champion' 
            then {{ total_order_value }} * {{ multiplier_champion }}
        when {{ customer_segment }} = 'loyal_customer' 
            then {{ total_order_value }} * {{ multiplier_loyal }}
        when {{ customer_segment }} = 'potential_loyalist' 
            then {{ total_order_value }} * {{ multiplier_potential }}
        else {{ total_order_value }} * {{ multiplier_default }}
    end

{% endmacro %}

{% macro standardize_currency(currency_column) %}
    {# 
    Standardize currency codes to uppercase 3-letter format.
    
    Args:
        currency_column: Column containing currency codes
    
    Returns:
        Standardized currency code
    #}
    
    upper(trim({{ currency_column }}))

{% endmacro %}

{% macro calculate_order_value_tier(amount_column, high_threshold=1000, medium_threshold=100) %}
    {# 
    Categorize orders into value tiers based on amount.
    
    Args:
        amount_column: Column containing order amounts
        high_threshold: Minimum amount for high value tier
        medium_threshold: Minimum amount for medium value tier
    
    Returns:
        Value tier classification
    #}
    
    case
        when {{ amount_column }} >= {{ high_threshold }} then 'high_value'
        when {{ amount_column }} >= {{ medium_threshold }} then 'medium_value'
        else 'low_value'
    end

{% endmacro %}

{% macro calculate_rfm_score(
    recency_days,
    frequency_count,
    monetary_value,
    recency_thresholds=[30, 90, 365],
    frequency_thresholds=[2, 5, 10],
    monetary_thresholds=[100, 500, 1000]
) %}
    {# 
    Calculate RFM (Recency, Frequency, Monetary) score for customer segmentation.
    
    Args:
        recency_days: Days since last purchase
        frequency_count: Number of purchases
        monetary_value: Total purchase value
        *_thresholds: Lists of threshold values for scoring (low to high)
    
    Returns:
        Concatenated RFM score (e.g., '543')
    #}
    
    concat(
        {# Recency score (lower days = higher score) #}
        case
            when {{ recency_days }} <= {{ recency_thresholds[0] }} then '5'
            when {{ recency_days }} <= {{ recency_thresholds[1] }} then '4'
            when {{ recency_days }} <= {{ recency_thresholds[2] }} then '3'
            when {{ recency_days }} <= {{ recency_thresholds[2] }} * 2 then '2'
            else '1'
        end,
        
        {# Frequency score #}
        case
            when {{ frequency_count }} >= {{ frequency_thresholds[2] }} then '5'
            when {{ frequency_count }} >= {{ frequency_thresholds[1] }} then '4'
            when {{ frequency_count }} >= {{ frequency_thresholds[0] }} then '3'
            when {{ frequency_count }} >= 1 then '2'
            else '1'
        end,
        
        {# Monetary score #}
        case
            when {{ monetary_value }} >= {{ monetary_thresholds[2] }} then '5'
            when {{ monetary_value }} >= {{ monetary_thresholds[1] }} then '4'
            when {{ monetary_value }} >= {{ monetary_thresholds[0] }} then '3'
            when {{ monetary_value }} >= 1 then '2'
            else '1'
        end
    )

{% endmacro %}

{% macro clean_email_address(email_column) %}
    {# 
    Clean and standardize email addresses.
    
    Args:
        email_column: Column containing email addresses
    
    Returns:
        Cleaned email address in lowercase
    #}
    
    lower(trim({{ email_column }}))

{% endmacro %}

{% macro clean_phone_number(phone_column) %}
    {# 
    Clean phone numbers by removing non-numeric characters.
    
    Args:
        phone_column: Column containing phone numbers
    
    Returns:
        Phone number with only digits
    #}
    
    regexp_replace({{ phone_column }}, '[^0-9]', '', 'g')

{% endmacro %}

{% macro calculate_delivery_performance(
    estimated_date,
    actual_date,
    late_threshold_days=1
) %}
    {# 
    Calculate delivery performance based on estimated vs actual delivery.
    
    Args:
        estimated_date: Estimated delivery date
        actual_date: Actual delivery date
        late_threshold_days: Days after estimated considered significantly late
    
    Returns:
        Delivery performance category
    #}
    
    case
        when {{ actual_date }} is null then 'not_delivered'
        when {{ actual_date }} <= {{ estimated_date }} then 'on_time'
        when {{ actual_date }} <= {{ estimated_date }} + interval '{{ late_threshold_days }} days' 
            then 'slightly_late'
        else 'significantly_late'
    end

{% endmacro %}

{% macro generate_surrogate_key(column_list) %}
    {# 
    Generate a surrogate key by hashing multiple columns.
    
    Args:
        column_list: List of column names to include in hash
    
    Returns:
        MD5 hash of concatenated columns
    #}
    
    {{ dbt_utils.generate_surrogate_key(column_list) }}

{% endmacro %}

{% macro safe_divide(numerator, denominator, default_value=0) %}
    {# 
    Safely divide two values, handling division by zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default_value: Value to return when denominator is zero
    
    Returns:
        Division result or default value
    #}
    
    case
        when {{ denominator }} = 0 or {{ denominator }} is null 
            then {{ default_value }}
        else {{ numerator }}::decimal / {{ denominator }}::decimal
    end

{% endmacro %}

{% macro get_date_spine(start_date, end_date) %}
    {# 
    Generate a date spine for time series analysis.
    
    Args:
        start_date: Start date for spine
        end_date: End date for spine
    
    Returns:
        CTE with date spine
    #}
    
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('" ~ start_date ~ "' as date)",
        end_date="cast('" ~ end_date ~ "' as date)"
    ) }}

{% endmacro %}

{% macro pivot_order_statuses() %}
    {# 
    Pivot order statuses into columns for analysis.
    
    Returns:
        Pivot columns for common order statuses
    #}
    
    {{ dbt_utils.pivot(
        'order_status',
        dbt_utils.get_column_values(ref('stg_raw_orders'), 'order_status'),
        agg='count',
        then_value='1'
    ) }}

{% endmacro %}
