with shipments as (
    select * from {{ ref('stg_shipments') }}
),

carriers as (
    select * from {{ ref('stg_carriers') }}
)

select
    c.carrier_id,
    c.carrier_name,
    c.mode,
    date_part('year', s.order_date) as year,
    count(*) as shipment_count,
    round(avg(s.transit_days_planned), 2) as avg_transit_days_planned,
    round(avg(s.transit_days_actual), 2) as avg_transit_days_actual,
    round(avg(s.freight_cost / nullif(s.distance_km, 0)), 4) as avg_cost_per_km,
    round(
        sum(case when s.is_on_time then 1 else 0 end)::double
        / nullif(sum(case when s.is_delivered then 1 else 0 end), 0),
        4
    ) as on_time_rate
from shipments s
inner join carriers c on s.carrier_id = c.carrier_id
where s.is_delivered
group by 1, 2, 3, 4
order by 1, 4
