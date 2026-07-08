{{
    config(
        materialized='view',
        tags=['staging', 'customers']
    )
}}

{# 
This model standardizes and cleans raw customer data from the source system.
Applies data quality rules and creates consistent customer attributes.
#}

with

customers_source as (

    select
        id,
        customer_id,
        email,
        first_name,
        last_name,
        phone,
        addresses,
        country,
        registration_date,
        last_login as last_login_date,
        marketing_consent,
        source_system,
        source_file,
        ingestion_timestamp,
        batch_id,
        record_hash,
        is_valid,
        validation_errors

    from {{ source('raw', 'raw_customers') }}

    where is_valid = true

),

cleaned_customers as (

    select
        id,
        customer_id,
        lower(trim(email)) as email,
        initcap(trim(first_name)) as first_name,
        initcap(trim(last_name)) as last_name,
        
        {# Clean phone number format #}
        regexp_replace(
            phone,
            '[^0-9]',
            '',
            'g'
        ) as phone_cleaned,
        
        addresses,
        upper(trim(country)) as country,
        cast(registration_date as timestamp) as registration_date,
        cast(last_login_date as timestamp) as last_login_date,
        coalesce(marketing_consent, false) as marketing_consent,
        source_system,
        source_file,
        ingestion_timestamp,
        batch_id,
        record_hash,

        {# Derived fields #}
        concat(
            initcap(trim(first_name)),
            ' ',
            initcap(trim(last_name))
        ) as full_name,

        case
            when email is not null 
                and email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
                then true
            else false
        end as has_valid_email,

        case
            when registration_date >= current_date - interval '30 days'
                then 'new'
            when registration_date >= current_date - interval '365 days'
                then 'active'
            else 'established'
        end as customer_tenure,

        date_part(
            'day',
            current_timestamp - last_login_date
        ) as days_since_last_login

    from customers_source

),

validated_customers as (

    select
        *,
        
        {# Data quality flags #}
        case
            when email is null or not has_valid_email then false
            when first_name is null or last_name is null then false
            when country is null then false
            else true
        end as passes_quality_checks

    from cleaned_customers

)

select * from validated_customers
