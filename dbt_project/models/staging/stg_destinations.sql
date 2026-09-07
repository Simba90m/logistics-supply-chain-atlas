select
    destination_id,
    city,
    country,
    region,
    cast(lat as double) as lat,
    cast(lon as double) as lon
from {{ source('raw', 'raw_destinations') }}
