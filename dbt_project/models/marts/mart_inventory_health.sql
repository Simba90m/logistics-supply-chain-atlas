with inventory as (
    select * from {{ ref('stg_inventory_snapshots') }}
),

warehouses as (
    select * from {{ ref('stg_warehouses') }}
)

select
    i.warehouse_id,
    w.warehouse_name,
    w.region,
    i.month,
    i.category,
    avg(i.stock_units) as avg_stock_units,
    round(
        sum(case when i.is_stockout then 1 else 0 end)::double / count(*),
        4
    ) as stockout_rate
from inventory i
inner join warehouses w on i.warehouse_id = w.warehouse_id
group by 1, 2, 3, 4, 5
order by 1, 4
