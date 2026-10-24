-- Every staged order amount must be the raw amount converted to the base
-- currency with the fx_rates row in force on the order date. Returns the offending orders.

select
    raw_orders.order_id,
    raw_orders.currency,
    raw_orders.total_amount as raw_total_amount,
    staged.total_amount as staged_total_amount

from {{ source('raw', 'raw_orders') }} as raw_orders

inner join {{ ref('stg_raw_orders') }} as staged
    on staged.order_id = raw_orders.order_id

inner join lateral (
    select rates.rate_to_base
    from {{ ref('fx_rates') }} as rates
    where rates.currency = upper(trim(raw_orders.currency))
      and rates.valid_from <= cast(raw_orders.order_date as date)
    order by rates.valid_from desc
    limit 1
) as fx on true

where abs(staged.total_amount - round(raw_orders.total_amount * fx.rate_to_base, 2)) > 0.01
