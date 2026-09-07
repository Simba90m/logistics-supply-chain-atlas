select
    carrier_id,
    carrier_name,
    mode,
    cast(cost_per_km as double) as cost_per_km,
    cast(speed_kmph as double) as speed_kmph,
    cast(base_on_time_rate as double) as base_on_time_rate
from {{ source('raw', 'raw_carriers') }}
