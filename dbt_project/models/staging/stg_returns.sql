select
    return_id,
    shipment_id,
    cast(return_date as date) as return_date,
    return_reason,
    cast(refund_amount as double) as refund_amount
from {{ source('raw', 'raw_returns') }}
