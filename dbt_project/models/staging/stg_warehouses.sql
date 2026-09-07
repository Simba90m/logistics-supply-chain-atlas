select
    warehouse_id,
    warehouse_name,
    city,
    country,
    region,
    cast(lat as double) as lat,
    cast(lon as double) as lon,
    cast(capacity_units as integer) as capacity_units
from {{ source('raw', 'raw_warehouses') }}
