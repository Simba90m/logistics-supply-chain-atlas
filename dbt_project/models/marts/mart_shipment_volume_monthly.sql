with shipments as (
    select * from {{ ref('stg_shipments') }}
),

warehouses as (
    select * from {{ ref('stg_warehouses') }}
)

select
    date_trunc('month', s.order_date) as month_start,
    w.warehouse_id,
    w.warehouse_name,
    w.region,
    count(*) as shipment_count,
    sum(s.weight_kg) as total_weight_kg,
    sum(s.freight_cost) as total_freight_cost,
    sum(case when s.is_delivered then 1 else 0 end) as delivered_count,
    sum(case when s.is_on_time then 1 else 0 end) as on_time_count,
    round(
        sum(case when s.is_on_time then 1 else 0 end)::double
        / nullif(sum(case when s.is_delivered then 1 else 0 end), 0),
        4
    ) as on_time_rate
from shipments s
inner join warehouses w on s.warehouse_id = w.warehouse_id
group by 1, 2, 3, 4
order by 1, 2
