select
    shipment_id,
    warehouse_id,
    destination_id,
    carrier_id,
    cast(order_date as date) as order_date,
    cast(planned_ship_date as date) as planned_ship_date,
    cast(actual_ship_date as date) as actual_ship_date,
    cast(planned_delivery_date as date) as planned_delivery_date,
    cast(actual_delivery_date as date) as actual_delivery_date,
    cast(distance_km as double) as distance_km,
    cast(weight_kg as double) as weight_kg,
    cast(freight_cost as double) as freight_cost,
    status,
    -- on_time_flag comes in as a nullable python bool via CSV (True/False/empty);
    -- normalize explicitly rather than relying on duckdb's CSV type inference
    case
        when lower(cast(on_time_flag as varchar)) = 'true' then true
        when lower(cast(on_time_flag as varchar)) = 'false' then false
        else null
    end as is_on_time,
    status = 'Delivered' as is_delivered,
    status = 'Cancelled' as is_cancelled,
    status = 'In Transit' as is_in_transit,
    datediff('day', planned_ship_date, planned_delivery_date) as transit_days_planned,
    case
        when actual_ship_date is not null and actual_delivery_date is not null
            then datediff('day', actual_ship_date, actual_delivery_date)
    end as transit_days_actual,
    case
        when actual_delivery_date is not null and planned_delivery_date is not null
            then datediff('day', planned_delivery_date, actual_delivery_date)
    end as delay_days
from {{ source('raw', 'raw_shipments') }}
