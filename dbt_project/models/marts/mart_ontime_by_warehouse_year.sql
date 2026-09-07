with shipments as (
    select * from {{ ref('stg_shipments') }}
),

warehouses as (
    select * from {{ ref('stg_warehouses') }}
)

select
    w.warehouse_id,
    w.warehouse_name,
    w.region,
    date_part('year', s.order_date) as year,
    count(*) as shipment_count,
    round(
        sum(case when s.is_on_time then 1 else 0 end)::double
        / nullif(sum(case when s.is_delivered then 1 else 0 end), 0),
        4
    ) as on_time_rate
from shipments s
inner join warehouses w on s.warehouse_id = w.warehouse_id
where s.is_delivered
group by 1, 2, 3, 4
order by 1, 4
