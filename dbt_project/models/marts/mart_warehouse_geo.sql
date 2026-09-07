with shipments as (
    select * from {{ ref('stg_shipments') }}
),

warehouses as (
    select * from {{ ref('stg_warehouses') }}
)

select
    w.warehouse_id,
    w.warehouse_name,
    w.city,
    w.country,
    w.region,
    w.lat,
    w.lon,
    w.capacity_units,
    count(*) as shipment_count,
    sum(s.weight_kg) as total_weight_kg,
    round(avg(s.freight_cost), 2) as avg_freight_cost,
    round(avg(s.distance_km), 1) as avg_distance_km,
    round(
        sum(case when s.is_on_time then 1 else 0 end)::double
        / nullif(sum(case when s.is_delivered then 1 else 0 end), 0),
        4
    ) as on_time_rate
from warehouses w
left join shipments s on s.warehouse_id = w.warehouse_id
group by 1, 2, 3, 4, 5, 6, 7, 8
order by 9 desc
