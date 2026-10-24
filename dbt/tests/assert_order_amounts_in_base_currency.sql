-- Every staged order amount must be the raw amount converted to the base
-- currency with the rate in the fx_rates seed. Returns the offending orders.

select
    raw_orders.order_id,
    raw_orders.currency,
    raw_orders.total_amount as raw_total_amount,
    staged.total_amount as staged_total_amount

from {{ source('raw', 'raw_orders') }} as raw_orders

inner join {{ ref('stg_raw_orders') }} as staged
    on staged.order_id = raw_orders.order_id

inner join {{ ref('fx_rates') }} as fx
    on fx.currency = upper(trim(raw_orders.currency))

where abs(staged.total_amount - round(raw_orders.total_amount * fx.rate_to_base, 2)) > 0.01
