select
    warehouse_id,
    cast(month as date) as month,
    category,
    cast(stock_units as integer) as stock_units,
    cast(reorder_point as integer) as reorder_point,
    case
        when lower(cast(stockout_flag as varchar)) = 'true' then true
        else false
    end as is_stockout
from {{ source('raw', 'raw_inventory_snapshots') }}
